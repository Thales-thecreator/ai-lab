"""O que uma LLM realmente faz: prevê a probabilidade do PRÓXIMO token.

E como temperature muda o sorteio entre os candidatos.

Pré-requisito: llama-server rodando (veja o README do módulo).
Uso:  uv run modulos/06-por-dentro/02_proximo_token.py ["seu começo de frase"]
"""

import json
import math
import os
import sys
import urllib.request

URL = os.environ.get("LLAMA_URL", "http://localhost:8080")
if os.name == "nt":
    os.system("")  # liga as cores/negrito (códigos ANSI) no console do Windows
PROMPT = sys.argv[1] if len(sys.argv) > 1 else "Era uma vez um"


def completar(**corpo) -> dict:
    req = urllib.request.Request(
        f"{URL}/completion",
        data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


# ── 1) A distribuição de probabilidade do próximo token ──────────────────
r = completar(prompt=PROMPT, n_predict=1, n_probs=10, temperature=0)
candidatos = r["completion_probabilities"][0]["top_logprobs"]

print(f'Prompt: "{PROMPT}"\n')
print("Top 10 candidatos para o próximo token:\n")
for c in candidatos:
    p = math.exp(c["logprob"])  # logprob → probabilidade
    barra = "█" * round(p * 50)
    print(f"  {c['token']!r:>14}  {p:6.1%}  {barra}")

# ── 2) Gerando token a token, "na mão" (greedy: sempre o mais provável) ────
print("\nGerando 12 tokens, sempre escolhendo o mais provável:\n")
texto = PROMPT
for _ in range(12):
    r = completar(prompt=texto, n_predict=1, n_probs=3, temperature=0)
    top = r["completion_probabilities"][0]["top_logprobs"]
    escolhido = top[0]["token"]
    alternativas = ", ".join(f"{t['token']!r} {math.exp(t['logprob']):.0%}" for t in top)
    print(f"  + {escolhido!r:<14} (candidatos: {alternativas})")
    texto += escolhido
print(f"\nResultado: {texto}")

# ── 3) Temperature: mesmo prompt, 4 sorteios por temperatura ───────────────
print("\nEfeito da temperature (4 sorteios cada):")
for temp in [0.0, 0.7, 1.5]:
    print(f"\n  temperature = {temp}")
    for _ in range(4):
        r = completar(prompt=PROMPT, n_predict=15, temperature=temp, seed=-1)
        continuacao = r["content"].replace("\n", " ")
        print(f"    → {PROMPT}\033[1m{continuacao}\033[0m")  # \033[1m = negrito no terminal
