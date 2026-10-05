# Módulo 6 — Por dentro: tokens, sampling e quantização

**Objetivo:** abrir o capô. Ver o texto virar tokens, ver a LLM calcular **probabilidades do próximo token**, e entender o que é "Q4" no nome dos modelos.

**Tempo:** ~2 h · Aqui usamos o **llama.cpp direto**, que expõe o que o Ollama esconde.

---

## Passo 0 — Instalar o llama.cpp

Escolha o arquivo certo em <https://github.com/ggml-org/llama.cpp/releases> (os comandos abaixo usam a versão `b11429`; troque pelo número mais novo se quiser):

| Seu computador | Arquivo |
|---|---|
| Mac Intel | `llama-bXXXX-bin-macos-x64.tar.gz` |
| Mac Apple Silicon (M1–M4) | `llama-bXXXX-bin-macos-arm64.tar.gz` |
| Windows, só CPU | `llama-bXXXX-bin-win-cpu-x64.zip` |
| Windows + GPU NVIDIA | `llama-bXXXX-bin-win-cuda-12.4-x64.zip` **e** `cudart-llama-bin-win-cuda-12.4-x64.zip` (descompacte os dois na mesma pasta) |
| Windows + GPU AMD/Intel | `llama-bXXXX-bin-win-vulkan-x64.zip` |

**🍎 macOS**
```bash
cd ~/ai-lab/ferramentas
curl -L -o llama.tgz https://github.com/ggml-org/llama.cpp/releases/download/b11429/llama-b11429-bin-macos-x64.tar.gz
mkdir -p llama.cpp && tar -xzf llama.tgz -C llama.cpp --strip-components=1 && rm llama.tgz

echo 'export PATH="$HOME/ai-lab/ferramentas/llama.cpp:$PATH"' >> ~/.zshrc
source ~/.zshrc
which llama-server     # deve apontar para ferramentas/llama.cpp (o Ollama tem um com o mesmo nome!)
```

**🪟 Windows**
```powershell
cd $HOME\ai-lab\ferramentas
curl.exe -L -o llama.zip https://github.com/ggml-org/llama.cpp/releases/download/b11429/llama-b11429-bin-win-cpu-x64.zip
mkdir llama.cpp; tar -xf llama.zip -C llama.cpp; rm llama.zip

# llama.cpp vai para o INÍCIO do PATH, para ter prioridade sobre o do Ollama
$dir = "$HOME\ai-lab\ferramentas\llama.cpp"
[Environment]::SetEnvironmentVariable("Path", "$dir;" + [Environment]::GetEnvironmentVariable("Path", "User"), "User")
$env:Path = "$dir;$env:Path"
Get-Command llama-server   # deve apontar para ferramentas\llama.cpp
```

Baixe o modelo de estudo (o mesmo Qwen3 1.7B do Ollama, mas como arquivo `.gguf` solto):

**🍎 macOS / Linux**
```bash
mkdir -p ~/ai-lab/modelos && cd ~/ai-lab/modelos
curl -L -o Qwen3-1.7B-Q4_K_M.gguf https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q4_K_M.gguf
```

**🪟 Windows**
```powershell
mkdir -Force $HOME\ai-lab\modelos; cd $HOME\ai-lab\modelos
curl.exe -L -o Qwen3-1.7B-Q4_K_M.gguf https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q4_K_M.gguf
```

Ligue o servidor (**Aba 1**, deixe rodando; pode desligar o `ollama serve` para liberar memória). `-t` é o número de threads: use o número de **núcleos físicos** da sua CPU (4 é um bom chute).

**🍎 macOS / Linux**
```bash
llama-server -m ~/ai-lab/modelos/Qwen3-1.7B-Q4_K_M.gguf -c 4096 -t 4
```

**🪟 Windows**
```powershell
llama-server -m $HOME\ai-lab\modelos\Qwen3-1.7B-Q4_K_M.gguf -c 4096 -t 4
```

> Com GPU (build CUDA/Vulkan ou Apple Silicon), acrescente `-ngl 99` para colocar todas as camadas na GPU — e compare a velocidade!

Bônus: abra <http://localhost:8080> no navegador — o llama-server tem uma UI de chat embutida.

---

## Parte A — Tokens

```bash
cd ~/ai-lab
uv run modulos/06-por-dentro/01_tokens.py
uv run modulos/06-por-dentro/01_tokens.py "escreva aqui o que quiser"
```

👀 Observe:
- Palavras comuns em inglês = 1 token. Em português, palavras com acento costumam quebrar (`[Ol][á]`).
- Números viram **um token por dígito** → um dos motivos de LLMs errarem contas.
- O espaço faz parte do token (`[·como]`).
- O modelo nunca vê letras: vê **IDs** (números). Por isso ele erra "quantos R tem em *morango*?".

## Parte B — Próximo token e sampling

```bash
uv run modulos/06-por-dentro/02_proximo_token.py
uv run modulos/06-por-dentro/02_proximo_token.py "A capital da França é"
```

👀 Observe:
- Uma LLM é **uma função**: texto → probabilidades para *cada* token do vocabulário (~150 mil). Gerar texto = repetir isso, um token por vez.
- **temperature 0**: sempre o mais provável → resposta idêntica toda vez (determinística).
- **temperature 0.7**: sorteia entre os prováveis → variedade com coerência.
- **temperature 1.5**: dá chance para candidatos ruins → criatividade vira delírio.
- Com "A capital da França é", o top 1 tem quase 100%. Com "Era uma vez um", o mais provável tem ~3%. **Incerteza** é visível.

Outros botões do sampling (teste no chat do navegador, menu de configurações):
- **top_k**: só sorteia entre os K mais prováveis.
- **top_p**: só sorteia entre os que somam P% de probabilidade.
- **repeat_penalty**: penaliza repetir tokens recentes.

## Parte C — Quantização

Um modelo de 1.7B tem 1,7 bilhão de números. Guardar cada um com:
- 16 bits (BF16) → ~3,4 GB · **original**
- 8 bits (Q8_0) → ~1,8 GB
- ~4,5 bits (Q4_K_M) → ~1,1 GB · o padrão do Ollama
- ~2,5 bits (Q2_K) → ~0,8 GB

Menos bits = arquivo menor e **mais rápido** (a CPU passa a maior parte do tempo esperando a RAM entregar os pesos), mas os números ficam "arredondados" → qualidade cai.

Baixa ~7 GB na primeira vez:

**🍎 macOS / Linux**
```bash
zsh modulos/06-por-dentro/03_quantizacao.sh
```

**🪟 Windows**
```powershell
powershell -ExecutionPolicy Bypass -File modulos\06-por-dentro\03_quantizacao.ps1
```

👀 Observe:
- `tg` (gerar) escala com o tamanho do arquivo: metade do tamanho ≈ quase o dobro da velocidade. Isso mostra que o gargalo é a **memória**, não o processamento.
- `pp` (ler prompt) é muito mais rápido que `tg`: o prompt é processado em paralelo; a geração é sequencial.
- Compare as respostas: a partir de qual nível a qualidade cai visivelmente?

## Parte D — O Ollama por baixo dos panos

**🍎 macOS / Linux**
```bash
ollama show qwen3:1.7b --modelfile | grep FROM
```

**🪟 Windows**
```powershell
ollama show qwen3:1.7b --modelfile | Select-String FROM
```

Esse caminho em `.ollama/models/blobs/...` (na sua pasta pessoal) é um **arquivo GGUF comum**. Rode o llama.cpp direto nele:

```bash
llama-server -m <cole o caminho aqui> -c 4096 -t 4
```

O Ollama = llama.cpp + download de modelos + gerenciamento de memória + API mais simples.

## 🎯 Desafios

1. No `02_proximo_token.py`, troque a geração greedy por um sorteio seu: use `random.choices` com as probabilidades do top 10.
2. Rode `llama-bench` com `-t 1`, `-t 4` e `-t 8`. Mais threads é sempre melhor? (Descubra seus núcleos: 🍎 `sysctl hw.physicalcpu hw.logicalcpu` · 🪟 `Get-CimInstance Win32_Processor | Select NumberOfCores, NumberOfLogicalProcessors`.)
3. Calcule: quantos GB o `qwen3:8b` teria em BF16? Caberia na sua RAM?
