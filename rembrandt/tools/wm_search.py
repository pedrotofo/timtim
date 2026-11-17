"""Busca obras no Wikimedia Commons pela página de busca (a API está limitada nesta rede) e lista os arquivos.
Uso: python3 wm_search.py consultas.json saida.json"""
import json, sys, time, re, html, urllib.request, urllib.parse
UA = 'drawing-book-builder/1.0 (educational use)'
def get(url):
    for k in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40).read().decode('utf-8', 'replace')
        except Exception:
            time.sleep(4 * (k + 1))
    return ''
Q = json.load(open(sys.argv[1]))
out = json.load(open(sys.argv[2])) if len(sys.argv) > 3 else {}
for key, q in Q.items():
    if key in out and out[key]:
        continue
    t = get('https://commons.wikimedia.org/w/index.php?' + urllib.parse.urlencode({'search': q, 'title': 'Special:MediaSearch', 'type': 'image'}))
    seen = []
    for m in re.findall(r'File:([^"&<>\\]+?\.(?:jpe?g|png|tiff?))', html.unescape(t), re.I):
        n = urllib.parse.unquote(m).replace(' ', '_')
        if n not in seen:
            seen.append(n)
    out[key] = seen[:6]
    print(key)
    for n in seen[:4]:
        print('    ', n[:120])
    time.sleep(1.2)
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
