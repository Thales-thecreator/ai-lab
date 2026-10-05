"""Buscador semântico: encontra frases pelo significado, não pelas palavras."""

import numpy as np
import ollama

MODELO = "embeddinggemma"

DOCUMENTOS = [
    "O gato subiu no telhado e não quer descer.",
    "Meu cachorro late toda vez que a campainha toca.",
    "Peixes de aquário precisam de água filtrada.",
    "A taxa Selic subiu meio ponto percentual.",
    "Investir em renda fixa é mais seguro que em ações.",
    "O dólar fechou em alta frente ao real.",
    "Para fazer arroz, refogue alho antes de colocar a água.",
    "O bolo de cenoura leva cobertura de chocolate.",
    "Feijoada é tradicionalmente servida aos sábados.",
    "O Brasil é pentacampeão mundial de futebol.",
    "A maratona tem 42 quilômetros e 195 metros.",
    "Natação é um exercício de baixo impacto para as articulações.",
    "Python é uma linguagem de programação popular em ciência de dados.",
    "Um compilador traduz código-fonte para linguagem de máquina.",
    "Senhas fortes misturam letras, números e símbolos.",
    "Chove muito na Amazônia durante o inverno.",
    "O deserto do Atacama é um dos lugares mais secos do mundo.",
    "A Lua influencia as marés dos oceanos.",
    "Dormir pouco prejudica a memória e a concentração.",
    "Beber água ao longo do dia ajuda a manter a disposição.",
]

# O embeddinggemma foi treinado com esses prefixos: um para documentos, outro para perguntas.
print(f"Indexando {len(DOCUMENTOS)} documentos...")
indice = np.array(ollama.embed(
    model=MODELO, input=[f"title: none | text: {d}" for d in DOCUMENTOS]
).embeddings)
# Normalizar (tamanho 1) deixa o cosseno igual a um simples produto escalar
indice /= np.linalg.norm(indice, axis=1, keepdims=True)


def buscar(consulta, k=3):
    v = np.array(ollama.embed(model=MODELO, input=f"task: search result | query: {consulta}").embeddings[0])
    v /= np.linalg.norm(v)
    notas = indice @ v  # similaridade com todos os documentos de uma vez
    melhores = np.argsort(-notas)[:k]
    return [(notas[i], DOCUMENTOS[i]) for i in melhores]


print("Pronto! Digite uma busca (ou /sair).\n")
while True:
    try:
        consulta = input("🔎 ").strip()
    except (KeyboardInterrupt, EOFError):
        break
    if consulta in ("", "/sair"):
        break
    for nota, doc in buscar(consulta):
        print(f"   {nota:.3f}  {doc}")
    print()
