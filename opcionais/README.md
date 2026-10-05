# Opcionais

Para depois dos 8 módulos, em qualquer ordem.

## A) Compilar o llama.cpp do código-fonte

Mesmo processo do whisper.cpp no Mac (Módulo 8).

Pré-requisitos no 🪟 Windows (no Mac já foram instalados no Módulo 8):
- **Git**: <https://git-scm.com/download/win>
- **Visual Studio Build Tools** com a carga de trabalho "Desenvolvimento para desktop com C++": <https://visualstudio.microsoft.com/visual-cpp-build-tools/>
- **cmake**: `uv tool install cmake`

Os comandos são os mesmos nos dois sistemas (no Windows, rode no PowerShell):

```bash
cd ~/ai-lab/ferramentas
git clone --depth 1 https://github.com/ggml-org/llama.cpp llama.cpp-src
cd llama.cpp-src
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=OFF -DGGML_NATIVE=ON
cmake --build build -j 8 --config Release
```

Os programas ficam em 🍎 `build/bin` · 🪟 `build\bin\Release`.

👀 Compare com `llama-bench` o binário que você compilou (`-DGGML_NATIVE=ON` = otimizado para **esta** CPU) com o baixado pronto (genérico). Há diferença?

Para ir além: abra `src/llama-sampling.cpp` e encontre a temperature sendo aplicada. É uma divisão — igual ao `modelo.py` do Módulo 7.

## B) Mini UI de chat no navegador

Construa uma interface web para o seu `03_chat.py`, usando só a biblioteca padrão:
- `http.server` em Python servindo uma página HTML
- a página faz `fetch("/chat")` com o histórico
- o servidor repassa para o Ollama e devolve a resposta

Dica: comece sem streaming. Depois adicione streaming com *Server-Sent Events*.

## C) MCP — conectar o modelo local a ferramentas padronizadas

**MCP** (*Model Context Protocol*) é um padrão para ferramentas: em vez de escrever `calcular()` dentro do seu script (Módulo 5), a ferramenta vive num **servidor MCP** separado, que qualquer cliente (Claude, seu agente, outros apps) pode usar.

Roteiro:
1. `uv add mcp` e crie um servidor MCP com uma ferramenta (`FastMCP`, ~15 linhas).
2. Modifique o `agente.py` para **listar** as ferramentas do servidor MCP e convertê-las para o formato do Ollama.
3. Quando o modelo pedir uma ferramenta, encaminhe a chamada para o servidor MCP.

👀 Você vai ver que o MCP é o mesmo loop do Módulo 5 — só que com as ferramentas do outro lado de um protocolo.

## D) Fine-tune com LoRA (leitura)

Fazer fine-tune só na CPU leva horas (com GPU NVIDIA de 8 GB+ dá para praticar localmente), então fica como **leitura**:
- **O que é:** em vez de treinar os bilhões de pesos, treina-se uma "camada fina" extra (milhões de pesos) que ajusta o comportamento.
- **Quando usar:** ensinar **estilo/formato** (responder sempre em JSON, tom da empresa). Para ensinar **fatos**, RAG (Módulo 4) quase sempre é melhor.
- **Onde praticar de graça:** notebooks do *Unsloth* no Google Colab (GPU gratuita) → exporta `.gguf` → roda aqui no Ollama com um `Modelfile`.

## E) Modelfile — personalizar modelos no Ollama

Crie um arquivo de texto `Modelfile` (sem extensão) em `ai-lab/opcionais` com este conteúdo:

```
FROM llama3.2:3b
PARAMETER temperature 0.3
SYSTEM Você é um revisor de textos em português. Aponte erros e sugira correções.
```

Pode usar qualquer editor (TextEdit em modo texto simples, Bloco de Notas, VS Code). No Bloco de Notas, escolha "Todos os arquivos" ao salvar, para ele não virar `Modelfile.txt`. Depois:

```bash
cd ~/ai-lab/opcionais
ollama create revisor -f Modelfile
ollama run revisor
```

O modelo **não** foi treinado de novo — é só o mesmo arquivo GGUF com um system prompt e parâmetros fixos. Confira com `ollama show revisor --modelfile`.
