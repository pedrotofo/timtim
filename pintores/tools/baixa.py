#!/usr/bin/env python3
"""Baixa do Wikimedia Commons as imagens listadas no campo "imagens" de cada artistas/NN-chave.json.

python3 tools/baixa.py 19 23 41     -> só esses pintores
python3 tools/baixa.py              -> todos

Grava em obras/<chave>/<arquivo> (fora do git) e registra licença, autor e endereço em pesquisa/creditos/<chave>.json,
que o livro usa nos créditos das imagens. Só aceita imagem em domínio público (Public domain, PD-*, CC0)."""
import glob, json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commons

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRED = os.path.join(ROOT, 'pesquisa', 'creditos')   # um arquivo por pintor: agentes podem baixar em paralelo
LIVRE = ('public domain', 'pd', 'cc0', 'cc-zero', 'no restrictions')

def baixa_um(url_orig, larg, destino):
    """Miniatura numa largura padrão do Commons, via curl (o original costuma voltar 429)."""
    nome = url_orig.rsplit('/', 1)[1]
    url = url_orig.replace('/wikipedia/commons/', '/wikipedia/commons/thumb/') + f'/{larg}px-{nome}'
    for t in range(5):
        r = subprocess.run(['curl', '-sS', '-m', '90', '-o', destino, '-w', '%{http_code}', '-A', commons.UA['User-Agent'], url], capture_output=True, text=True)
        if r.stdout == '200': return True
        if r.stdout in ('404', '400'): return False
        time.sleep(8 + 8 * t)
    return False

def main():
    alvo = set(int(x) for x in sys.argv[1:])
    os.makedirs(CRED, exist_ok=True)
    erros = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'artistas', '*.json'))):
        pos = int(os.path.basename(f).split('-')[0])
        if alvo and pos not in alvo: continue
        a = json.load(open(f)); ch = a['chave']; ims = a.get('imagens', {})
        cf = os.path.join(CRED, ch + '.json'); cred = json.load(open(cf)) if os.path.exists(cf) else {}
        def tem(n):
            p = os.path.join(ROOT, 'obras', ch, n)
            if not os.path.exists(p): return False
            try:
                from PIL import Image; Image.open(p).verify(); return True
            except Exception:
                os.remove(p); return False
        falta = {n: t for n, t in ims.items() if not tem(n) or f'{ch}/{n}' not in cred}
        if not falta:
            continue
        info = {}
        tits = list(dict.fromkeys(falta.values()))
        for i in range(0, len(tits), 40):
            info.update(commons.info(tits[i:i + 40]))
        os.makedirs(os.path.join(ROOT, 'obras', ch), exist_ok=True)
        for n, t in falta.items():
            v = info.get(t) or info.get(t.replace('_', ' '))
            if not v or not v.get('original'):
                erros.append(f'{pos} {n}: arquivo não existe no Commons ({t})'); continue
            lic = (v['licenca'] or '').lower()
            if not any(k in lic for k in LIVRE):
                erros.append(f'{pos} {n}: licença "{v["licenca"]}" não é domínio público ({t})'); continue
            dest = os.path.join(ROOT, 'obras', ch, n); orig = v['original'].split('?')[0]; ok = tem(n)
            tmp = dest + '.part'
            # o servidor de imagens só aceita larguras padrão (960, 1280, 1920...); o original costuma voltar 429
            for larg in (1920, 1280, 960):
                if ok: break
                if larg > 960 and (v['w'] or 0) < larg * .75: continue
                ok = baixa_um(orig, larg, tmp)
            if ok and os.path.exists(tmp):
                try:
                    from PIL import Image; Image.open(tmp).verify(); os.replace(tmp, dest)
                except Exception:
                    ok = False
            if os.path.exists(tmp): os.remove(tmp)
            if not ok:
                erros.append(f'{pos} {n}: download falhou ({t})'); continue
            cred[f'{ch}/{n}'] = {'arquivo': t, 'licenca': v['licenca'], 'artista': v['artista'], 'credito': v['credito'],
                                 'pagina': 'https://commons.wikimedia.org/wiki/' + t.replace(' ', '_')}
            json.dump(cred, open(cf, 'w'), ensure_ascii=False, indent=1)
            print('ok', pos, n, v['licenca'])
            time.sleep(1)
    for e in erros: print('ERRO', e)
    sys.exit(1 if erros else 0)

if __name__ == '__main__':
    main()
