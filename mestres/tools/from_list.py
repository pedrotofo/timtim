"""Lê um JSON de openart_creation_list (stdin) e baixa os itens do ledger que estão prontos e ainda não baixados."""
import json, sys, os, subprocess
led = dict(l.split()[::-1] for l in open('tools/ledger.txt') if l.strip())  # historyId -> chave
d = json.load(sys.stdin)
for it in d['items']:
    k = led.get(it['historyId'])
    if k and it['status'] == 'completed' and it['url'] and not os.path.exists(f'gen/{k}.png'):
        subprocess.run(['python3', 'tools/fetch.py', k, it['url']])
