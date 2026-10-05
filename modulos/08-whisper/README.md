# Módulo 8 — Whisper: voz → texto → LLM

**Objetivo:** usar um terceiro tipo de modelo (fala → texto) e **encadear** com a LLM: fale uma pergunta, receba a resposta.

**Tempo:** ~1,5 h · **Pré-requisito:** `ollama serve` rodando (para a parte final).

---

## Passo 1 — Instalar o whisper.cpp

### 🍎 macOS / Linux — compilar

Não existe binário pronto para Mac, então você vai **compilar** (transformar código C++ em programa). É uma ótima prévia do opcional "compilar o llama.cpp".
Pré-requisito no Mac: ferramentas de linha de comando da Apple (`xcode-select --install`, se ainda não tiver). No Linux: `build-essential` e `git`.

```bash
uv tool install cmake            # ferramenta de compilação (instalada via uv, sem Homebrew)

cd ~/ai-lab/ferramentas
git clone --depth 1 https://github.com/ggml-org/whisper.cpp
cd whisper.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=OFF   # configura (OFF = sem GPU; em Mac M1–M4 tire essa opção)
cmake --build build -j 8 --config Release                    # compila (~3–5 min, 8 em paralelo)
ls build/bin                                                 # 🎉 seus programas
```

👀 Nos logs de compilação, procure `AVX2` e `FMA`: o compilador está gerando código específico para a **sua** CPU.

### 🪟 Windows — baixar pronto

No Windows existe binário oficial. Em <https://github.com/ggml-org/whisper.cpp/releases>, procure o release mais recente que tenha o arquivo **`whisper-bin-x64.zip`** (no momento, o `b5130`):

```powershell
cd $HOME\ai-lab\ferramentas
curl.exe -L -o whisper.zip https://github.com/ggml-org/whisper.cpp/releases/download/b5130/whisper-bin-x64.zip
mkdir whisper.cpp; tar -xf whisper.zip -C whisper.cpp; rm whisper.zip
ls whisper.cpp\Release          # 🎉 whisper-cli.exe está aqui
```

👀 Repare nos vários `ggml-cpu-*.dll` (haswell, alderlake...): mesma ideia do Ollama — uma versão do motor por geração de CPU.

## Passo 2 — Baixar modelos e testar

Os modelos ficam em `ferramentas/whisper.cpp/models`:

**🍎 macOS / Linux**
```bash
cd ~/ai-lab/ferramentas/whisper.cpp
sh ./models/download-ggml-model.sh base     # ~150 MB, rápido
sh ./models/download-ggml-model.sh small    # ~480 MB, bem melhor em português

./build/bin/whisper-cli -m models/ggml-base.bin -f samples/jfk.wav
```

**🪟 Windows**
```powershell
cd $HOME\ai-lab\ferramentas\whisper.cpp
mkdir -Force models, samples
curl.exe -L -o models\ggml-base.bin  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
curl.exe -L -o models\ggml-small.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin
curl.exe -L -o samples\jfk.wav https://raw.githubusercontent.com/ggml-org/whisper.cpp/master/samples/jfk.wav

.\Release\whisper-cli.exe -m models\ggml-base.bin -f samples\jfk.wav
```

Deve sair o discurso do Kennedy. 11 segundos de áudio transcritos em 1–2 segundos.

## Passo 3 — Voz → LLM

```bash
cd ~/ai-lab
uv run modulos/08-whisper/voz.py
```

Permissão de **microfone**:
- 🍎 Na primeira vez, o macOS pergunta se o Terminal pode usar o microfone — aceite. (Se gravar silêncio: Ajustes do Sistema → Privacidade e Segurança → Microfone → Terminal.)
- 🪟 Se gravar silêncio: Configurações → Privacidade e segurança → Microfone → ative "Permitir que aplicativos da área de trabalho acessem o microfone". Confira também qual é o microfone padrão em Configurações → Sistema → Som.

Compare os modelos do Whisper:

```bash
uv run modulos/08-whisper/voz.py --modelo-whisper base
uv run modulos/08-whisper/voz.py --modelo-whisper small
```

## 👀 O que observar

- `base` × `small`: velocidade e erros em português (acentos, nomes próprios, números).
- O Whisper também é um **Transformer** — mas a entrada é um *espectrograma* (o áudio desenhado como imagem de frequências) em vez de tokens de texto. A saída é texto, gerada token a token como numa LLM.
- Às vezes ele "alucina" em silêncio (escreve "Obrigado." ou "Legendas por..."). Isso vem dos dados de treino: muito áudio da internet terminava com legendas assim.
- O pipeline todo (gravação → Whisper → LLM) mostra o padrão de **encadear modelos especializados**, que é como assistentes de voz funcionam.

## 🎯 Desafios

1. Transforme `voz.py` num loop: várias perguntas seguidas, com histórico (junte com o `03_chat.py`).
2. Teste o `-l auto` (detecção automática de idioma) falando em inglês.
3. Experimente o `whisper-server` (🍎 em `build/bin` · 🪟 em `Release`): uma API HTTP para transcrição, como a do Ollama.
4. Ligue voz → **RAG** (Módulo 4): pergunte em voz alta sobre seus documentos.
