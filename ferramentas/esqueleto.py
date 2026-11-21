"""Esqueleto do Kratos (entrada sem nome, tag 0x1f0001, logo após `gohero` no R_HERO00.WAD).

Layout observado:
  +0x04 u32 nº de juntas (254)
  +0x14 hierarquia: 8 B por junta = u16 flags, u16 primeiro filho, u16 irmão, u16 pai (0xffff = nenhum)
  nomes: campos de 56 B ('hero', 'JOPelvis1', …)
  +0x3fa0: u32 n, u32 n, u32 offset → matrizes 4x4 locais (relativas ao pai), linha-maior,
           translação na 4ª linha (convenção v * M).
"""
import re
import struct

import numpy as np


def ler(b):
    n = struct.unpack_from('<I', b, 4)[0]
    pais = []
    for i in range(n):
        flags, filho, irmao, pai = struct.unpack_from('<4H', b, 0x14 + i * 8)
        pais.append(-1 if pai == 0xffff else pai)
    i = b.find(b'hero\x00')
    nomes = []
    for k in range(n):
        o = i + k * 56
        nomes.append(b[o:o + 56].split(b'\0')[0].decode('latin1'))
    # tabela de matrizes: procura (n, n, offset) após os nomes
    p = i + n * 56
    while p < len(b) - 12:
        a, c, off = struct.unpack_from('<3I', b, p)
        if a == n and c == n and p < off < len(b):
            break
        p += 4
    off += 16                                   # dados começam 16 B após o offset
    loc = np.frombuffer(b[off:off + n * 64], dtype='<f4').reshape(n, 4, 4).astype(np.float64)
    glob = np.zeros_like(loc)
    for k in range(n):
        glob[k] = loc[k] if pais[k] < 0 else loc[k] @ glob[pais[k]]
    return dict(n=n, pais=pais, nomes=nomes, local=loc, mundo=glob)


def aplicar(M, pts):
    pts = np.asarray(pts, dtype=np.float64)
    h = np.c_[pts, np.ones(len(pts))]
    return (h @ M)[:, :3]
