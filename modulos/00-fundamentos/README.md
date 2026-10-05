# Módulo 0 — Fundamentos + instalação

**Objetivo:** entender o mínimo de terminal, Python e API para não ficar só copiando e colando. No fim, instalar o Ollama e conversar com o primeiro modelo.

**Tempo:** ~1,5 h

> Os comandos aparecem em blocos **🍎 macOS / Linux** e **🪟 Windows (PowerShell)** quando são diferentes. Veja a seção "Como os comandos aparecem" no [README principal](../../README.md).

---

## Parte A — Terminal em 10 minutos

O terminal é uma conversa por texto com o computador: você digita um **comando**, ele responde.

- 🍎 macOS: abra o app **Terminal** (`Cmd+Espaço` → "Terminal").
- 🪟 Windows: abra o **PowerShell** (menu Iniciar → "PowerShell" ou "Terminal"). Não use o "Prompt de Comando" (cmd).

| Comando | O que faz | 🍎 Teste | 🪟 Teste |
|---|---|---|---|
| `pwd` | mostra **onde** você está (pasta atual) | `pwd` | `pwd` |
| `ls` | **lista** o que tem na pasta | `ls ~/ai-lab` | `ls $HOME\ai-lab` |
| `cd` | **muda** de pasta | `cd ~/ai-lab` | `cd $HOME\ai-lab` |
| `cat` | **mostra** o conteúdo de um arquivo | `cat README.md` | `cat README.md` |
| `~` / `$HOME` | atalho para sua pasta pessoal | `cd ~` | `cd $HOME` |
| `Ctrl+C` | **interrompe** o programa rodando | — | — |
| `↑` | repete o comando anterior | — | — |

> No PowerShell, `ls`, `cat` e `pwd` são apelidos de comandos do Windows (`Get-ChildItem`, `Get-Content`...). Funcionam do mesmo jeito para o que vamos fazer.

Conceito importante — **PATH**: quando você digita `ollama`, o terminal procura um programa com esse nome numa lista de pastas chamada `PATH`. Veja a sua:

**🍎 macOS / Linux**
```bash
echo $PATH
```

**🪟 Windows**
```powershell
$env:Path -split ";"
```

Se um programa "não é encontrado" (`command not found` / `não é reconhecido como nome de cmdlet`), quase sempre é porque a pasta dele não está no PATH.

## Parte B — Pegar o lab e instalar o uv

Coloque a pasta `ai-lab` (que você recebeu em .zip ou via git) na sua pasta pessoal: `~/ai-lab` no Mac, `C:\Users\<você>\ai-lab` no Windows.

Agora instale o **uv**, o gerenciador de Python do lab:

**🍎 macOS / Linux**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**🪟 Windows**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Feche o terminal e abra de novo** (para ele reler o PATH) e confira: `uv --version`.

## Parte C — Python e ambientes

- **Python** é a linguagem dos scripts do lab.
- **Biblioteca** (ou pacote) é código pronto de outra pessoa: `numpy` (contas), `torch` (redes neurais), `ollama` (falar com o Ollama).
- **Ambiente virtual** é uma pasta (`.venv`) com um Python e bibliotecas **só deste projeto**, sem bagunçar o resto do computador.
- **uv** cria e gerencia esse ambiente. O arquivo `pyproject.toml` diz quais bibliotecas o lab usa.

Crie o ambiente (o uv baixa o Python 3.12 sozinho — você **não** precisa instalar Python antes):

```bash
cd ~/ai-lab
uv sync                          # baixa Python + bibliotecas (~300 MB–1 GB, só na primeira vez)
cat pyproject.toml
uv run python --version          # deve dizer 3.12.x
uv run python -c "print(2 + 2)"
```

> `uv run` sempre usa o Python do lab, mesmo que exista outro Python instalado no computador.

## Parte D — O que é uma API HTTP

Quando um programa quer algo de outro programa, ele manda uma **requisição** (request) e recebe uma **resposta** (response). Na web, isso usa o protocolo **HTTP** — o mesmo do navegador.

```
seu script  ──── POST http://localhost:11434/api/chat  {"model": ..., "messages": [...]} ────▶  Ollama
seu script  ◀─── 200 OK  {"message": {"content": "Olá!"}} ──────────────────────────────────  Ollama
```

- `localhost` = "este próprio computador". Nada sai da sua máquina.
- `11434` = a **porta**, o "número do apartamento" onde o Ollama atende.
- O corpo da mensagem é **JSON**: texto estruturado com `{chaves: valores}`.

Teste com um servidor público (precisa de internet):

**🍎 macOS / Linux**
```bash
curl https://api.github.com/repos/ollama/ollama
```

**🪟 Windows**
```powershell
curl.exe https://api.github.com/repos/ollama/ollama
```

Isso que voltou é JSON. No Módulo 2 você fará exatamente isso, mas com o Ollama.

---

## Parte E — Instalar o Ollama

Vamos usar a versão "portátil" (sem instalador, sem ícone na barra), para que ele **só rode quando você mandar**.

**🍎 macOS**
```bash
# 1. baixar (≈ 100 MB)
cd ~/ai-lab/ferramentas
curl -L -o ollama.tgz https://github.com/ollama/ollama/releases/latest/download/ollama-darwin.tgz

# 2. descompactar numa pasta própria
mkdir -p ollama && tar -xzf ollama.tgz -C ollama && rm ollama.tgz

# 3. colocar a pasta no PATH (vale para os próximos terminais)
echo 'export PATH="$HOME/ai-lab/ferramentas/ollama:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 4. conferir
ollama --version
```

> Se o macOS bloquear ("não foi possível verificar o desenvolvedor"): Ajustes do Sistema → Privacidade e Segurança → "Abrir mesmo assim".

**🪟 Windows**
```powershell
# 1. baixar (≈ 1,4 GB — inclui suporte a GPU NVIDIA)
cd $HOME\ai-lab\ferramentas
curl.exe -L -o ollama.zip https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip

# 2. descompactar numa pasta própria
mkdir ollama; tar -xf ollama.zip -C ollama; rm ollama.zip

# 3. colocar a pasta no PATH do seu usuário (vale para os próximos terminais)
$dir = "$HOME\ai-lab\ferramentas\ollama"
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$dir", "User")
$env:Path += ";$dir"

# 4. conferir
ollama --version
```

> Se o Windows Defender/SmartScreen avisar na primeira execução: "Mais informações" → "Executar assim mesmo". Se o Firewall perguntar, permita só em **redes privadas**.
>
> Alternativa mais simples (mas que fica rodando sempre, com ícone na bandeja): o instalador `OllamaSetup.exe` em <https://ollama.com/download>. Se usar ele, **pule** o `ollama serve` da Parte F — o servidor já estará ligado.

**🐧 Linux:** `curl -fsSL https://ollama.com/install.sh | sh` (instala como serviço do sistema; também dispensa o `ollama serve`).

**Observe:** liste a pasta do Ollama (🍎 `ls ~/ai-lab/ferramentas/ollama` · 🪟 `ls $HOME\ai-lab\ferramentas\ollama\lib\ollama`). Tem vários arquivos `ggml-cpu-*` lá dentro — o Ollama é construído **em cima do llama.cpp**. Cada arquivo `ggml-cpu-*` é uma versão do motor otimizada para uma geração de CPU (`haswell`, `alderlake`...); o Ollama escolhe a melhor para a sua.

## Parte F — Ligar o servidor e baixar os modelos

**Aba 1** do terminal (deixe aberta):

```bash
ollama serve
```

Vão aparecer logs. Procure a linha "inference compute" — é o Ollama descobrindo seu hardware (CPU ou GPU, e quanta memória).

**Aba 2** (🍎 `Cmd+T` · 🪟 `Ctrl+Shift+T`, ou abra outra janela do PowerShell):

```bash
ollama pull qwen3:1.7b          # ≈ 1,4 GB — pequeno e rápido
ollama pull llama3.2:3b         # ≈ 2,0 GB — pequeno, outra "família"
ollama pull qwen3:8b            # ≈ 5,2 GB — o "esperto" e lento (pule se tiver só 8 GB de RAM)
ollama pull embeddinggemma      # ≈ 0,6 GB — embeddings multilíngue (Módulo 3)
ollama list
```

## Parte G — Primeira conversa 🎉

```bash
ollama run llama3.2:3b
```

Pergunte qualquer coisa. Para sair: `/bye`.

Agora com estatísticas:

```bash
ollama run llama3.2:3b --verbose
```

Depois de cada resposta aparecem números. Os mais importantes:

- `prompt eval rate` — velocidade de **ler** sua pergunta (tokens/s)
- `eval rate` — velocidade de **escrever** a resposta (tokens/s) ← é o que você "sente"

Em outra aba, rode `ollama ps` enquanto o modelo está carregado: mostra quanto de memória ele ocupa e se está rodando em CPU ou GPU.

---

## ✅ Checklist

- [ ] `uv run python --version` mostra 3.12
- [ ] `ollama --version` funciona num terminal novo
- [ ] `ollama list` mostra os 4 modelos
- [ ] copiou `NOTAS.modelo.md` para `NOTAS.md`, conversou com um modelo e anotou o `eval rate` nele

## 🎯 Desafio

Com o `ollama serve` rodando, abra no **navegador**: <http://localhost:11434/api/tags>.
O que é isso? Compare com `ollama list`. (Dica: o comando `ollama` também é só um cliente da API.)
