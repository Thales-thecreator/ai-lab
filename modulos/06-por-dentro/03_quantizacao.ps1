# Compara o MESMO modelo (Qwen3 1.7B) em 4 níveis de quantização:
# tamanho do arquivo, velocidade (llama-bench) e uma resposta de exemplo.
# Versão Windows (PowerShell) do 03_quantizacao.sh
#
# Uso:  powershell -ExecutionPolicy Bypass -File modulos\06-por-dentro\03_quantizacao.ps1
$ErrorActionPreference = "Stop"

$Modelos = "$HOME\ai-lab\modelos"
$HF = "https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main"
$Quants = @("Q2_K", "Q4_K_M", "Q8_0", "BF16")   # do mais "comprimido" ao original (16 bits)
$Threads = [Math]::Max(1, [Environment]::ProcessorCount / 2)  # ≈ núcleos físicos

New-Item -ItemType Directory -Force -Path $Modelos | Out-Null

Write-Host "── 1) Baixando (só na primeira vez) ──"
foreach ($q in $Quants) {
    $arq = "$Modelos\Qwen3-1.7B-$q.gguf"
    if (-not (Test-Path $arq)) { curl.exe -L --progress-bar -o $arq "$HF/Qwen3-1.7B-$q.gguf" }
}

Write-Host "`n── 2) Tamanho em disco ──"
Get-ChildItem "$Modelos\Qwen3-1.7B-*.gguf" |
    ForEach-Object { "{0,8:N2} GB  {1}" -f ($_.Length / 1GB), $_.Name }

Write-Host "`n── 3) Velocidade (pp = ler o prompt, tg = gerar texto; em tokens/s) ──"
foreach ($q in $Quants) {
    llama-bench -m "$Modelos\Qwen3-1.7B-$q.gguf" -p 128 -n 64 -t $Threads -r 2 2>$null |
        Select-String -Pattern "qwen|model"
}

Write-Host "`n── 4) Mesma pergunta, mesma semente, temperature 0 ──"
$Pergunta = "Explique em 3 frases por que o céu é azul."
$Prompt = "<|im_start|>user`n$Pergunta /no_think<|im_end|>`n<|im_start|>assistant`n"
foreach ($q in $Quants) {
    Write-Host "`n### $q"
    llama-completion -m "$Modelos\Qwen3-1.7B-$q.gguf" -t $Threads --temp 0 -n 150 -no-cnv -p $Prompt 2>$null
}
