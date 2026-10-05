"""Uma chamada à API do Ollama usando só a biblioteca padrão do Python.

É exatamente o mesmo que o `curl` do README, para você ver que não há mágica.
"""

import json
import urllib.request

URL = "http://localhost:11434/api/chat"

corpo = {
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Explique o que é uma API em uma frase."}],
    "stream": False,
}

# Monta a requisição HTTP: endereço + corpo em JSON + método POST
requisicao = urllib.request.Request(
    URL,
    data=json.dumps(corpo).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(requisicao) as resposta:
    dados = json.loads(resposta.read())

print("Resposta completa (JSON):")
print(json.dumps(dados, indent=2, ensure_ascii=False))
print()
print("Só o texto:", dados["message"]["content"])
