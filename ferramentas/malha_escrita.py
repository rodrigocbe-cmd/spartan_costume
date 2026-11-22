"""Escrita de grupos rígidos em malhas MG (ver CLAUDE.md, "Malha MG").

Estratégia segura: o grupo novo (descritor + índices) e seus vértices vão para o FIM do MG e só a
entrada do grupo na tabela (+0x18) passa a apontar para lá. O bloco antigo fica sem uso; nenhum
outro ponteiro (todos relativos) muda.

Molde: grupo rígido simples com 1 conjunto de streams e 1 submalha (ex.: grupo 9 do Kratos,
gldnFlcShould1). Layout do molde (offsets a partir do início do grupo):
  +0x08 osso   +0x20 tamanho do resto (bloco - 0x30)   +0x50 material<<16 | 1
  +0x68/+0x6c ponteiros relativos para a cauda   +0x70 paleta (u16 osso)
  +0x74 4 streams × 12 B (pos, uso4, uso5, UV)   +0xa4 submalha 16 B   +0xb4 índices   cauda 32 B
"""
import struct

import numpy as np

ESTRIDE = 28


def _alinhar(b, a=16):
    return b + b'\x00' * ((-len(b)) % a)


def empacotar_s16(v):
    v = np.clip(np.asarray(v, dtype=np.float64), -1, 1)
    return np.round(v * 32767).astype('<i2')


def bloco_grupo(molde, osso, material, ntri, flags=0x16):
    """Descritor (sem índices/cauda) copiado do molde com osso/material ajustados."""
    d = bytearray(molde[:0xb4])
    struct.pack_into('<I', d, 0x08, osso)
    struct.pack_into('<I', d, 0x50, (material << 16) | 1)
    struct.pack_into('<I', d, 0x70, osso)          # paleta: 1 osso (u16) + padding
    return d


def substituir_grupo(mg, g_alvo, g_molde, osso, material, pos, nrm_raw, tan_raw, uv, tris):
    """Devolve um MG novo em que o grupo `g_alvo` passa a ser uma malha rígida nova.

    pos: (n,3) float no espaço local do osso; nrm_raw/tan_raw: (n,4) int16 (w = ±32767);
    uv: (n,2) float JÁ na convenção do arquivo (v = v_png + 1); tris: (m,3) índices.
    """
    mg = bytearray(mg)
    n = len(pos)
    tris = np.asarray(tris, dtype='<u2').reshape(-1, 3)
    ntri = len(tris)
    tab = 0x18
    g0 = struct.unpack_from('<I', mg, tab + g_molde * 4)[0]
    molde = bytes(mg[g0:g0 + 0xb4])
    assert molde[0x74 + 5] == 1 and molde[0x74 + 36 + 5] == 0x0f, 'molde inesperado'

    # vértices: pos float3 + uso4 s16×4 + uso5 s16×4 (28 B), depois UV float2
    vb = bytearray()
    for i in range(n):
        vb += struct.pack('<3f', *pos[i]) + np.asarray(nrm_raw[i], '<i2').tobytes() + np.asarray(tan_raw[i], '<i2').tobytes()
    uvb = np.asarray(uv, dtype='<f4').tobytes()

    desc = bloco_grupo(molde, osso, material, ntri)
    ind = tris.tobytes()
    P = np.asarray(pos)
    centro = (P.min(0) + P.max(0)) / 2
    raio = float(np.linalg.norm(np.asarray(pos) - centro, axis=1).max())
    cauda = struct.pack('<4f', *centro, 0.0) + struct.pack('<4f', *centro, raio)
    corpo = bytes(desc) + struct.pack('<IIiI', n, (ntri << 8) | 0x16, 8, 0x10000)
    # (o cabeçalho da submalha ocupa 0xa4..0xb4; os índices começam em +0xb4 = rel 8 a partir de +0xac)
    corpo = bytes(desc[:0xa4]) + struct.pack('<IIiI', n, (ntri << 8) | 0x16, 8, 0x10000) + ind
    pos_cauda = len(corpo)
    corpo += cauda
    corpo = bytearray(corpo)
    struct.pack_into('<I', corpo, 0x20, len(corpo) - 0x30)
    struct.pack_into('<i', corpo, 0x68, pos_cauda - 0x68)
    struct.pack_into('<i', corpo, 0x6c, pos_cauda - 0x6c)

    # posiciona: [MG atual][pad][grupo novo][pad][vértices][UV]
    mg = bytearray(_alinhar(bytes(mg)))
    ini = len(mg)
    mg += corpo
    mg = bytearray(_alinhar(bytes(mg)))
    vini = len(mg)
    mg += vb
    uvini = len(mg)
    mg += uvb
    # streams (relativos à própria entrada)
    def ent(k, alvo, tam):
        p = ini + 0x74 + k * 12
        struct.pack_into('<i', mg, p, alvo - p)
        struct.pack_into('<I', mg, p + 8, tam)
    ent(0, vini, n * ESTRIDE)
    ent(1, vini + 12, n * ESTRIDE)
    ent(2, vini + 20, n * ESTRIDE)
    ent(3, uvini, n * 8)
    struct.pack_into('<I', mg, tab + g_alvo * 4, ini)
    return bytes(_alinhar(bytes(mg)))


def substituir_grupo_no_lugar(mg, g_alvo, g_molde, osso, material, pos, nrm_raw, tan_raw, uv, tris,
                              vertices_no_lugar=False):
    """Como substituir_grupo, mas o DESCRITOR vai no lugar do bloco antigo do grupo (precisa caber).
    vertices_no_lugar=True: vértices/UV sobre os do grupo antigo (precisa caber); senão, no fim do MG."""
    mg = bytearray(mg)
    n = len(pos)
    tris = np.asarray(tris, dtype='<u2').reshape(-1, 3)
    ntri = len(tris)
    tab = 0x18
    g0 = struct.unpack_from('<I', mg, tab + g_molde * 4)[0]
    molde = bytes(mg[g0:g0 + 0xb4])
    ga = struct.unpack_from('<I', mg, tab + g_alvo * 4)[0]
    tam_antigo = 0x30 + struct.unpack_from('<I', mg, ga + 0x20)[0]
    # streams antigos do grupo (para reaproveitar o espaço de vértices)
    antigo = None
    if vertices_no_lugar:
        import malha
        antigo = [m for m in malha.ler(bytes(mg)) if m['grupo'] == g_alvo][0]
    desc = bloco_grupo(molde, osso, material, ntri)
    P = np.asarray(pos, dtype=np.float64)
    centro = (P.min(0) + P.max(0)) / 2
    raio = float(np.linalg.norm(P - centro, axis=1).max())
    corpo = bytes(desc[:0xa4]) + struct.pack('<IIiI', n, (ntri << 8) | 0x16, 8, 0x10000) + tris.tobytes()
    pos_cauda = len(corpo)
    corpo = bytearray(corpo + struct.pack('<4f', *centro, 0.0) + struct.pack('<4f', *centro, raio))
    assert len(corpo) <= tam_antigo, f'descritor novo ({len(corpo):#x}) maior que o antigo ({tam_antigo:#x})'
    struct.pack_into('<I', corpo, 0x20, len(corpo) - 0x30)
    struct.pack_into('<i', corpo, 0x68, pos_cauda - 0x68)
    struct.pack_into('<i', corpo, 0x6c, pos_cauda - 0x6c)
    vb = bytearray()
    for i in range(n):
        vb += struct.pack('<3f', *pos[i]) + np.asarray(nrm_raw[i], '<i2').tobytes() + np.asarray(tan_raw[i], '<i2').tobytes()
    uvb = np.asarray(uv, dtype='<f4').tobytes()
    if vertices_no_lugar:
        assert n <= antigo['total'] and antigo['stride'] == ESTRIDE, 'vértices não cabem no lugar antigo'
        vini = antigo['ents'][0]['alvo']
        uvini = antigo['uv']['alvo']
        mg[vini:vini + len(vb)] = vb
        mg[uvini:uvini + len(uvb)] = uvb
    else:
        mg = bytearray(_alinhar(bytes(mg)))
        vini = len(mg)
        mg += vb
        uvini = len(mg)
        mg += uvb
    mg[ga:ga + tam_antigo] = bytes(corpo) + b'\x00' * (tam_antigo - len(corpo))
    def ent(k, alvo, tam):
        p = ga + 0x74 + k * 12
        struct.pack_into('<i', mg, p, alvo - p)
        struct.pack_into('<I', mg, p + 8, tam)
    ent(0, vini, n * ESTRIDE)
    ent(1, vini + 12, n * ESTRIDE)
    ent(2, vini + 20, n * ESTRIDE)
    ent(3, uvini, n * 8)
    return bytes(_alinhar(bytes(mg)))


# ---------------------------------------------------------------- grupo COM PESOS (vértices de 40 B)
# Layout (visto nas asas de Hermes, grupos 15/17, e na pele/saia, grupo 21), offsets do início do grupo:
#   +0x10 nº de conjuntos   +0x20 tamanho do resto   +0x24 tabela: rel (a partir da própria entrada) → registro
#   de cada conjunto. Registro R (tudo relativo ao próprio campo):
#   R+0x00 0x17, 1, (6 | 1<<16), float, 1, 0, 0x20, 0   R+0x20 nº streams (6) | nº submalhas<<16
#   R+0x24 1 | material<<16   R+0x28 soma das paletas das submalhas | nº de ossos distintos<<16
#   R+0x2c 0x7c3 | 4<<16      R+0x30 rel→paleta (R+0x44: u16 por osso distinto, crescente, alinhada a 4)
#   R+0x34 rel→streams (6×12: pos, uso4, uso5, UV, pesos u8×4 @+0x1c, ossos u16×4 @+0x20)
#   R+0x38 rel→submalhas (16 B: nv, ntri<<8|flags, rel→índices, nº ossos<<16 | início cumulativo)
#   R+0x3c/R+0x40 rel→cauda: 1 registro de 16 B por (submalha, osso): centro da caixa (modelo) dos vértices
#   desse osso + u8 osso + 3 bytes (1º = expoente do raio em float; os outros 2 não decifrados).
# Na saia original cada conjunto tem 1 submalha e no máximo 16 ossos. Índices de osso nos vértices =
# juntas do esqueleto (absolutos); posições em espaço do MODELO (pose de ligação).
ESTRIDE_PESOS = 40


def _registro_cauda(P, osso):
    c = (P.min(0) + P.max(0)) / 2
    r = max(float(np.linalg.norm((P.max(0) - P.min(0)) / 2)), 1e-3)
    bits = struct.unpack('<I', struct.pack('<f', r))[0]
    man = (bits >> 7) & 0xffff
    return struct.pack('<3fBBH', *c, osso & 0xff, (bits >> 23) & 0xff, ((man & 0xff) << 8) | (man >> 8))


def substituir_grupo_ponderado_no_lugar(mg, g_alvo, osso_raiz, material, pos, nrm_raw, tan_raw, uv, tris,
                                        ossos, pesos, conjuntos, max_ossos=16):
    """Grupo `g_alvo` vira uma malha com pesos (como a pele), descritor no lugar do bloco antigo.
    pos (n,3) espaço do modelo; ossos (n,4) juntas; pesos (n,4) u8 somando 255 (0 = sem uso, osso 0);
    tris (m,3) índices globais; conjuntos = [(v0, v1, t0, t1)] intervalos contíguos de vértices/triângulos,
    cada um gravado como um conjunto com 1 submalha e no máximo `max_ossos` ossos."""
    mg = bytearray(mg)
    pos = np.asarray(pos, np.float64); n = len(pos)
    tris = np.asarray(tris, np.int64).reshape(-1, 3)
    ossos = np.asarray(ossos, np.int64); pesos = np.asarray(pesos, np.int64)
    assert (pesos.sum(1) == 255).all()
    tab = 0x18
    g9 = struct.unpack_from('<I', mg, tab + 9 * 4)[0]
    molde = bytes(mg[g9:g9 + 0x70])                          # grupo rígido de 1 conjunto (registro em +0x2c)
    ga = struct.unpack_from('<I', mg, tab + g_alvo * 4)[0]
    tam_antigo = 0x30 + struct.unpack_from('<I', mg, ga + 0x20)[0]
    nc = len(conjuntos)
    d = bytearray(molde[:0x24]) + b'\x00' * (4 * nc)
    struct.pack_into('<I', d, 0x08, osso_raiz)
    struct.pack_into('<H', d, 0x10, nc)
    streams = []                                              # (posição absoluta no grupo, v0, nv)
    for k, (v0, v1, t0, t1) in enumerate(conjuntos):
        assert tris[t0:t1].min() >= v0 and tris[t0:t1].max() < v1
        u = sorted({int(o) for o, w in zip(ossos[v0:v1].ravel(), pesos[v0:v1].ravel()) if w})
        assert len(u) <= max_ossos, ('conjunto com ossos demais', len(u))
        d += b'\x00' * ((-len(d)) % 4)
        R = len(d)
        struct.pack_into('<i', d, 0x24 + 4 * k, R - (0x24 + 4 * k))
        reg = bytearray(molde[0x2c:0x70])
        pal = struct.pack('<%dH' % len(u), *u); pal += b'\x00' * ((-len(pal)) % 4)
        S = 0x44 + len(pal); SUB = S + 72; I0 = SUB + 16
        struct.pack_into('<I', reg, 0x08, 6 | 1 << 16)
        struct.pack_into('<HH', reg, 0x20, 6, 1)
        struct.pack_into('<HH', reg, 0x24, 1, material)
        struct.pack_into('<HH', reg, 0x28, len(u), len(u))
        struct.pack_into('<HH', reg, 0x2c, 0x7c3, 4)
        struct.pack_into('<i', reg, 0x30, 0x44 - 0x30)
        struct.pack_into('<i', reg, 0x34, S - 0x34)
        struct.pack_into('<i', reg, 0x38, SUB - 0x38)
        corpo = reg + pal + b'\x00' * 72
        corpo += struct.pack('<IIiI', v1 - v0, ((t1 - t0) << 8) | 0x15, I0 - (SUB + 8), len(u) << 16)
        corpo += (tris[t0:t1] - v0).astype('<u2').tobytes()
        corpo += b'\x00' * ((-(R + len(corpo))) % 16)
        cauda = len(corpo)
        for o in u:
            sel = ((ossos[v0:v1] == o) & (pesos[v0:v1] > 0)).any(1)
            corpo += _registro_cauda(pos[v0:v1][sel], o)
        struct.pack_into('<i', corpo, 0x3c, cauda - 0x3c)
        struct.pack_into('<i', corpo, 0x40, cauda - 0x40)
        streams.append((R + S, v0, v1 - v0))
        d += corpo
    struct.pack_into('<I', d, 0x20, len(d) - 0x30)
    assert len(d) <= tam_antigo, f'descritor novo ({len(d):#x}) maior que o antigo ({tam_antigo:#x})'
    vb = bytearray()
    for i in range(n):
        vb += (struct.pack('<3f', *pos[i]) + np.asarray(nrm_raw[i], '<i2').tobytes()
               + np.asarray(tan_raw[i], '<i2').tobytes() + bytes(int(x) for x in pesos[i])
               + struct.pack('<4H', *[int(o) if w else 0 for o, w in zip(ossos[i], pesos[i])]))
    assert len(vb) == n * ESTRIDE_PESOS
    mg = bytearray(_alinhar(bytes(mg)))
    vini = len(mg); mg += vb
    mg = bytearray(_alinhar(bytes(mg)))
    uvini = len(mg); mg += np.asarray(uv, dtype='<f4').tobytes()
    mg[ga:ga + tam_antigo] = bytes(d) + b'\x00' * (tam_antigo - len(d))
    for S, v0, nv in streams:
        va = vini + v0 * ESTRIDE_PESOS
        for k, (alvo, a, uso, tipo, b, tam) in enumerate((
                (va, 0x00, 0x01, 7, 0x0a, nv * ESTRIDE_PESOS), (va + 12, 0x10, 0x04, 5, 0x0a, nv * ESTRIDE_PESOS),
                (va + 20, 0x20, 0x05, 5, 0x0a, nv * ESTRIDE_PESOS), (uvini + v0 * 8, 0xf1, 0x0f, 0x12, 2, nv * 8),
                (va + 28, 0x00, 0x08, 0, 0x0a, 0), (va + 32, 0x00, 0x0a, 0, 0x0a, 0))):
            p = ga + S + k * 12
            struct.pack_into('<iBBBBI', mg, p, alvo - p, a, uso, tipo, b, tam)
    return bytes(_alinhar(bytes(mg)))
