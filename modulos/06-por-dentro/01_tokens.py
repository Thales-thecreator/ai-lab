"""Como o modelo "vê" o texto: tokens.

Pré-requisito: llama-server rodando (veja o README do módulo).
Uso:  uv run modulos/06-por-dentro/01_tokens.py ["seu texto"]
"""

import json
import os
import sys
import urllib.request

URL = os.environ.get("LLAMA_URL", "http://localhost:8080")


def tokenizar(texto: str) -> list[dict]:
    req = urllib.request.Request(
        f"{URL}/tokenize",
        data=json.dumps({"content": texto, "with_pieces": True}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["tokens"]


def mostrar(texto: str):
    tokens = tokenizar(texto)
    # cada token entre colchetes; espaço visível como ·
    pedacos = "".join(f"[{t['piece'].replace(' ', '·')}]" for t in tokens)
    print(f"{len(tokens):>3} tokens · {len(texto):>3} caracteres │ {pedacos}")


exemplos = sys.argv[1:] or [
    "Hello, how are you today?",
    "Olá, como você está hoje?",
    "inconstitucionalissimamente",
    "antidisestablishmentarianism",
    "1234567890",
    "def soma(a, b): return a + b",
    "🤖🧪🔥",
    "     espaços     ",
]

for e in exemplos:
    mostrar(e)

print("\nIDs (o que o modelo realmente recebe):")
print([t["id"] for t in tokenizar(exemplos[0])])
