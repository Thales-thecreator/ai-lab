r"""RAG: "pergunte aos seus arquivos".

1. lê os arquivos de uma pasta (.txt, .md, .pdf, .docx)
2. corta em pedaços (chunks) e gera um embedding para cada um
3. para cada pergunta: acha os pedaços mais parecidos e manda junto para a LLM

Uso:
  uv run modulos/04-rag/rag.py                          # docs públicos
  uv run modulos/04-rag/rag.py "~/Documents/Minha Pasta"            # seus docs (macOS/Linux)
  uv run modulos/04-rag/rag.py "$HOME\Documents\Minha Pasta"        # seus docs (Windows)
"""

import hashlib
import pathlib
import sys

import numpy as np
import ollama

MODELO_EMBED = "embeddinggemma"
MODELO_CHAT = "qwen3:8b"     # troque por llama3.2:3b se quiser mais rapidez
TAMANHO_CHUNK = 1000         # caracteres por pedaço
SOBREPOSICAO = 200           # pedaços se sobrepõem para não cortar ideias no meio
TOP_K = 4                    # quantos pedaços mandar para a LLM

PASTA = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                     pathlib.Path(__file__).parent / "dados" / "publicos").expanduser()


def ler_arquivo(caminho: pathlib.Path) -> str:
    sufixo = caminho.suffix.lower()
    if sufixo in (".txt", ".md"):
        return caminho.read_text(encoding="utf-8", errors="ignore")
    if sufixo == ".pdf":
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(caminho).pages)
    if sufixo == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(caminho).paragraphs)
    return ""


def cortar(texto: str) -> list[str]:
    texto = " ".join(texto.split())  # normaliza espaços e quebras de linha
    passo = TAMANHO_CHUNK - SOBREPOSICAO
    return [texto[i:i + TAMANHO_CHUNK] for i in range(0, max(len(texto) - SOBREPOSICAO, 1), passo)]


# ── Indexação ──────────────────────────────────────────────────────────────
chunks: list[tuple[str, str]] = []  # (nome do arquivo, texto)
for arq in sorted(PASTA.rglob("*")):
    if arq.is_file():
        texto = ler_arquivo(arq)
        if texto.strip():
            chunks += [(arq.name, c) for c in cortar(texto)]

if not chunks:
    sys.exit(f"Nenhum texto encontrado em {PASTA}. Rode baixar_publicos.py primeiro?")

# Cache: só recalcula os embeddings se os pedaços mudarem
assinatura = hashlib.sha1("".join(c for _, c in chunks).encode()).hexdigest()[:12]
cache = pathlib.Path(__file__).parent / ".cache" / f"{MODELO_EMBED}-{assinatura}.npy"
if cache.exists():
    vetores = np.load(cache)
else:
    print(f"Gerando embeddings de {len(chunks)} pedaços (só na primeira vez)...")
    vetores = []
    for i in range(0, len(chunks), 32):  # em lotes de 32
        lote = [f"title: {arq} | text: {c}" for arq, c in chunks[i:i + 32]]
        vetores += ollama.embed(model=MODELO_EMBED, input=lote).embeddings
        print(f"  {min(i + 32, len(chunks))}/{len(chunks)}", end="\r")
    vetores = np.array(vetores)
    vetores /= np.linalg.norm(vetores, axis=1, keepdims=True)
    cache.parent.mkdir(exist_ok=True)
    np.save(cache, vetores)

print(f"📚 {len(chunks)} pedaços de {len({a for a, _ in chunks})} arquivos em {PASTA}\n")


# ── Busca + geração ────────────────────────────────────────────────────────
def recuperar(pergunta: str):
    v = np.array(ollama.embed(model=MODELO_EMBED, input=f"task: search result | query: {pergunta}").embeddings[0])
    notas = vetores @ (v / np.linalg.norm(v))
    return [(notas[i], *chunks[i]) for i in np.argsort(-notas)[:TOP_K]]


def responder(pergunta: str):
    trechos = recuperar(pergunta)
    contexto = "\n\n".join(f"[{i + 1}] (de {arq})\n{txt}" for i, (_, arq, txt) in enumerate(trechos))
    prompt = (
        "Responda à pergunta usando APENAS os trechos abaixo. "
        "Cite os trechos usados como [1], [2]... "
        "Se a resposta não estiver nos trechos, diga que não sabe.\n\n"
        f"TRECHOS:\n{contexto}\n\nPERGUNTA: {pergunta}"
    )
    print("📎 trechos recuperados:")
    for i, (nota, arq, txt) in enumerate(trechos):
        print(f"   [{i + 1}] {nota:.3f} {arq}: {txt[:70]}...")
    print("\n💬 ", end="")
    for p in ollama.chat(model=MODELO_CHAT, messages=[{"role": "user", "content": prompt}],
                         stream=True, think=False):
        print(p.message.content, end="", flush=True)
    print("\n")


while True:
    try:
        pergunta = input("❓ ").strip()
    except (KeyboardInterrupt, EOFError):
        break
    if pergunta in ("", "/sair"):
        break
    responder(pergunta)
