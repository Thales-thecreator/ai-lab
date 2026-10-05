# 🧪 AI Lab — aprenda IA local na prática

Lab para entender como IA local funciona: **usar**, **integrar** e **ver por dentro**.
Funciona em **macOS** e **Windows** (e Linux, com os comandos de macOS).

## Que computador eu preciso?

| Recurso | Mínimo | Confortável |
|---|---|---|
| RAM | 8 GB (modelos até ~3B) | 16 GB (modelos até ~8B) |
| Disco livre | 25 GB | 50 GB |
| CPU | x64 com AVX2 (Intel 2015+ / AMD Ryzen) ou Apple Silicon | — |
| GPU | não precisa | NVIDIA com 6 GB+ de VRAM, ou Mac M1/M2/M3/M4 → bem mais rápido |

O lab foi criado e testado num **iMac 2015** (i7‑6700K, 16 GB, só CPU). Nessa máquina:
modelos 1–3B ≈ 10–50 tokens/s · 7–8B ≈ 4–7 tokens/s. Se o seu computador tem GPU NVIDIA ou é um Mac com Apple Silicon, o Ollama usa a GPU sozinho e tudo fica várias vezes mais rápido.

## Como os comandos aparecem neste guia

Quando o comando é diferente entre os sistemas, aparecem **dois blocos**:

**🍎 macOS / Linux** (app *Terminal*)
```bash
ls ~/ai-lab
```

**🪟 Windows** (app *PowerShell* — **não** use o "Prompt de Comando"/cmd)
```powershell
ls $HOME\ai-lab
```

Quando há um bloco só, ele funciona igual nos dois (por exemplo, `uv run ...` e `ollama ...`).

Diferenças que aparecem o tempo todo:

| | 🍎 macOS / Linux | 🪟 Windows (PowerShell) |
|---|---|---|
| Pasta do lab | `~/ai-lab` | `$HOME\ai-lab` (= `C:\Users\<você>\ai-lab`) |
| Separador de pastas | `/` | `\` (o `/` também costuma funcionar) |
| Baixar arquivo | `curl` | `curl.exe` (só `curl` no PowerShell é outro comando!) |
| Nova aba do terminal | `Cmd+T` | `Ctrl+Shift+T` (Windows Terminal) |
| Programas | `ollama` | `ollama.exe` (pode digitar só `ollama`) |

## Ferramentas

| Ferramenta | Para quê | Onde |
|---|---|---|
| **uv** | gerencia o Python 3.12 e as bibliotecas do lab | Módulo 0 |
| **Ollama** | servidor de modelos com API simples | Módulo 0 → `ferramentas/ollama` |
| **llama.cpp** | o "motor" por baixo do Ollama, com todos os botões expostos | Módulo 6 → `ferramentas/llama.cpp` |
| **whisper.cpp** | áudio → texto | Módulo 8 → `ferramentas/whisper.cpp` |

Todas são instaladas **dentro da pasta do lab**, sem instalador e sem senha de administrador. Para desinstalar tudo, apague a pasta (e a linha do PATH, ver Módulo 0).

## Roteiro

| # | Módulo | Você termina com |
|---|---|---|
| 0 | [Fundamentos + instalação](modulos/00-fundamentos/README.md) | primeiro `ollama run` funcionando |
| 1 | [Usar: comparar modelos](modulos/01-usar/README.md) | sua tabela de comparação |
| 2 | [Integrar: a API](modulos/02-api/README.md) | um chat no terminal feito por você |
| 3 | [Integrar: embeddings](modulos/03-embeddings/README.md) | um buscador semântico |
| 4 | [Integrar: RAG](modulos/04-rag/README.md) | "pergunte aos seus arquivos" |
| 5 | [Integrar: tool calling](modulos/05-tools/README.md) | um agente que usa ferramentas |
| 6 | [Por dentro: tokens, sampling, quantização](modulos/06-por-dentro/README.md) | experimento qualidade × velocidade × tamanho |
| 7 | [Por dentro: treine um mini-GPT](modulos/07-mini-gpt/README.md) | um modelo **seu** gerando texto |
| 8 | [Whisper: voz → LLM](modulos/08-whisper/README.md) | fale uma pergunta, receba a resposta |
| + | [Opcionais](opcionais/README.md) | compilar llama.cpp, mini UI, MCP, LoRA |

Cada módulo tem: **objetivo**, **passos**, **o que observar** e **desafio**.

## Como rodar qualquer script

Sempre de dentro da pasta do lab (igual nos dois sistemas):

```bash
cd ~/ai-lab
uv run modulos/02-api/03_chat.py
```

`uv run` garante que o Python certo (3.12) e as bibliotecas certas sejam usados. Você não precisa "ativar" nada.

## Ollama: lembrete diário

O Ollama roda **sob demanda**. Antes de estudar, abra uma aba do terminal e deixe rodando:

```bash
ollama serve
```

Ao terminar, `Ctrl+C` nessa aba. Isso libera a RAM.

## Anotações

Copie `NOTAS.modelo.md` para `NOTAS.md` e use como diário: o que testou, o que surpreendeu, dúvidas. O `NOTAS.md` é pessoal e não vai para o git.
