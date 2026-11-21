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
