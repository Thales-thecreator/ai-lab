"""Agente simples: a LLM decide quando chamar ferramentas (funções Python).

Uso:  uv run modulos/05-tools/agente.py [modelo]
"""

import ast
import datetime
import operator
import pathlib
import sys

import ollama

MODELO = sys.argv[1] if len(sys.argv) > 1 else "qwen3:8b"
MAX_PASSOS = 5  # trava de segurança contra loops
LAB = pathlib.Path(__file__).resolve().parents[2]  # ~/ai-lab


# ── Ferramentas: funções Python normais ─────────────────────────────────────
# O Ollama gera a "ficha técnica" que o modelo vê a partir da docstring e dos tipos.

def calcular(expressao: str) -> str:
    """Calcula uma expressão aritmética, como '1234 * 5678' ou '(2 + 3) / 4'.

    Args:
        expressao: a expressão matemática com números e + - * / ** ( )
    """
    # Avaliador seguro: só aceita números e operadores (nada de eval()!)
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}

    def avaliar(no):
        if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
            return no.value
        if isinstance(no, ast.BinOp):
            return ops[type(no.op)](avaliar(no.left), avaliar(no.right))
        if isinstance(no, ast.UnaryOp):
            return ops[type(no.op)](avaliar(no.operand))
        raise ValueError("expressão não permitida")

    try:
        return str(avaliar(ast.parse(expressao, mode="eval").body))
    except Exception as e:
        return f"erro: {e}"


def data_hora_atual() -> str:
    """Retorna a data e a hora atuais."""
    return datetime.datetime.now().strftime("%A, %d/%m/%Y %H:%M")


def listar_arquivos(subpasta: str = ".") -> str:
    """Lista os arquivos e pastas dentro do lab.

    Args:
        subpasta: caminho relativo à pasta do lab, por exemplo '.' ou 'modulos'
    """
    alvo = (LAB / subpasta).resolve()
    if not alvo.is_relative_to(LAB) or not alvo.is_dir():
        return "erro: pasta inválida (só é permitido dentro do lab)"
    return "\n".join(sorted(p.name + ("/" if p.is_dir() else "")
                            for p in alvo.iterdir() if not p.name.startswith(".")))


def ler_arquivo(caminho: str) -> str:
    """Lê um arquivo de texto dentro do lab.

    Args:
        caminho: caminho relativo à pasta do lab, por exemplo 'README.md'
    """
    alvo = (LAB / caminho).resolve()
    if not alvo.is_relative_to(LAB) or not alvo.is_file():
        return "erro: arquivo não encontrado (só é permitido dentro do lab)"
    return alvo.read_text(encoding="utf-8", errors="ignore")[:4000]


FERRAMENTAS = {f.__name__: f for f in [calcular, data_hora_atual, listar_arquivos, ler_arquivo]}


# ── O loop do agente ───────────────────────────────────────────────────────
def executar(pergunta: str):
    mensagens = [
        {"role": "system", "content": "Você é um assistente em português. Use as ferramentas "
                                      "quando precisar de contas exatas, data/hora ou arquivos."},
        {"role": "user", "content": pergunta},
    ]
    for passo in range(1, MAX_PASSOS + 1):
        r = ollama.chat(model=MODELO, messages=mensagens,
                        tools=list(FERRAMENTAS.values()), think=False)
        mensagens.append(r.message)

        if not r.message.tool_calls:  # o modelo não quer mais ferramentas → resposta final
            print(f"💬 {r.message.content}\n")
            return

        for chamada in r.message.tool_calls:
            nome, args = chamada.function.name, chamada.function.arguments
            print(f"  🔧 passo {passo}: {nome}({args})")
            funcao = FERRAMENTAS.get(nome)
            try:
                resultado = funcao(**args) if funcao else f"erro: ferramenta '{nome}' não existe"
            except TypeError as e:  # o modelo inventou/errou argumentos
                resultado = f"erro nos argumentos: {e}"
            print(f"     ↳ {resultado[:200]!r}")
            mensagens.append({"role": "tool", "tool_name": nome, "content": resultado})

    print("⚠️  limite de passos atingido — o modelo entrou em loop?\n")


print(f"🤖 Agente com {MODELO}. Ferramentas: {', '.join(FERRAMENTAS)}. /sair para terminar.\n")
while True:
    try:
        pergunta = input("você › ").strip()
    except (KeyboardInterrupt, EOFError):
        break
    if pergunta in ("", "/sair"):
        break
    executar(pergunta)
