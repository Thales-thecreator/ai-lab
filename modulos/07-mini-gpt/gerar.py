"""Gera texto com o MiniGPT que você treinou.

Uso:  uv run modulos/07-mini-gpt/gerar.py [shakespeare|machado] [--temp 0.8] [--n 500] [--inicio "ROMEO:"]
"""

import argparse
import pathlib

import torch

from modelo import MiniGPT

p = argparse.ArgumentParser()
p.add_argument("dados", nargs="?", default="shakespeare")
p.add_argument("--temp", type=float, default=0.8)
p.add_argument("--n", type=int, default=500)
p.add_argument("--inicio", default="\n")
args = p.parse_args()

ckpt = torch.load(pathlib.Path(__file__).parent / f"mini-gpt-{args.dados}.pt", weights_only=False)
vocab = ckpt["vocab"]
stoi = {ch: i for i, ch in enumerate(vocab)}
modelo = MiniGPT(ckpt["config"])
modelo.load_state_dict(ckpt["modelo"])
modelo.eval()

ids = torch.tensor([[stoi[ch] for ch in args.inicio if ch in stoi]])
print(args.inicio, end="")
for t in modelo.gerar(ids, args.n, temperature=args.temp):
    print(vocab[t], end="", flush=True)
print()
