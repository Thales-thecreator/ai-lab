# Módulo 4 — Integrar: RAG ("pergunte aos seus arquivos")

**Objetivo:** juntar o Módulo 2 (chat) com o 3 (embeddings) para que a LLM responda com base em **documentos seus** — sem treinar nada e sem nada sair da máquina.

**Tempo:** ~2 h · **Pré-requisito:** `ollama serve` rodando.

---

## A ideia

**RAG** = *Retrieval-Augmented Generation* = "geração aumentada por busca".

```
pergunta ──▶ embedding ──▶ busca os trechos mais parecidos ──┐
                                                             ▼
           LLM ◀── prompt: "responda usando só estes trechos: [1]... [2]... Pergunta: ..."
            │
            ▼
        resposta citando [1], [2]
```

A LLM não "aprende" seus documentos. A cada pergunta, o script **cola os trechos relevantes no prompt**. É o mesmo truque do histórico do Módulo 2: tudo é texto na entrada.

## Passo 1 — Dados públicos

```bash
cd ~/ai-lab
uv run modulos/04-rag/baixar_publicos.py
uv run modulos/04-rag/rag.py
```

Perguntas para testar:
- "O que é um transformer e quem o criou?"
- "Quais são os planetas do Sistema Solar?"
- "Onde o café foi descoberto?"
- "Quem ganhou a Copa de 2002?" ← **não** está nos documentos. Ele admite que não sabe?

## Passo 2 — Seus documentos

Passe a pasta com os seus documentos (entre aspas, por causa de espaços no nome):

**🍎 macOS / Linux**
```bash
uv run modulos/04-rag/rag.py "~/Documents/Minha Pasta"
```

**🪟 Windows**
```powershell
uv run modulos/04-rag/rag.py "$HOME\Documents\Minha Pasta"
```

> Dica: no Explorer do Windows, clique com o botão direito na pasta → "Copiar como caminho" e cole entre as aspas. No Finder do Mac, arraste a pasta para dentro do Terminal.

O script lê `.pdf`, `.docx`, `.txt` e `.md`. Faça perguntas sobre o conteúdo: contratos, relatórios, anotações...

> 🔒 Tudo roda localmente: os documentos não saem do seu computador.
> ⚠️ PDFs que são **imagem escaneada** não têm texto extraível — o script vai ignorá-los. (Resolver isso = OCR, um desafio extra.)

## 👀 O que observar

- Os **trechos recuperados** aparecem antes da resposta. Quando a resposta é ruim, quase sempre o problema está na **busca** (trechos errados), não na LLM.
- Mude `TAMANHO_CHUNK` para 300 e para 3000. O que acontece com a qualidade?
- Mude `TOP_K` para 1 e para 8. Mais contexto = mais lento (mais tokens para ler).
- Troque `MODELO_CHAT` para `qwen3:1.7b`. O modelo pequeno segue a instrução "use APENAS os trechos"?

## 🎯 Desafios

1. Faça o script **mostrar o prompt completo** enviado à LLM (descomente/adicione um `print(prompt)`). Veja com seus olhos que RAG é só texto colado.
2. Faça o RAG lembrar da conversa (junte com o histórico do `03_chat.py`).
3. Adicione suporte a outro formato de arquivo (`.csv`? `.html`?).
