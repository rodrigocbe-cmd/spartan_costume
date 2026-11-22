"""Teste rápido (sem pacote/deltas): grava os trajes direto numa pasta de mod do SpartanPort.

uso: python -I costumes/god_armor/instalar_teste.py [ids...]      (padrão: todos do pacote)
Usa a mesma geração do build (ferramentas/trajes.py): slots 9, 10, ... na ordem dada.
Se o mod do instalador ("GoW3 Costumes") estiver instalado, desative-o para não conflitar.
"""
import json
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
import trajes  # noqa: E402
from build import TRAJES  # noqa: E402

DESTINOS = [os.path.join(RAIZ, 'build', 'teste_slot', 'GoW3 Costumes - Teste slot novo'),
            r'C:\Games\God of War III\mods\GoW3 Costumes - Teste slot novo']


def main(ids):
    arquivos = []
    slots = trajes.com_slot(ids)
    for cid in ids:
        i = trajes.PRIMEIRO_INDICE + slots.index(cid) if cid in slots else None
        for fonte, dest, dados in trajes.arquivos_traje(cid):
            arquivos.append((trajes.destino(dest, i), dados))
    if slots:
        arquivos += [(dest, dados) for _, dest, dados, _ in trajes.compartilhados(slots)]
    pats = [(cid, trajes.patches(cid, trajes.PRIMEIRO_INDICE + slots.index(cid))) for cid in slots]
    for out in DESTINOS:
        for velho in ('EXEC', 'patches'):                       # limpa a instalação anterior
            if os.path.isdir(os.path.join(out, velho)):
                shutil.rmtree(os.path.join(out, velho))
        for cid, p in pats:
            if 'spartanport' in p:
                os.makedirs(os.path.join(out, 'patches'), exist_ok=True)
                open(os.path.join(out, 'patches', cid + '.xml'), 'w', encoding='utf-8').write(p['spartanport'])
        for rel, dados in arquivos:
            p = os.path.join(out, 'EXEC', *rel.split('/'))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'wb') as f:
                f.write(dados)
        nomes = ', '.join(trajes.meta(c)['nomes']['pt'] for c in ids)
        json.dump(dict(name='GoW III Costumes (teste)', author='GoW III Costumes', version='dev',
                       description='Teste: ' + nomes), open(os.path.join(out, 'mod.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        mj = os.path.join(os.path.dirname(os.path.dirname(out)), 'mods.json')   # SpartanPort: ordem dos mods
        if os.path.exists(mj):
            j = json.load(open(mj, encoding='utf-8'))
            nome = os.path.basename(out)
            if nome not in j.get('order', []):
                j.setdefault('order', []).append(nome)
                json.dump(j, open(mj, 'w', encoding='utf-8'), indent=2)
        print('instalado em', out)


if __name__ == '__main__':
    main(sys.argv[1:] or TRAJES)
