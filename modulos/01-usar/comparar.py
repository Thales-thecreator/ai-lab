"""Roda as mesmas perguntas em vários modelos e mede a velocidade de cada um.

Uso:  uv run modulos/01-usar/comparar.py
"""

import ollama

MODELOS = ["qwen3:1.7b", "llama3.2:3b", "qwen3:8b"]

PERGUNTAS = [
    "Em uma frase: o que é fotossíntese?",
    "Qual é a capital da Austrália? Responda só o nome.",
    "Escreva um haicai em português sobre café.",
    "Se eu tenho 3 maçãs, como 1 e compro mais 5, quantas tenho? Explique em uma linha.",
    "Quem ganhou a Copa do Mundo de 1994?",
]

NS = 1e9  # o Ollama mede tempo em nanossegundos

for modelo in MODELOS:
    print("=" * 70)
    print(f"🤖 {modelo}")
    print("=" * 70)
    velocidades = []

    for pergunta in PERGUNTAS:
        r = ollama.chat(
            model=modelo,
            messages=[{"role": "user", "content": pergunta}],
            think=False,  # desliga o "thinking" do Qwen3 para comparar de forma justa
        )
        tokens = r.eval_count
        segundos = r.eval_duration / NS
        velocidade = tokens / segundos
        velocidades.append(velocidade)

        print(f"\n❓ {pergunta}")
        print(f"💬 {r.message.content.strip()}")
        print(f"   ⏱  {tokens} tokens em {segundos:.1f}s = {velocidade:.1f} tok/s"
              f"  (carregar modelo: {r.load_duration / NS:.1f}s)")

    media = sum(velocidades) / len(velocidades)
    print(f"\n📊 {modelo}: média de {media:.1f} tokens/s\n")
