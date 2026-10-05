"""Fale uma pergunta → Whisper transcreve → LLM responde.

Uso:
  uv run modulos/08-whisper/voz.py                 # grava do microfone
  uv run modulos/08-whisper/voz.py audio.wav       # usa um arquivo WAV 16 kHz
Opções: --modelo-whisper base|small   --modelo-llm llama3.2:3b
"""

import argparse
import pathlib
import queue
import subprocess
import tempfile
import time
import wave

import numpy as np
import ollama
import sounddevice as sd

WHISPER = pathlib.Path.home() / "ai-lab" / "ferramentas" / "whisper.cpp"
TAXA = 16_000  # o Whisper espera áudio a 16 mil amostras por segundo, mono

p = argparse.ArgumentParser()
p.add_argument("arquivo", nargs="?")
p.add_argument("--modelo-whisper", default="small")
p.add_argument("--modelo-llm", default="llama3.2:3b")
args = p.parse_args()


def gravar() -> pathlib.Path:
    """Grava do microfone entre dois Enter e salva como WAV 16 kHz mono."""
    blocos = queue.Queue()
    input("🎙  Aperte Enter para começar a gravar...")
    with sd.InputStream(samplerate=TAXA, channels=1, dtype="int16",
                        callback=lambda dados, *_: blocos.put(dados.copy())):
        input("🔴 Gravando... aperte Enter para parar.")
    audio = np.concatenate(list(blocos.queue))

    caminho = pathlib.Path(tempfile.gettempdir()) / "ai-lab-gravacao.wav"
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # int16 = 2 bytes
        w.setframerate(TAXA)
        w.writeframes(audio.tobytes())
    print(f"   {len(audio) / TAXA:.1f}s de áudio gravados")
    return caminho


def achar_whisper_cli() -> pathlib.Path:
    """Onde o whisper-cli fica: compilado (Mac/Linux) ou baixado pronto (Windows)."""
    candidatos = [
        WHISPER / "build" / "bin" / "whisper-cli",      # compilado com cmake
        WHISPER / "Release" / "whisper-cli.exe",        # zip oficial do Windows
        WHISPER / "build" / "bin" / "Release" / "whisper-cli.exe",  # compilado no Windows
    ]
    for c in candidatos:
        if c.exists():
            return c
    raise SystemExit(f"whisper-cli não encontrado em {WHISPER}. Fez o Passo 1 do README?")


def transcrever(caminho: pathlib.Path) -> str:
    inicio = time.time()
    r = subprocess.run(
        [achar_whisper_cli(),
         "-m", WHISPER / "models" / f"ggml-{args.modelo_whisper}.bin",
         "-f", caminho, "-l", "pt", "-t", "4", "--no-timestamps"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    texto = " ".join(r.stdout.split())
    print(f"📝 ({time.time() - inicio:.1f}s, whisper {args.modelo_whisper}) {texto}")
    return texto


audio = pathlib.Path(args.arquivo) if args.arquivo else gravar()
pergunta = transcrever(audio)

print(f"\n💬 ({args.modelo_llm}) ", end="")
for pedaco in ollama.chat(
    model=args.modelo_llm,
    messages=[
        {"role": "system", "content": "Responda em português, em no máximo 3 frases. "
                                      "A pergunta veio de uma transcrição de voz e pode ter erros."},
        {"role": "user", "content": pergunta},
    ],
    stream=True,
):
    print(pedaco.message.content, end="", flush=True)
print()
