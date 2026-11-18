"""Ranking dos 50 pintores: combina alcance mundial (Wikipédias), influência (Wikidata 'influenciado por'),
presença em acervos (obras catalogadas) e menções na mídia especializada e no cânone."""
import json, math, sys
d = json.load(open(sys.argv[1]))

# Menções nas fontes consultadas (cada fonte vale 1 ponto; o topo de cada lista vale mais)
MIDIA = {
    # Artnet, 10 mais buscados no banco de preços em 2025 (só pintores mortos)
    'Pablo_Picasso': 3, 'Andy_Warhol': 2.5, 'Marc_Chagall': 2, 'Roy_Lichtenstein': 1, 'Joan_Miró': 1, 'Jean-Michel_Basquiat': 1,
    # Ken Bromley, artista mais buscado no Google por país (2020)
    'Leonardo_da_Vinci': 3, 'Frida_Kahlo': 2.5, 'Vincent_van_Gogh': 2.5, 'Artemisia_Gentileschi': 1.5, 'Diego_Velázquez': 1,
    # Prometheus (arquivo de imagens das universidades alemãs), mais buscados em 2025
    'Caspar_David_Friedrich': 1.5,
    # Charles Murray, Human Accomplishment (163 histórias da arte): os 10 primeiros pintores
    'Michelangelo': 3, 'Raphael': 2, 'Titian': 1.5, 'Albrecht_Dürer': 1.5, 'Rembrandt': 1.5, 'Giotto': 1.5, 'Paul_Cézanne': 1,
    # Pantheon (MIT): mais famosos entre os pintores; Monet 9º
    'Claude_Monet': 1.5,
    # Artprice 2025: maior faturamento em leilão (Klimt) e chinês mais vendido (Zhang Daqian)
    'Gustav_Klimt': 1, 'Chang_Dai-chien': .5,
    # Rijksmuseum 2023: a exposição Vermeer vendeu 650 mil ingressos, recorde do museu
    'Johannes_Vermeer': 1.5,
}
# somas para quem aparece em mais de uma lista
for k, extra in (('Pablo_Picasso', 3), ('Vincent_van_Gogh', 1.5), ('Michelangelo', 1), ('Leonardo_da_Vinci', 1.5)):
    MIDIA[k] = MIDIA.get(k, 0) + extra

def pct(chave, f=lambda x: x):
    vals = sorted(f(v[chave] or 0) for v in d.values())
    return {k: sum(x <= f(v[chave] or 0) for x in vals) / len(vals) for k, v in d.items()}
alc = pct('wikis'); inf = pct('influenciou', lambda x: math.log1p(x)); acv = pct('obras', lambda x: math.log1p(x))
mmax = max(MIDIA.values())
for k, v in d.items():
    v['midia'] = MIDIA.get(k, 0)
    # alcance mundial 50 %, mídia e cânone 30 %, influência sobre outros artistas 20 %
    # (o número de obras catalogadas ficou fora: pune quem pintou pouco, como Vermeer e Caravaggio)
    v['nota'] = round(100 * (.50 * alc[k] + .20 * inf[k] + .30 * (MIDIA.get(k, 0) / mmax) ** .5), 1)
    m = v['morte'] or 0
    if m <= 1955: v['direito'] = 'livre'
    else: v['direito'] = f'protegido no Brasil até {m + 70}'
    if v['pais'] == 'México' and m > 1925: v['direito'] += '; México: 100 anos' if m > 1955 else '; protegido no México (100 anos)'
    if 1931 <= m <= 1955: v['direito'] += ' (EUA: só obras de antes de 1931 com segurança)'
r = sorted(d.items(), key=lambda kv: -kv[1]['nota'])
json.dump(r, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
for i, (k, v) in enumerate(r, 1):
    print(f"{i:3d} {v['nota']:5.1f} {v['nome'][:28]:28s} {v['regiao'][:12]:12s} {v['nasc']}–{v['morte']} wikis={v['wikis']:3d} infl={v['influenciou'] if v['influenciou'] is not None else '?':>3} obras={v['obras'] if v['obras'] is not None else '?':>5} mídia={v['midia']:<4} {v['direito']}")
