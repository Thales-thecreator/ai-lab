"""Treina o MiniGPT do zero, na CPU, caractere por caractere.

Uso:
  uv run modulos/07-mini-gpt/treinar.py                    # Shakespeare (inglês)
  uv run modulos/07-mini-gpt/treinar.py --dados machado     # Machado de Assis (português)
  uv run modulos/07-mini-gpt/treinar.py --passos 500        # treino rápido, para testar
"""

import argparse
import pathlib
import time
import urllib.request

import torch

from modelo import Config, MiniGPT

FONTES = {
    "shakespeare": "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",
    "machado": "https://www.gutenberg.org/cache/epub/55752/pg55752.txt",  # Dom Casmurro
}

p = argparse.ArgumentParser()
p.add_argument("--dados", choices=FONTES, default="shakespeare")
p.add_argument("--passos", type=int, default=3000)
args = p.parse_args()

AQUI = pathlib.Path(__file__).parent
torch.manual_seed(42)
torch.set_num_threads(4)  # 4 núcleos físicos

# ── 1) Dados ────────────────────────────────────────────────────────────────
arquivo = AQUI / "dados" / f"{args.dados}.txt"
if not arquivo.exists():
    arquivo.parent.mkdir(exist_ok=True)
    print(f"Baixando {args.dados}...")
    urllib.request.urlretrieve(FONTES[args.dados], arquivo)
texto = arquivo.read_text(encoding="utf-8")
print(f"Texto: {len(texto):,} caracteres")

# ── 2) Tokenizador: o mais simples possível, 1 caractere = 1 token ───────────
vocab = sorted(set(texto))
stoi = {ch: i for i, ch in enumerate(vocab)}
dados = torch.tensor([stoi[ch] for ch in texto], dtype=torch.long)
print(f"Vocabulário: {len(vocab)} caracteres diferentes → {''.join(vocab)!r}")

corte = int(0.9 * len(dados))
treino, validacao = dados[:corte], dados[corte:]  # 10% guardado para checar se generaliza

# ── 3) Modelo ───────────────────────────────────────────────────────────────
config = Config(vocab_size=len(vocab))
modelo = MiniGPT(config)
otimizador = torch.optim.AdamW(modelo.parameters(), lr=1e-3)
print(f"Parâmetros: {sum(p.numel() for p in modelo.parameters()):,}\n")

LOTE = 32


def lote_aleatorio(fonte):
    """Pega 32 trechos aleatórios; o alvo é o mesmo trecho deslocado 1 caractere."""
    i = torch.randint(len(fonte) - config.contexto - 1, (LOTE,))
    x = torch.stack([fonte[j:j + config.contexto] for j in i])
    y = torch.stack([fonte[j + 1:j + config.contexto + 1] for j in i])
    return x, y


@torch.no_grad()
def avaliar():
    modelo.eval()
    perdas = {nome: torch.stack([modelo(*lote_aleatorio(f))[1] for _ in range(20)]).mean().item()
              for nome, f in [("treino", treino), ("validação", validacao)]}
    modelo.train()
    return perdas


def amostra(n=150):
    modelo.eval()
    ids = torch.tensor([[stoi["\n"]]])
    s = "".join(vocab[t] for t in modelo.gerar(ids, n, temperature=0.8))
    modelo.train()
    return s


# ── 4) Treino ───────────────────────────────────────────────────────────────
# Perda inicial esperada ≈ ln(vocabulário) ≈ 4,2: o modelo chuta ao acaso.
inicio = time.time()
for passo in range(args.passos + 1):
    if passo % 500 == 0:
        p = avaliar()
        print(f"── passo {passo:>5} │ perda treino {p['treino']:.3f} │ validação {p['validação']:.3f}"
              f" │ {time.time() - inicio:.0f}s")
        print(amostra().replace("\n", "\n   ") + "\n")

    x, y = lote_aleatorio(treino)
    _, perda = modelo(x, y)
    otimizador.zero_grad()
    perda.backward()   # calcula como cada parâmetro deveria mudar para errar menos
    otimizador.step()  # muda um pouquinho

torch.save({"modelo": modelo.state_dict(), "config": config, "vocab": vocab},
           AQUI / f"mini-gpt-{args.dados}.pt")
print(f"✓ Salvo em mini-gpt-{args.dados}.pt ({time.time() - inicio:.0f}s no total)")
