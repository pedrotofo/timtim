#!/usr/bin/env python3
"""Acha o tempo exato de palavras na transcrição, para sincronizar o motion com a fala.

    python3 achar_palavras.py decup/transcricao.json Ceará Pernambuco Bahia [--de 10 --ate 15]

Imprime cada ocorrência com início, fim e a frase em volta. Ignora acentos, maiúsculas e
pontuação; aceita trechos de mais de uma palavra entre aspas ("São Paulo").
"""
import argparse, json, unicodedata, re


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return re.sub(r"[^\w\s]", "", "".join(c for c in t if unicodedata.category(c) != "Mn")).strip()


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("transcricao")
ap.add_argument("termos", nargs="+")
ap.add_argument("--de", type=float, default=0)
ap.add_argument("--ate", type=float, default=1e9)
a = ap.parse_args()

dados = json.load(open(a.transcricao, encoding="utf-8"))
palavras = [(norm(w["p"]), w, s) for s in dados["segmentos"] for w in s["palavras"]]
for termo in a.termos:
    alvo = norm(termo).split()
    achou = False
    for i in range(len(palavras) - len(alvo) + 1):
        if [p[0] for p in palavras[i:i + len(alvo)]] == alvo:
            ini, fim = palavras[i][1]["inicio"], palavras[i + len(alvo) - 1][1]["fim"]
            if a.de <= ini <= a.ate:
                achou = True
                print(f'{termo:<20} {ini:8.2f} -> {fim:8.2f}   "{palavras[i][2]["texto"]}"')
    if not achou:
        print(f"{termo:<20} não encontrado (confira a grafia na transcrição)")
