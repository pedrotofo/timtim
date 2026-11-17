"""Lê a página de cada arquivo no Commons e extrai data, técnica, dimensões e acervo para tools/fichas_raw.json."""
import json, re, time, html, subprocess, urllib.parse
UA = 'drawing-book-builder/1.0 (educational use)'
S = json.load(open('tools/selecao.json'))
out = {}
def clean(x):
    x = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', x, flags=re.S)
    x = re.sub(r'<[^>]+>', ' ', x); x = html.unescape(x)
    return re.sub(r'\s+', ' ', x).strip()
for k, f in S.items():
    u = 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(f)
    t = subprocess.run(['curl', '-s', '-m', '40', '-A', UA, u], capture_output=True, text=True).stdout
    d = {}
    for lab in ['Title', 'Object type', 'Date', 'Medium', 'Dimensions', 'Collection', 'Current location', 'Accession number', 'Institution', 'Artist', 'Author']:
        m = re.search(r'id="fileinfotpl_[a-z_]*"[^>]*>\s*' + lab + r'.*?</td>\s*<td[^>]*>(.*?)</td>', t, re.S | re.I)
        if not m:
            m = re.search(r'>\s*' + lab + r'\s*</t[dh]>\s*<td[^>]*>(.*?)</td>', t, re.S | re.I)
        if m:
            d[lab] = clean(m.group(1))[:220]
    out[k] = d
    print(k, '|', d.get('Date', ''), '|', d.get('Collection') or d.get('Current location') or d.get('Institution', ''), flush=True)
    time.sleep(1.2)
json.dump(out, open('tools/fichas_raw.json', 'w'), ensure_ascii=False, indent=1)
