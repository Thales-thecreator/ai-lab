# Módulo 3 — Integrar: embeddings e busca semântica

**Objetivo:** entender como um texto vira uma **lista de números** que captura o significado, e usar isso para buscar por *sentido* (não por palavra exata).

**Tempo:** ~1,5 h · **Pré-requisito:** `ollama serve` rodando e `embeddinggemma` baixado.

---

## A ideia

Um **embedding** transforma um texto num vetor (uma lista de números, aqui 768). Textos com significado parecido viram vetores que **apontam para direções parecidas**.

```
"o gato dormiu no sofá"        → [0.12, -0.40, 0.88, ...]  ┐ parecidos
"o felino cochilou na poltrona" → [0.10, -0.38, 0.91, ...]  ┘
"a bolsa de valores caiu"      → [-0.70, 0.22, 0.05, ...]    diferente
```

Para medir "parecido" usamos a **similaridade de cosseno**: 1 = mesma direção, 0 = sem relação.

> O modelo de embedding **não gera texto**. É outro tipo de modelo, pequeno e rápido, que só "lê" e devolve o vetor.

## Passo 1 — Ver um embedding

```bash
uv run modulos/03-embeddings/01_basico.py
```

Veja o tamanho do vetor e a matriz de similaridade entre frases.

## Passo 2 — Buscador semântico

```bash
uv run modulos/03-embeddings/02_buscador.py
```

Ele indexa ~20 frases sobre assuntos variados. Busque coisas **sem usar as mesmas palavras** das frases. Ex.: "animal de estimação", "dinheiro", "como fazer comida".

## 👀 O que observar

- "Felino" encontra frases com "gato" — a busca por palavra-chave (Ctrl+F) não faria isso.
- A similaridade nunca é exatamente 0; frases sem relação ficam em torno de 0,3 com esse modelo. O que importa é a **ordem**.
- O `embeddinggemma` foi treinado com prefixos: `task: search result | query:` para perguntas e `title: ... | text:` para documentos (veja o código). Tire-os e compare.

## 🧪 Experimento: modelo de embedding errado

Nem todo modelo de embedding entende português. Baixe o popular `nomic-embed-text` (treinado quase só em inglês):

```bash
ollama pull nomic-embed-text
```

Troque `MODELO` em `01_basico.py` e rode de novo. Com ele, "gato × felino" fica tão parecido quanto "gato × bolsa de valores" (~0,57) — ele não separa os assuntos. Moral: **para RAG em português, escolha um embedding multilíngue.**

## 🎯 Desafios

1. Adicione frases suas ao buscador.
2. Busque em inglês frases que estão em português. Funciona? Por quê?
3. Mostre a busca por palavra-chave ao lado da semântica para comparar.
