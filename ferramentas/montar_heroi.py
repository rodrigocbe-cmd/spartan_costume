"""Lê o Kratos de qualquer R_HEROnn.WAD (malha MG + esqueleto + lista de materiais) para análise/render.

heroi(n) -> dict(d=bytes do WAD, mg=bytes do MG, sk=esqueleto, refs=[nomes dos MAT do 1º bloco],
                 pecas=[{grupo, material, nome_mat, stride, P (modelo, pose T), T, m}])
Grupos rígidos podem estar no espaço LOCAL do osso (ossos auxiliares) ou no espaço do MODELO (ossos do
corpo); decide pelo que deixa o centro da peça mais perto do osso.
"""
import os
import struct

import numpy as np

import esqueleto
import malha
import wad

JOGO = os.environ.get('GOW3_JOGO', r'C:\Users\rodri\Downloads\ShadPS4 Output\CUSA01623\EXEC')


def heroi(n, caminho=None):
    d = open(caminho or os.path.join(JOGO, 'WAD', 'PS4_LE', 'R_HERO%s.WAD' % n), 'rb').read()
    es = wad.parse(d)
    i = [k for k, e in enumerate(es) if e['tag'] == 0x520001 and e['name'].startswith('MG_')][0]
    mge = es[i]
    mg = d[mge['data_off']:mge['data_off'] + mge['size']]
    j = [k for k, e in enumerate(es) if e['tag'] == 1 and e['name'] == mge['name']][0]
    refs = []
    k = j - 1
    while es[k]['tag'] == 1 and es[k]['name'].startswith('MAT'):
        refs.insert(0, es[k]['name']); k -= 1
    sk = None
    for e in es:
        if e['tag'] == 0x1f0001 and e['name'] == '' and e['size'] > 0x1000:
            sk = esqueleto.ler(d[e['data_off']:e['data_off'] + e['size']])
            break
    pecas = []
    for m in malha.ler_com_material(mg):
        p, uv, idx = malha.vertices(mg, m)
        P = np.array(p)
        if m['stride'] != 40 and m['grupo'] is not None:
            Wb = sk['mundo'][m['osso']]
            osso = Wb[3, :3]
            Pl = esqueleto.aplicar(Wb, P)
            if np.linalg.norm(Pl.mean(0) - osso) < np.linalg.norm(P.mean(0) - osso):
                P = Pl
        pecas.append(dict(grupo=m['grupo'], material=m['material'], stride=m['stride'], P=P,
                          T=np.array(idx).reshape(-1, 3), m=m,
                          nome_mat=refs[m['material']].split(':')[-1] if 0 <= m['material'] < len(refs) else '?'))
    nmat = max(p['material'] for p in pecas) + 1
    return dict(d=d, es=es, mg=mg, mg_entrada=mge, sk=sk, refs=refs[:nmat], todas_refs=refs, pecas=pecas)
