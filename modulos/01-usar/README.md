# Módulo 1 — Usar: comparar modelos

**Objetivo:** criar intuição sobre o trade-off **tamanho × velocidade × qualidade**, e notar diferenças entre "famílias" de modelos.

**Tempo:** ~1 h · **Pré-requisito:** `ollama serve` rodando em outra aba.

---

## Conceitos rápidos

- **Parâmetros (1.7b, 3b, 8b):** quantos números ("pesos") o modelo tem. Mais pesos ≈ mais conhecimento e raciocínio, mas mais RAM e mais lento.
- **Token:** pedaço de texto (≈ ¾ de uma palavra em inglês; em português costuma ser menos). Modelos leem e escrevem token por token.
- **Família:** Qwen (Alibaba), Llama (Meta), Gemma (Google)... treinadas com dados diferentes → estilos diferentes.
- **Modo "thinking" (Qwen3):** o modelo "pensa em voz alta" antes de responder (aparece entre `<think>` e `</think>`). Melhora raciocínio, mas gasta muito mais tokens.

## Passo 1 — Bateria de perguntas

O script roda as **mesmas** perguntas em vários modelos e mede a velocidade:

```bash
cd ~/ai-lab
uv run modulos/01-usar/comparar.py
```

Ele demora alguns minutos (o 8B é lento — isso faz parte da lição). Leia as respostas com calma.

## Passo 2 — Preencha a tabela no `NOTAS.md`

Para cada modelo: tamanho (`ollama list`), tokens/s (saída do script) e uma nota de qualidade sua.

## Passo 3 — Thinking ligado × desligado

```bash
ollama run qwen3:8b --verbose
```

Pergunte: *"Um bastão e uma bola custam R$ 1,10 no total. O bastão custa R$ 1,00 a mais que a bola. Quanto custa a bola?"*

Depois, na mesma sessão, digite `/set nothink` e pergunte de novo. Compare o tempo total e se acertou (resposta: R$ 0,05).

## 👀 O que observar

- O modelo de 1.7B **inventa** fatos com confiança? (isso se chama *alucinação*)
- Em português, qual modelo escreve melhor?
- A primeira resposta de cada modelo demora mais: é o tempo de **carregar** o modelo do disco para a RAM.
- O `eval rate` do 8B é ~3–4× menor que o do 1.7B. Bate com a proporção de tamanho?

## 🎯 Desafio

Edite `comparar.py` e adicione uma pergunta sua — uma do seu trabalho, de preferência. Qual o **menor** modelo que responde bem o suficiente?
