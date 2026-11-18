"""Busca e baixa imagens do Wikimedia Commons com calma (o Commons responde 429 quando há pressa).

python3 commons.py busca "Hokusai Great Wave"            -> lista arquivos
python3 commons.py info "File:Nome.jpg" ...               -> licença, autor, data, tamanho
python3 commons.py baixa "File:Nome.jpg" destino.jpg [largura]"""
import json, sys, time, urllib.parse, urllib.request
UA = {'User-Agent': 'LivroPesquisa/1.0 (pesquisa editorial)'}
API = 'https://commons.wikimedia.org/w/api.php?'

def pega(url, binario=False):
    for t in range(10):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                dado = r.read(); time.sleep(1.5)
                return dado if binario else json.loads(dado)
        except urllib.error.HTTPError as e:
            espera = int(e.headers.get('Retry-After') or 0) or (5 + 10 * t)
            print(f'  {e.code}, esperando {espera}s', file=sys.stderr); time.sleep(min(espera, 90))
        except Exception as e:
            print('  erro', repr(e)[:80], file=sys.stderr)
            if 'Tunnel connection failed: 403' in repr(e): raise SystemExit('host bloqueado na rede: ' + url.split('/')[2])
            time.sleep(5 + 5 * t)
    raise SystemExit('desisti: ' + url)

def busca(q, n=8):
    d = pega(API + urllib.parse.urlencode({'action': 'query', 'list': 'search', 'srnamespace': 6, 'srsearch': q, 'srlimit': n, 'format': 'json'}))
    return [x['title'] for x in d['query']['search']]

def info(titulos, largura=None):
    p = {'action': 'query', 'titles': '|'.join(titulos), 'prop': 'imageinfo', 'iiprop': 'url|size|extmetadata', 'format': 'json'}
    if largura: p['iiurlwidth'] = largura
    d = pega(API + urllib.parse.urlencode(p)); out = {}
    for pg in d['query']['pages'].values():
        ii = (pg.get('imageinfo') or [{}])[0]; md = ii.get('extmetadata', {})
        g = lambda k: (md.get(k, {}).get('value') or '')
        out[pg['title']] = {'url': ii.get('thumburl') or ii.get('url'), 'original': ii.get('url'), 'w': ii.get('width'), 'h': ii.get('height'),
                            'licenca': g('LicenseShortName'), 'artista': g('Artist'), 'data': g('DateTimeOriginal'), 'credito': g('Credit')}
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'busca':
        for t in busca(sys.argv[2]): print(t)
    elif cmd == 'info':
        for t, v in info(sys.argv[2:]).items(): print(t, '|', v['w'], 'x', v['h'], '|', v['licenca'], '|', v['data'][:40])
    elif cmd == 'baixa':
        larg = int(sys.argv[4]) if len(sys.argv) > 4 else 2400
        v = info([sys.argv[2]], larg)[sys.argv[2]]
        # o Commons só serve miniaturas em larguras padrão, e o original costuma voltar 429
        PADRAO = [320, 640, 800, 1024, 1280, 1920, 2560, 3840]
        larg = max([p for p in PADRAO if p <= larg] or [320])
        if (v['w'] or 0) <= larg: url = v['original'].split('?')[0]
        else:
            orig = v['original'].split('?')[0]; nome = orig.rsplit('/', 1)[1]
            url = orig.replace('/wikipedia/commons/', '/wikipedia/commons/thumb/') + f'/{larg}px-{nome}'
        import subprocess   # o urllib trava no servidor de imagens; o curl não
        for t in range(6):
            r = subprocess.run(['curl', '-sS', '-m', '90', '-o', sys.argv[3], '-w', '%{http_code}', '-A', UA['User-Agent'], url], capture_output=True, text=True)
            if r.stdout == '200': break
            print('  ', r.stdout, r.stderr[:80], file=sys.stderr); time.sleep(10 + 10 * t)
        print('ok' if r.stdout == '200' else 'FALHOU', sys.argv[3], v['licenca'])
