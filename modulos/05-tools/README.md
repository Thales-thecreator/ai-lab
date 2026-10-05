# Módulo 5 — Integrar: tool calling e um agente simples

**Objetivo:** fazer o modelo **decidir chamar funções Python** (ferramentas) e entender o loop de um "agente".

**Tempo:** ~1,5 h · **Pré-requisito:** `ollama serve` rodando.

---

## A ideia

LLMs são ruins em conta e não sabem a hora atual nem o que tem nos seus arquivos. Mas podem **pedir** para você rodar uma função:

```
você: "quanto é 1234 * 5678?"
  │
  ▼
LLM ──▶ "quero chamar calcular(expressao='1234*5678')"       ← tool call (JSON)
  │
seu código roda calcular() ──▶ "7006652"                    ← resultado volta como mensagem role=tool
  │
  ▼
LLM ──▶ "1234 × 5678 = 7.006.652"                           ← resposta final
```

O modelo **nunca executa nada**. Ele só escreve um JSON dizendo qual função quer e com quais argumentos. Quem executa é o **seu** código. Um **agente** é só esse ciclo repetido até o modelo parar de pedir ferramentas.

## Passo 1 — Rodar o agente

```bash
cd ~/ai-lab
uv run modulos/05-tools/agente.py
```

Teste:
- "Quanto é 987654 * 123456?"
- "Que horas são agora?"
- "Quais arquivos existem na pasta do lab?"
- "Leia o README.md e me diga quantos módulos tem o lab."
- "Quanto é 2+2 e que dia é hoje?" ← duas ferramentas
- "Me conte uma piada." ← nenhuma ferramenta

O script mostra **cada** tool call. Leia o código: as ferramentas são funções Python normais, e a "descrição" que o modelo vê vem da docstring e dos tipos.

## 👀 O que observar — falhas são parte da lição

Com modelos de 3–8B, tool calling **funciona mas falha às vezes**. Procure:
- Chamar ferramenta **sem precisar** (ex.: calculadora para "oi").
- **Não** chamar quando precisava (e chutar o resultado da conta).
- Argumentos errados (caminho de arquivo inventado).
- Entrar em **loop** chamando a mesma coisa (por isso existe `MAX_PASSOS`).

Rode as mesmas perguntas com `qwen3:8b` e com `llama3.2:3b` (mude `MODELO`). Anote no `NOTAS.md` qual erra mais.

## ⚠️ Segurança

`ler_arquivo` só lê dentro de `~/ai-lab`. Nunca dê a um modelo uma ferramenta que **apaga**, **envia** ou **executa** coisas sem você confirmar — modelos erram, e textos lidos podem conter instruções maliciosas (*prompt injection*).

## 🎯 Desafios

1. Crie uma ferramenta `buscar_documentos(pergunta)` que usa o RAG do Módulo 4. Agora o agente decide **quando** buscar.
2. Crie `salvar_nota(texto)` que adiciona uma linha ao `NOTAS.md` — mas peça confirmação (`input("ok? s/n")`) antes de escrever.
