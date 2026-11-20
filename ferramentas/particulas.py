"""Cores de partículas (entradas PTS_*, tag 0x2a0001).

Estrutura observada: em +0x120 há uma tabela de 7 offsets (u32, relativos ao início dos dados)
para blocos de curvas; cada bloco = u32 contador + chaves. Nos blocos de COR cada chave tem
5 floats: (tempo, R, G, B, A). A cor final da partícula ~ cor da curva × textura.
"""
import struct

from wad import parse

TAG_PART = 0x2a0001


def blocos_cor(dados):
    """Gera (offset_da_chave, r, g, b) das chaves de cor de uma entrada PTS."""
    if len(dados) < 0x140:
        return
    offs = list(struct.unpack_from('<7I', dados, 0x120))
    lim = [o for o in offs if 0x120 < o < len(dados)]
    for i, o in enumerate(offs):
        if not (0x120 < o < len(dados) - 4):
            continue
        n = struct.unpack_from('<I', dados, o)[0]
        if not (1 <= n <= 16):
            continue
        prox = min([x for x in lim if x > o] + [len(dados)])
        if (prox - o - 4) < n * 20 or (prox - o - 4) // n != 20:
            continue                                   # só blocos com chaves de 5 floats
        for k in range(n):
            p = o + 4 + k * 20
            t, r, g, b, a = struct.unpack_from('<5f', dados, p)
            if 0 <= t <= 1.0001 and all(0 <= x <= 16 for x in (r, g, b)):
                yield p, r, g, b


def dourar_cor(r, g, b, ouro=(1.0, 0.72, 0.25)):
    """Troca o matiz de uma cor quente por dourado, mantendo intensidade e o 'branco'."""
    m = max(r, g, b)
    if m <= 1e-6:
        return r, g, b
    sat = (m - min(r, g, b)) / m
    quente = r >= g >= b * 0.9 and sat > 0.25          # vermelho/laranja/amarelo
    if not quente:
        return r, g, b
    return tuple(m * (oc * sat + (1 - sat)) for oc in ouro)


def dourar_wad(d):
    """Devolve o WAD com as chaves de cor quentes das partículas trocadas por dourado."""
    d = bytearray(d)
    n = 0
    for e in parse(bytes(d)):
        if e['tag'] != TAG_PART or not e['name'].startswith('PTS_'):
            continue
        base = e['data_off']
        dados = bytes(d[base:base + e['size']])
        for p, r, g, b in blocos_cor(dados):
            nr, ng, nb = dourar_cor(r, g, b)
            if (nr, ng, nb) != (r, g, b):
                struct.pack_into('<3f', d, base + p + 4, nr, ng, nb)
                n += 1
    return bytes(d), n
