"""O que é um embedding: texto → vetor de números. E como comparar vetores."""

import numpy as np
import ollama

MODELO = "embeddinggemma"

frases = [
    "o gato dormiu no sofá",
    "o felino cochilou na poltrona",
    "meu cachorro adora passear",
    "a bolsa de valores caiu hoje",
    "o mercado financeiro teve queda",
]

# Uma chamada só, com todas as frases
vetores = np.array(ollama.embed(model=MODELO, input=frases).embeddings)

print(f"Cada frase virou um vetor de {vetores.shape[1]} números.")
print(f"Primeiros 8 números de '{frases[0]}':\n  {vetores[0][:8].round(3)}\n")


def cosseno(a, b):
    """1 = mesma direção (mesmo sentido), 0 = sem relação."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


print("Similaridade entre todas as frases:\n")
print(" " * 32 + "  ".join(f"F{i}  " for i in range(len(frases))))
for i, a in enumerate(vetores):
    linha = "  ".join(f"{cosseno(a, b):.2f}" for b in vetores)
    print(f"F{i} {frases[i][:28]:<28} {linha}")
