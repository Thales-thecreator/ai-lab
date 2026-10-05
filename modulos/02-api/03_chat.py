"""Chat no terminal, com histórico e streaming.

Uso:  uv run modulos/02-api/03_chat.py [modelo]
Sair: digite /sair (ou Ctrl+C)
"""

import sys

import ollama

MODELO = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:3b"
SYSTEM = "Você é um assistente prestativo. Responda sempre em português do Brasil, de forma curta."

# O "segredo" do chat: a lista inteira é reenviada a cada pergunta.
historico = [{"role": "system", "content": SYSTEM}]

print(f"💬 Chat com {MODELO}. Digite /sair para terminar.\n")

while True:
    try:
        pergunta = input("você › ").strip()
    except (KeyboardInterrupt, EOFError):
        break
    if not pergunta:
        continue
    if pergunta == "/sair":
        break

    historico.append({"role": "user", "content": pergunta})

    print("bot › ", end="", flush=True)
    resposta = ""
    for pedaco in ollama.chat(model=MODELO, messages=historico, stream=True, think=False):
        print(pedaco.message.content, end="", flush=True)
        resposta += pedaco.message.content
        if pedaco.done:
            info = pedaco
    print()
    print(f"      [{info.prompt_eval_count} tokens lidos · {info.eval_count} escritos]\n")

    historico.append({"role": "assistant", "content": resposta})

print("tchau 👋")
