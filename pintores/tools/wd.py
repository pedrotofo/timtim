"""Métricas do Wikidata para o ranking: em quantas Wikipédias o pintor tem artigo (alcance),
quantos itens dizem 'influenciado por' ele (influência) e quantas obras dele estão catalogadas (presença em acervos)."""
import json, time, urllib.parse, urllib.request, sys
UA = {'User-Agent': 'LivroPesquisa/1.0 (pesquisa editorial)'}
POOL = """Leonardo_da_Vinci|Itália|Europa
Michelangelo|Itália|Europa
Raphael|Itália|Europa
Titian|Itália|Europa
Albrecht_Dürer|Alemanha|Europa
Rembrandt|Holanda|Europa
Giotto|Itália|Europa
Caravaggio|Itália|Europa
Sandro_Botticelli|Itália|Europa
Diego_Velázquez|Espanha|Europa
Francisco_Goya|Espanha|Europa
Peter_Paul_Rubens|Flandres|Europa
Jan_van_Eyck|Flandres|Europa
Hieronymus_Bosch|Holanda|Europa
Pieter_Bruegel_the_Elder|Flandres|Europa
El_Greco|Grécia/Espanha|Europa
Johannes_Vermeer|Holanda|Europa
Artemisia_Gentileschi|Itália|Europa
Hans_Holbein_the_Younger|Alemanha|Europa
Masaccio|Itália|Europa
Piero_della_Francesca|Itália|Europa
Andrea_Mantegna|Itália|Europa
Tintoretto|Itália|Europa
Nicolas_Poussin|França|Europa
Anthony_van_Dyck|Flandres|Europa
Frans_Hals|Holanda|Europa
Jacques-Louis_David|França|Europa
Jean-Auguste-Dominique_Ingres|França|Europa
Eugène_Delacroix|França|Europa
J._M._W._Turner|Inglaterra|Europa
John_Constable|Inglaterra|Europa
Caspar_David_Friedrich|Alemanha|Europa
Gustave_Courbet|França|Europa
Édouard_Manet|França|Europa
Claude_Monet|França|Europa
Pierre-Auguste_Renoir|França|Europa
Edgar_Degas|França|Europa
Camille_Pissarro|França|Europa
Berthe_Morisot|França|Europa
Mary_Cassatt|EUA|América do Norte
Paul_Cézanne|França|Europa
Paul_Gauguin|França|Europa
Vincent_van_Gogh|Holanda|Europa
Georges_Seurat|França|Europa
Henri_de_Toulouse-Lautrec|França|Europa
Henri_Rousseau|França|Europa
Gustav_Klimt|Áustria|Europa
Egon_Schiele|Áustria|Europa
Edvard_Munch|Noruega|Europa
Henri_Matisse|França|Europa
Pablo_Picasso|Espanha|Europa
Georges_Braque|França|Europa
Wassily_Kandinsky|Rússia|Europa
Piet_Mondrian|Holanda|Europa
Kazimir_Malevich|Rússia/Ucrânia|Europa
Marc_Chagall|Rússia/França|Europa
Amedeo_Modigliani|Itália|Europa
Paul_Klee|Suíça/Alemanha|Europa
Joan_Miró|Espanha|Europa
Salvador_Dalí|Espanha|Europa
René_Magritte|Bélgica|Europa
Edward_Hopper|EUA|América do Norte
Georgia_O'Keeffe|EUA|América do Norte
Jackson_Pollock|EUA|América do Norte
Mark_Rothko|EUA|América do Norte
Andy_Warhol|EUA|América do Norte
Roy_Lichtenstein|EUA|América do Norte
Jean-Michel_Basquiat|EUA|América do Norte
Francis_Bacon_(artist)|Irlanda/Inglaterra|Europa
Lucian_Freud|Inglaterra|Europa
Alphonse_Mucha|Tchéquia|Europa
Ivan_Aivazovsky|Rússia/Armênia|Europa
Ilya_Repin|Rússia/Ucrânia|Europa
John_Singer_Sargent|EUA|América do Norte
Winslow_Homer|EUA|América do Norte
Diego_Rivera|México|América Latina
Frida_Kahlo|México|América Latina
Tarsila_do_Amaral|Brasil|América Latina
Candido_Portinari|Brasil|América Latina
José_Clemente_Orozco|México|América Latina
David_Alfaro_Siqueiros|México|América Latina
Rufino_Tamayo|México|América Latina
Fernando_Botero|Colômbia|América Latina
Joaquín_Torres_García|Uruguai|América Latina
Wifredo_Lam|Cuba|América Latina
Juan_Luna|Filipinas|Ásia
Hokusai|Japão|Ásia
Hiroshige|Japão|Ásia
Sesshū_Tōyō|Japão|Ásia
Utamaro|Japão|Ásia
Ogata_Kōrin|Japão|Ásia
Itō_Jakuchū|Japão|Ásia
Gu_Kaizhi|China|Ásia
Fan_Kuan|China|Ásia
Wu_Daozi|China|Ásia
Qi_Baishi|China|Ásia
Xu_Beihong|China|Ásia
Chang_Dai-chien|China|Ásia
Raja_Ravi_Varma|Índia|Ásia
Amrita_Sher-Gil|Índia|Ásia
Abanindranath_Tagore|Índia|Ásia
Kamāl_ud-Dīn_Behzād|Pérsia|Oriente Médio
Reza_Abbasi|Pérsia|Oriente Médio
Osman_Hamdi_Bey|Império Otomano|Oriente Médio
Ben_Enwonwu|Nigéria|África
Irma_Stern|África do Sul|África
Gerard_Sekoto|África do Sul|África
Albert_Namatjira|Austrália|Oceania
Emily_Kame_Kngwarreye|Austrália|Oceania"""
def get(url):
    for t in range(9):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: return json.load(r)
        except Exception as e:
            print('tentativa', t, repr(e)[:120], file=sys.stderr); time.sleep(3 + 5 * t)
    return None
API = 'https://www.wikidata.org/w/api.php?'
rows = [l.split('|') for l in POOL.splitlines()]
out = {}
for i in range(0, len(rows), 8):
    lote = rows[i:i + 8]
    d = get(API + urllib.parse.urlencode({'action': 'wbgetentities', 'sites': 'enwiki', 'titles': '|'.join(r[0] for r in lote),
                                          'props': 'sitelinks|claims|labels', 'languages': 'pt|en', 'format': 'json'}))
    porTitulo = {}
    for q, e in d['entities'].items():
        if 'sitelinks' in e: porTitulo[e['sitelinks']['enwiki']['title'].replace(' ', '_')] = (q, e)
    for t, pais, reg in lote:
        if t not in porTitulo: print('NÃO ACHEI', t, file=sys.stderr); continue
        q, e = porTitulo[t]
        sl = [k for k in e['sitelinks'] if k.endswith('wiki') and k not in ('commonswiki', 'specieswiki', 'wikidatawiki', 'metawiki', 'mediawikiwiki', 'sourceswiki', 'outreachwiki', 'incubatorwiki')]
        def ano(p):
            try: return int(e['claims'][p][0]['mainsnak']['datavalue']['value']['time'][1:5])
            except Exception: return None
        lab = e.get('labels', {}).get('pt', e.get('labels', {}).get('en', {})).get('value', t)
        out[t] = {'qid': q, 'nome': lab, 'pais': pais, 'regiao': reg, 'nasc': ano('P569'), 'morte': ano('P570'), 'wikis': len(sl),
                  'langs': {k[:-4]: e['sitelinks'][k]['title'] for k in sl}}
import os
cache = json.load(open('busca.json')) if os.path.exists('busca.json') else {}
for t, v in out.items():
    for prop, chave in (('P737', 'influenciou'), ('P170', 'obras')):
        ck = f'{prop}={v["qid"]}'
        if ck in cache: v[chave] = cache[ck]; continue
        d = None
        for t_ in range(8):
            d = get(API + urllib.parse.urlencode({'action': 'query', 'list': 'search', 'srsearch': f'haswbstatement:{prop}={v["qid"]}', 'srlimit': 1, 'srinfo': 'totalhits', 'format': 'json'}))
            if d and 'query' in d: break
            time.sleep(4 + 4 * t_)
        v[chave] = d['query']['searchinfo']['totalhits'] if d and 'query' in d else None
        if v[chave] is not None: cache[ck] = v[chave]; json.dump(cache, open('busca.json', 'w'))
        time.sleep(1.0)
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
print(len(out), 'pintores')
