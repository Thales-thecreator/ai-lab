#!/bin/zsh
# Compara o MESMO modelo (Qwen3 1.7B) em 4 níveis de quantização:
# tamanho do arquivo, velocidade (llama-bench) e uma resposta de exemplo.
#
# Uso:  zsh modulos/06-por-dentro/03_quantizacao.sh
set -e

LAB="$HOME/ai-lab"
MODELOS="$LAB/modelos"
HF="https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main"
QUANTS=(Q2_K Q4_K_M Q8_0 BF16)   # do mais "comprimido" ao original (16 bits)

mkdir -p "$MODELOS"

echo "── 1) Baixando (só na primeira vez) ──"
for q in $QUANTS; do
  arq="$MODELOS/Qwen3-1.7B-$q.gguf"
  [[ -f "$arq" ]] || curl -L --progress-bar -o "$arq" "$HF/Qwen3-1.7B-$q.gguf"
done

echo "\n── 2) Tamanho em disco ──"
ls -lh "$MODELOS"/Qwen3-1.7B-*.gguf | awk '{print $5, $9}'

echo "\n── 3) Velocidade (pp = ler o prompt, tg = gerar texto; em tokens/s) ──"
for q in $QUANTS; do
  llama-bench -m "$MODELOS/Qwen3-1.7B-$q.gguf" -p 128 -n 64 -t 4 -r 2 2>/dev/null | grep -E "qwen|model"
done

echo "\n── 4) Mesma pergunta, mesma semente, temperature 0 ──"
PERGUNTA="Explique em 3 frases por que o céu é azul."
for q in $QUANTS; do
  echo "\n### $q"
  llama-completion -m "$MODELOS/Qwen3-1.7B-$q.gguf" -t 4 --temp 0 -n 150 -no-cnv \
    -p "<|im_start|>user
$PERGUNTA /no_think<|im_end|>
<|im_start|>assistant
" 2>/dev/null
done
