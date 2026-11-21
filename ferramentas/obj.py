"""Leitura simples de OBJ (v, vt, f, usemtl) por material."""
import numpy as np


def ler(caminho):
    V, VT, partes, cur = [], [], {}, None
    for l in open(caminho, encoding='latin1'):
        t = l.split()
        if not t:
            continue
        if t[0] == 'v':
            V.append([float(x) for x in t[1:4]])
        elif t[0] == 'vt':
            VT.append([float(x) for x in t[1:3]])
        elif t[0] == 'usemtl':
            cur = t[1]
            partes.setdefault(cur, [])
        elif t[0] == 'f':
            f = []
            for c in t[1:]:
                s = c.split('/')
                f.append((int(s[0]) - 1, int(s[1]) - 1 if len(s) > 1 and s[1] else -1))
            for k in range(1, len(f) - 1):
                partes[cur].append((f[0], f[k], f[k + 1]))
    return np.array(V), np.array(VT) if VT else None, partes
