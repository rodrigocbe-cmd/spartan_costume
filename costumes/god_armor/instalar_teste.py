"""Teste rápido (sem pacote/deltas): grava os trajes direto numa pasta de mod do SpartanPort.

uso: python -I costumes/god_armor/instalar_teste.py [ids...]      (padrão: todos do pacote)
Usa a mesma geração do build (ferramentas/trajes.py): slots 9, 10, ... na ordem dada.
Se o mod do instalador ("GoW3 Costumes") estiver instalado, desative-o para não conflitar.
"""
import os
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
    for out in DESTINOS:
        for rel, dados in arquivos:
            p = os.path.join(out, 'EXEC', *rel.split('/'))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'wb') as f:
                f.write(dados)
        print('instalado em', out)


if __name__ == '__main__':
    main(sys.argv[1:] or TRAJES)
