"""Streaming: recebe a resposta pedaço por pedaço, conforme o modelo gera.

Primeiro com urllib (para ver as linhas cruas), depois com a biblioteca `ollama`.
"""

import json
import urllib.request

import ollama

PERGUNTA = "Conte uma história de 3 frases sobre um robô que aprende a cozinhar."

print("── 1) Cru: cada linha é um JSON com um pedacinho ──\n")
requisicao = urllib.request.Request(
    "http://localhost:11434/api/chat",
    data=json.dumps({
        "model": "llama3.2:3b",
        "messages": [{"role": "user", "content": "Diga 'olá mundo'"}],
        "stream": True,
    }).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(requisicao) as resposta:
    for linha in resposta:
        print(linha.decode().strip())

print("\n── 2) Com a biblioteca ollama, imprimindo só o texto ──\n")
for pedaco in ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": PERGUNTA}],
    stream=True,
):
    # flush=True força o texto a aparecer na hora, sem esperar a linha acabar
    print(pedaco.message.content, end="", flush=True)
print()
