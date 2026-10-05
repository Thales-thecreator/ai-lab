# Módulo 2 — Integrar: a API

**Objetivo:** entender que "conversar com uma LLM" é só **mandar JSON por HTTP**, e construir seu próprio chat no terminal.

**Tempo:** ~1,5 h · **Pré-requisito:** `ollama serve` rodando.

> Tudo que você aprender aqui vale para APIs na nuvem (OpenAI, Anthropic): muda o endereço e o formato um pouco, a ideia é a mesma.

---

## Passo 1 — Na mão, pelo terminal

**🍎 macOS / Linux**
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:3b",
  "messages": [{"role": "user", "content": "Diga oi em 3 idiomas"}],
  "stream": false
}'
```

**🪟 Windows** — no PowerShell, aspas dentro de JSON no `curl.exe` dão dor de cabeça. Use o comando nativo `Invoke-RestMethod`:
```powershell
$corpo = @{
  model    = "llama3.2:3b"
  messages = @(@{ role = "user"; content = "Diga oi em 3 idiomas" })
  stream   = $false
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri http://localhost:11434/api/chat -Method Post -Body $corpo -ContentType "application/json; charset=utf-8"
```

Leia a resposta. Encontre: o texto (`message.content`), `eval_count`, `eval_duration`.

Agora troque `"stream": false` por `true` (🪟 `$false` → `$true`) e rode de novo. 👀 Cada linha é **um pedacinho** da resposta (geralmente um token). É assim que o texto "aparece digitando" no ChatGPT.

> 🪟 Com `stream = $true` o `Invoke-RestMethod` junta tudo antes de mostrar, então você não verá o efeito "digitando" — mas verá as várias linhas JSON. O Passo 3 mostra o streaming de verdade, em Python.

## Passo 2 — A mesma coisa em Python, sem bibliotecas

```bash
uv run modulos/02-api/01_requisicao_crua.py
```

Leia o código: é o `curl` traduzido para Python.

## Passo 3 — Streaming

```bash
uv run modulos/02-api/02_streaming.py
```

## Passo 4 — Seu chat no terminal

```bash
uv run modulos/02-api/03_chat.py
```

Converse. Diga seu nome e, algumas mensagens depois, pergunte "qual é meu nome?".

## 👀 O que observar — o grande segredo

**O modelo não tem memória.** Cada requisição é independente. O chat "lembra" porque o script **reenvia o histórico inteiro** a cada mensagem (veja a lista `historico` no código).

Consequências:
- Conversas longas ficam **mais lentas** (mais tokens para ler a cada vez — veja o `prompt eval` crescer).
- Existe um limite: a **janela de contexto**. Passou dele, o começo é esquecido.

## Papéis das mensagens

| `role` | Quem fala | Para quê |
|---|---|---|
| `system` | você (o programador) | instruções de comportamento: "responda como um pirata" |
| `user` | o usuário | as perguntas |
| `assistant` | o modelo | as respostas anteriores (o histórico) |

## 🎯 Desafios

1. Mude o `SYSTEM` em `03_chat.py` para dar uma personalidade ao assistente.
2. Adicione um comando `/limpar` que zera o histórico.
3. Mostre, depois de cada resposta, quantos tokens o histórico já tem (`prompt_eval_count`).
4. Bônus: o `/bye` do `ollama run` é só um `if` num loop — igual ao seu.
