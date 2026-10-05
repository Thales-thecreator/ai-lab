# Módulo 7 — Por dentro: treine um mini-GPT do zero

**Objetivo:** treinar **seu próprio** modelo de linguagem, com a mesma arquitetura do ChatGPT/Llama/Qwen, só que minúsculo — e ver ele sair do ruído aleatório até escrever "quase Shakespeare".

**Tempo:** ~2 h (o treino leva ~13 min num i7 de 2015; varia com a CPU) · Não precisa do Ollama.

---

## Os 3 arquivos

| Arquivo | O que é |
|---|---|
| `modelo.py` | a arquitetura Transformer (~80 linhas). **Leia com calma.** |
| `treinar.py` | baixa o texto, treina, salva `mini-gpt-*.pt` |
| `gerar.py` | carrega o modelo salvo e gera texto |

## Passo 1 — Treinar

```bash
cd ~/ai-lab
uv run modulos/07-mini-gpt/treinar.py
```

A cada 500 passos ele mostra a **perda** e uma **amostra** de texto. Acompanhe a evolução:

| Passo | Perda | O que o modelo "sabe" |
|---|---|---|
| 0 | ~4,2 | nada — letras aleatórias (ln 65 ≈ 4,17 = chute uniforme) |
| 500 | ~2,0 | frequência de letras, espaços, quebras de linha, nomes em MAIÚSCULA: |
| 1500 | ~1,7 | palavras curtas reais, estrutura de diálogo |
| 3000 | ~1,5 | palavras quase sempre reais, "ritmo" de Shakespeare, mas sem sentido |

## Passo 2 — Gerar

```bash
uv run modulos/07-mini-gpt/gerar.py --inicio "ROMEO:"
uv run modulos/07-mini-gpt/gerar.py --temp 0.3
uv run modulos/07-mini-gpt/gerar.py --temp 1.5
```

O efeito da temperature é o mesmo do Módulo 6 — porque é **o mesmo mecanismo** (veja `gerar()` em `modelo.py`: `softmax(logits / temperature)` e depois sorteio).

## Passo 3 — Em português

```bash
uv run modulos/07-mini-gpt/treinar.py --dados machado
uv run modulos/07-mini-gpt/gerar.py machado --inicio "Capitu"
```

## 👀 O que observar

- **Perda de treino × validação:** validação = texto que o modelo **nunca viu**. Se a de treino cai e a de validação para ou sobe, o modelo está **decorando** (overfitting). Dom Casmurro é ~3× menor que o Shakespeare — acontece mais cedo?
- **Tokenizador:** aqui 1 caractere = 1 token (vocabulário 65). Os modelos de verdade usam pedaços de palavras (~150 mil; Módulo 6). Por isso o nosso precisa "aprender a soletrar".
- **Escala:** este modelo tem 0,8 milhão de parâmetros e treinou em minutos numa CPU comum. O `qwen3:8b` tem 10.000× mais parâmetros e treinou com trilhões de tokens em milhares de GPUs por semanas. A **arquitetura** é essencialmente a mesma.
- O modelo **não** tem modo chat. Modelos de chat passam por mais duas fases depois desta: *instruction tuning* e *RLHF*. O que você treinou é um **modelo base**: só continua texto.

## Mapa: código ↔ conceitos

| Conceito | Onde no código |
|---|---|
| Embedding de token | `self.emb_token` |
| Embedding de posição | `self.emb_posicao` |
| Atenção (cada token olha os anteriores) | `AutoAtencao` — `is_causal=True` |
| Multi-head | `n_heads` em `Config` |
| Conexão residual | `x = x + ...` em `Bloco` |
| Logits → probabilidades | `F.softmax(...)` em `gerar` |
| Função de perda | `F.cross_entropy` |
| Gradiente / aprendizado | `perda.backward()` + `otimizador.step()` |

## 🎯 Desafios

1. Dobre `n_camadas` para 8. Fica melhor? Quanto mais lento?
2. Reduza `contexto` para 16. O que piora no texto gerado?
3. Treine com um texto seu (coloque um `.txt` em `dados/` e adicione em `FONTES`).
4. Para ir fundo: assista **"Let's build GPT: from scratch"** (Andrej Karpathy, YouTube) — este código segue a mesma linha.
