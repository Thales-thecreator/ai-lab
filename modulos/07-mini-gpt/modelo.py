"""Um GPT minúsculo, do zero, em ~80 linhas de PyTorch.

É a MESMA arquitetura dos modelos grandes (Transformer decoder), só que pequena:
os modelos do Ollama têm bilhões de parâmetros; este tem ~0,8 milhão.
Baseado no "Let's build GPT" de Andrej Karpathy.
"""

from dataclasses import dataclass

import torch
import torch.nn as nn
from torch.nn import functional as F


@dataclass
class Config:
    vocab_size: int = 65    # quantos tokens diferentes existem (aqui: caracteres)
    contexto: int = 128     # quantos tokens o modelo enxerga para trás
    n_embd: int = 128       # tamanho do vetor que representa cada token
    n_heads: int = 4        # "cabeças" de atenção em paralelo
    n_camadas: int = 4      # blocos Transformer empilhados
    dropout: float = 0.1


class AutoAtencao(nn.Module):
    """Cada token olha para os anteriores e decide em quais prestar atenção."""

    def __init__(self, c: Config):
        super().__init__()
        self.c = c
        self.qkv = nn.Linear(c.n_embd, 3 * c.n_embd)  # query, key, value de uma vez
        self.saida = nn.Linear(c.n_embd, c.n_embd)
        self.dropout = nn.Dropout(c.dropout)

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        # separa em cabeças: (B, heads, T, C/heads)
        q, k, v = (t.view(B, T, self.c.n_heads, C // self.c.n_heads).transpose(1, 2) for t in (q, k, v))
        # is_causal=True: o token N não pode olhar para N+1 (senão "colaria" a resposta)
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True,
                                           dropout_p=self.c.dropout if self.training else 0)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.dropout(self.saida(y))


class Bloco(nn.Module):
    """Um bloco Transformer: atenção (comunicação entre tokens) + MLP (processamento de cada token)."""

    def __init__(self, c: Config):
        super().__init__()
        self.ln1 = nn.LayerNorm(c.n_embd)
        self.atencao = AutoAtencao(c)
        self.ln2 = nn.LayerNorm(c.n_embd)
        self.mlp = nn.Sequential(
            nn.Linear(c.n_embd, 4 * c.n_embd), nn.GELU(),
            nn.Linear(4 * c.n_embd, c.n_embd), nn.Dropout(c.dropout),
        )

    def forward(self, x):
        x = x + self.atencao(self.ln1(x))  # "x +" = conexão residual
        x = x + self.mlp(self.ln2(x))
        return x


class MiniGPT(nn.Module):
    def __init__(self, c: Config):
        super().__init__()
        self.c = c
        self.emb_token = nn.Embedding(c.vocab_size, c.n_embd)   # ID do token → vetor
        self.emb_posicao = nn.Embedding(c.contexto, c.n_embd)   # posição → vetor
        self.blocos = nn.Sequential(*[Bloco(c) for _ in range(c.n_camadas)])
        self.ln_final = nn.LayerNorm(c.n_embd)
        self.cabeca = nn.Linear(c.n_embd, c.vocab_size)         # vetor → nota para cada token

    def forward(self, ids, alvos=None):
        B, T = ids.shape
        x = self.emb_token(ids) + self.emb_posicao(torch.arange(T))
        logits = self.cabeca(self.ln_final(self.blocos(x)))
        perda = None
        if alvos is not None:
            # quão "surpreso" o modelo ficou com o próximo caractere real
            perda = F.cross_entropy(logits.view(-1, logits.size(-1)), alvos.view(-1))
        return logits, perda

    @torch.no_grad()
    def gerar(self, ids, n_tokens, temperature=1.0):
        for _ in range(n_tokens):
            logits, _ = self(ids[:, -self.c.contexto:])
            probs = F.softmax(logits[:, -1, :] / temperature, dim=-1)  # notas → probabilidades
            proximo = torch.multinomial(probs, num_samples=1)           # sorteio
            ids = torch.cat([ids, proximo], dim=1)
            yield proximo.item()
