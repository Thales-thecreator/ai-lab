"""Baixa alguns artigos da Wikipédia em português (texto puro) para o RAG."""

import json
import pathlib
import urllib.parse
import urllib.request

ARTIGOS = [
    "Inteligência artificial",
    "Rede neural artificial",
    "Modelo de linguagem grande",
    "Transformer (aprendizado profundo)",
    "Fotossíntese",
    "Revolução Industrial",
    "Sistema Solar",
    "Café",
]

PASTA = pathlib.Path(__file__).parent / "dados" / "publicos"
PASTA.mkdir(parents=True, exist_ok=True)

for titulo in ARTIGOS:
    params = urllib.parse.urlencode({
        "action": "query", "prop": "extracts", "explaintext": 1,
        "redirects": 1, "format": "json", "titles": titulo,
    })
    req = urllib.request.Request(
        f"https://pt.wikipedia.org/w/api.php?{params}",
        headers={"User-Agent": "ai-lab-estudo/0.1"},
    )
    with urllib.request.urlopen(req) as r:
        paginas = json.loads(r.read())["query"]["pages"]
    texto = next(iter(paginas.values())).get("extract", "")
    if not texto:
        print(f"⚠️  não encontrado: {titulo}")
        continue
    arquivo = PASTA / f"{titulo.replace(' ', '_').replace('/', '-')}.txt"
    arquivo.write_text(f"{titulo}\n\n{texto}", encoding="utf-8")
    print(f"✓ {arquivo.name} ({len(texto):,} caracteres)")
