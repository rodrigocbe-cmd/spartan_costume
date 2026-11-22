"""Transplante de peças entre malhas MG de trajes diferentes (mesmo esqueleto do corpo).

- extrair(mg, sk, filtro) -> conjuntos (um por SUBMALHA do doador) em espaço do MODELO, com pesos:
  dict(pos (n,3), tan (n,4) s16, bit (n,4) s16, uv (n,2) [convenção do arquivo], ossos (n,4), pesos (n,4) u8,
       tris (m,3) locais, material, registro (bytes do registro do conjunto doador, 0x44), origem)
  Peças rígidas (vértice 28 B) viram peso 255 no osso do grupo (convertendo do espaço local, se for o caso).
- abrir_espaco(mg, n): insere n bytes antes da REGIÃO DE VÉRTICES (cabeçalho +4) e corrige os streams
  (offsets relativos que atravessam o ponto). Descritores novos vão nesse espaço (antes dos vértices:
  descritor depois do início da região de vértices não é desenhado — CLAUDE.md, teste 1).
- gravar_grupo(mg, g, osso_raiz, conjuntos): grupo `g` passa a ser um grupo com pesos com esses conjuntos
  (1 submalha cada, ≤ 16 ossos), descritor no espaço novo, vértices no fim. O bloco antigo fica sem uso.
- esconder(mg, filtro): zera os índices das submalhas (triângulos degenerados; nada é desenhado).
"""
import struct

import numpy as np

import esqueleto
import malha

_ALINHA = 16


def _al(b, a=_ALINHA):
    return b + b'\x00' * ((-len(b)) % a)


def _registro_de(mg, m):
    for c in malha.conjuntos(mg):
        if c['streams'] == m['ents'][0]['pos']:
            return c
    return None


def _rot_s16(v, R):
    """Gira vetores s16×4 (w = sinal) por R (3x3, convenção v @ R)."""
    f = v[:, :3].astype(np.float64) / 32767.0
    g = f @ R
    g /= np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-9)
    out = v.copy()
    out[:, :3] = np.round(np.clip(g, -1, 1) * 32767).astype(np.int16)
    return out


def extrair(mg, sk, filtro):
    """filtro(m) -> bool, m = malha de malha.ler_com_material (tem grupo, material, osso, stride)."""
    out = []
    for m in malha.ler_com_material(mg):
        if not filtro(m):
            continue
        c = _registro_de(mg, m)
        ents = {e['uso']: e for e in m['ents']}
        st = m['stride']
        n = m['total']
        e0 = ents[1]['alvo']
        pos = np.array([struct.unpack_from('<3f', mg, e0 + i * st) for i in range(n)], np.float64)
        tan = np.array([struct.unpack_from('<4h', mg, ents[4]['alvo'] + i * st) for i in range(n)], np.int16)
        bit = np.array([struct.unpack_from('<4h', mg, ents[5]['alvo'] + i * st) for i in range(n)], np.int16)
        us = ents[0x0f]['b'] * 4
        uv = np.array([struct.unpack_from('<2f', mg, ents[0x0f]['alvo'] + i * us) for i in range(n)], np.float64)
        if 8 in ents and 0x0a in ents:
            pesos = np.array([struct.unpack_from('<4B', mg, ents[8]['alvo'] + i * st) for i in range(n)], np.int64)
            ossos = np.array([struct.unpack_from('<4H', mg, ents[0x0a]['alvo'] + i * st) for i in range(n)], np.int64)
        else:
            Wb = sk['mundo'][m['osso']]
            Pl = esqueleto.aplicar(Wb, pos)
            o = Wb[3, :3]
            if np.linalg.norm(Pl.mean(0) - o) < np.linalg.norm(pos.mean(0) - o):   # estava no espaço local
                pos = Pl
                tan = _rot_s16(tan, Wb[:3, :3])
                bit = _rot_s16(bit, Wb[:3, :3])
            pesos = np.zeros((n, 4), np.int64); pesos[:, 0] = 255
            ossos = np.zeros((n, 4), np.int64); ossos[:, 0] = m['osso']
        caudas_sub = {}
        if c:
            R = c['reg']
            cauda = R + 0x40 + struct.unpack_from('<i', mg, R + 0x40)[0]   # +0x3c = fim dos índices
            for si, s in enumerate(m['subs']):
                ini, cnt = s['extra'] & 0xffff, s['extra'] >> 16
                d = {}
                for k in range(ini, ini + cnt):
                    rb = bytes(mg[cauda + 16 * k:cauda + 16 * k + 16])
                    d[rb[12]] = rb
                caudas_sub[si] = d
        for si, s in enumerate(m['subs']):
            b0, nv = s['base'], s['nv']
            loc = np.array(struct.unpack_from('<%dH' % (s['ntri'] * 3), mg, s['ind']), np.int64).reshape(-1, 3)
            sl = slice(b0, b0 + nv)
            out.append(dict(pos=pos[sl], tan=tan[sl], bit=bit[sl], uv=uv[sl], ossos=ossos[sl], pesos=pesos[sl],
                            tris=loc, material=m['material'],
                            registro=bytes(mg[c['reg']:c['reg'] + 0x44]) if c else None,
                            caudas=caudas_sub.get(si, {}),
                            origem=(m['grupo'], m['material'], b0)))
    return out


def abrir_espaco(mg, n):
    mg = bytearray(mg)
    V = struct.unpack_from('<I', mg, 4)[0]
    n = (n + 15) & ~15
    fixos = []
    for c in malha.conjuntos(bytes(mg)):
        ns = struct.unpack_from('<H', mg, c['reg'] + 0x20)[0]
        for k in range(ns):
            p = c['streams'] + 12 * k
            alvo = p + struct.unpack_from('<i', mg, p)[0]
            if p < V <= alvo:
                fixos.append(p)
    for p in fixos:
        struct.pack_into('<i', mg, p, struct.unpack_from('<i', mg, p)[0] + n)
    mg[V:V] = b'\x00' * n
    struct.pack_into('<I', mg, 4, V + n)
    return bytes(mg), V, n


def _registro_cauda(P, osso):
    c = (P.min(0) + P.max(0)) / 2
    r = max(1.5 * float(np.linalg.norm((P.max(0) - P.min(0)) / 2)), 1e-3)   # originais: ~1,35-1,45 x
    bits = struct.unpack('<I', struct.pack('<f', r))[0]
    man = (bits >> 7) & 0xffff
    return struct.pack('<3fBBH', *c, osso & 0xff, (bits >> 23) & 0xff, ((man & 0xff) << 8) | (man >> 8))


def _dividir(c, max_ossos=16):
    """Garante ≤ max_ossos por conjunto (divide os triângulos em partes, se precisar)."""
    usados = {int(o) for o, w in zip(c['ossos'].ravel(), c['pesos'].ravel()) if w}
    if len(usados) <= max_ossos:
        return [c]
    partes, atual, tri_atual = [], set(), []
    for t in c['tris']:
        os_t = {int(o) for v in t for o, w in zip(c['ossos'][v], c['pesos'][v]) if w}
        if len(atual | os_t) > max_ossos and tri_atual:
            partes.append(tri_atual); atual, tri_atual = set(), []
        atual |= os_t; tri_atual.append(t)
    partes.append(tri_atual)
    out = []
    for tp in partes:
        tp = np.array(tp)
        vs = np.unique(tp)
        mapa = -np.ones(len(c['pos']), np.int64); mapa[vs] = np.arange(len(vs))
        d = {k: (v[vs] if isinstance(v, np.ndarray) and len(v) == len(c['pos']) else v) for k, v in c.items()}
        d['tris'] = mapa[tp]
        out.append(d)
    return out


def gravar_grupo(mg, g_alvo, osso_raiz, conjuntos, molde_grupo=9):
    """Grupo g_alvo = conjuntos com pesos (espaço do modelo). Cada conjunto: dict de extrair(), com
    'material' já no índice do DESTINO."""
    cs = [p for c in conjuntos for p in _dividir(c)]
    mg = bytes(mg)
    tab = 0x18
    gm = struct.unpack_from('<I', mg, tab + molde_grupo * 4)[0]
    molde = mg[gm:gm + 0x70]
    nc = len(cs)
    d = bytearray(molde[:0x24]) + b'\x00' * (4 * nc)
    struct.pack_into('<I', d, 0x08, osso_raiz)
    struct.pack_into('<H', d, 0x10, nc)
    streams = []
    for k, c in enumerate(cs):
        n = len(c['pos'])
        assert (c['pesos'].sum(1) == 255).all()
        u = sorted({int(o) for o, w in zip(c['ossos'].ravel(), c['pesos'].ravel()) if w})
        d = _al(bytes(d), 4); d = bytearray(d)
        R = len(d)
        struct.pack_into('<i', d, 0x24 + 4 * k, R - (0x24 + 4 * k))
        reg = bytearray(c['registro'] if c.get('registro') else molde[0x2c:0x70])
        pal = struct.pack('<%dH' % len(u), *u); pal += b'\x00' * ((-len(pal)) % 4)
        S = 0x44 + len(pal); SUB = S + 72; I0 = SUB + 16
        # R+0x08 (u16) = índice do MATERIAL (igual ao de R+0x24; nos originais: Kratos 5/8/11/15...).
        # Manter o do doador desenhava a peça com o material errado do destino (teste 15).
        struct.pack_into('<HH', reg, 0x08, c['material'], 1)
        struct.pack_into('<HH', reg, 0x20, 6, 1)
        struct.pack_into('<HH', reg, 0x24, 1, c['material'])
        struct.pack_into('<HH', reg, 0x28, len(u), len(u))
        if not c.get('registro'):
            struct.pack_into('<HH', reg, 0x2c, 0x7c3, 4)
        else:
            struct.pack_into('<H', reg, 0x2c, struct.unpack_from('<H', reg, 0x2c)[0] | 1)   # 0x7c2 -> 0x7c3 (com pesos)
        struct.pack_into('<i', reg, 0x30, 0x44 - 0x30)
        struct.pack_into('<i', reg, 0x34, S - 0x34)
        struct.pack_into('<i', reg, 0x38, SUB - 0x38)
        corpo = reg[:0x44] + pal + b'\x00' * 72
        corpo += struct.pack('<IIiI', n, (len(c['tris']) << 8) | 0x15, I0 - (SUB + 8), len(u) << 16)
        corpo += np.asarray(c['tris'], '<u2').tobytes()
        fim_indices = len(corpo)
        corpo += b'\x00' * ((-(R + len(corpo))) % 16)
        cauda = len(corpo)
        for o in u:
            sel = ((c['ossos'] == o) & (c['pesos'] > 0)).any(1)
            P = c['pos'][sel]
            rb = c.get('caudas', {}).get(o & 0xff)
            centro = (P.min(0) + P.max(0)) / 2
            if rb is not None and np.allclose(struct.unpack_from('<3f', rb, 0), centro, atol=1e-3):
                corpo += rb                                   # registro original da peça
            else:
                corpo += _registro_cauda(P, o)
        struct.pack_into('<i', corpo, 0x3c, fim_indices - 0x3c)          # como no jogo: fim dos índices
        struct.pack_into('<i', corpo, 0x40, cauda - 0x40)
        streams.append((R + S, k, n))
        d += corpo
    struct.pack_into('<I', d, 0x20, len(d) - 0x30)
    # espaço para o descritor antes da região de vértices
    mg, ini, _ = abrir_espaco(mg, len(d))
    mg = bytearray(mg)
    mg[ini:ini + len(d)] = d
    struct.pack_into('<I', mg, tab + g_alvo * 4, ini)
    # vértices (40 B) e UV no fim
    mg = bytearray(_al(bytes(mg)))
    for S, k, n in streams:
        c = cs[k]
        vb = bytearray()
        for i in range(n):
            vb += (struct.pack('<3f', *c['pos'][i]) + np.asarray(c['tan'][i], '<i2').tobytes()
                   + np.asarray(c['bit'][i], '<i2').tobytes() + bytes(int(x) for x in c['pesos'][i])
                   + struct.pack('<4H', *[int(o) if w else 0 for o, w in zip(c['ossos'][i], c['pesos'][i])]))
        va = len(mg); mg += vb
        mg = bytearray(_al(bytes(mg)))
        ua = len(mg); mg += np.asarray(c['uv'], '<f4').tobytes()
        mg = bytearray(_al(bytes(mg)))
        for j, (alvo, a, uso, tipo, b, tam) in enumerate((
                (va, 0x00, 0x01, 7, 0x0a, n * 40), (va + 12, 0x10, 0x04, 5, 0x0a, n * 40),
                (va + 20, 0x20, 0x05, 5, 0x0a, n * 40), (ua, 0xf1, 0x0f, 0x12, 2, n * 8),
                (va + 28, 0x00, 0x08, 0, 0x0a, 0), (va + 32, 0x00, 0x0a, 0, 0x0a, 0))):
            p = ini + S + j * 12
            struct.pack_into('<iBBBBI', mg, p, alvo - p, a, uso, tipo, b, tam)
    return bytes(mg)


def esconder(mg, filtro):
    """Zera os índices das submalhas das malhas em que filtro(m) é verdadeiro."""
    mg = bytearray(mg)
    n = 0
    for m in malha.ler_com_material(bytes(mg)):
        if filtro(m):
            for s in m['subs']:
                mg[s['ind']:s['ind'] + s['ntri'] * 6] = b'\x00' * (s['ntri'] * 6)
                n += s['ntri']
    return bytes(mg), n


def repesar(conjuntos, referencia, k=6, max_ossos=4):
    """Pesos de cada vértice = média dos k vértices mais próximos das peças `referencia` (que já usam
    o esqueleto do destino), mantendo os `max_ossos` maiores (soma 255). Ex.: religar o pano vermelho
    do Kratos aos ossos de saia de outro traje."""
    from scipy.spatial import cKDTree
    R = np.vstack([c['pos'] for c in referencia])
    O = np.vstack([c['ossos'] for c in referencia])
    W = np.vstack([c['pesos'] for c in referencia])
    arv = cKDTree(R)
    for c in conjuntos:
        _, idx = arv.query(c['pos'], k=k)
        idx = np.asarray(idx).reshape(len(c['pos']), -1)
        ossos = np.zeros((len(c['pos']), 4), np.int64)
        pesos = np.zeros((len(c['pos']), 4), np.int64)
        for v, ii in enumerate(idx):
            acc = {}
            for j in ii:
                for o, w in zip(O[j], W[j]):
                    if w:
                        acc[int(o)] = acc.get(int(o), 0) + int(w)
            top = sorted(acc.items(), key=lambda x: -x[1])[:max_ossos]
            tot = sum(w for _, w in top)
            ws = [int(round(255 * w / tot)) for _, w in top]
            ws[0] += 255 - sum(ws)
            for n, ((o, _), w) in enumerate(zip(top, ws)):
                ossos[v, n] = o; pesos[v, n] = w
        c['ossos'], c['pesos'] = ossos, pesos
        c['caudas'] = {}                          # registros de cauda do doador não valem mais
    return conjuntos


def _cruza(O, d, A, B, C, tmax):
    """Reta O + t·d (|t| <= tmax) cruza algum dos triângulos (A, B, C)? (Möller–Trumbore, vetorizado)"""
    e1, e2 = B - A, C - A
    p = np.cross(d, e2)
    det = (e1 * p).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
    s = O - A
    u = (s * p).sum(1) * inv
    q = np.cross(s, e1)
    v = (d * q).sum(1) * inv
    t = (e2 * q).sum(1) * inv
    return bool((ok & (u >= -1e-4) & (v >= -1e-4) & (u + v <= 1 + 1e-4) & (np.abs(t) <= tmax)).any())


def esconder_cobertos(mg, filtro, cobertura, dist=0.06, margem=1, y_max=None):
    """Esconde triângulos (índices viram degenerados) das malhas `filtro(m)` (pele, espaço do modelo) que
    ficam sob a peça `cobertura` (lista de conjuntos de extrair): a reta da normal de CADA vértice
    (|t| <= dist, frente ou trás — a peça pode passar rente/por dentro da pele) cruza um triângulo da peça.
    Nas bordas da peça a reta não a cruza, então a pele da borda fica (sem buraco). `margem` = passadas de
    fechamento (vértice isolado no meio de cobertos). Devolve (mg, nº de triângulos)."""
    from scipy.spatial import cKDTree
    TA, TB, TC = [], [], []
    for c in cobertura:
        P = c['pos'][c['tris']]
        TA.append(P[:, 0]); TB.append(P[:, 1]); TC.append(P[:, 2])
    TA, TB, TC = np.vstack(TA), np.vstack(TB), np.vstack(TC)
    cen = (TA + TB + TC) / 3
    raio = np.maximum(np.maximum(np.linalg.norm(TA - cen, axis=1), np.linalg.norm(TB - cen, axis=1)),
                      np.linalg.norm(TC - cen, axis=1)).max()
    arv = cKDTree(cen)
    mg = bytearray(mg)
    total = 0
    for m in malha.ler_com_material(bytes(mg)):
        if not filtro(m):
            continue
        p, _, idx = malha.vertices(bytes(mg), m)
        P = np.array(p)
        e = {x['uso']: x for x in m['ents']}
        st = m['stride']
        tg = np.array([struct.unpack_from('<4h', mg, e[4]['alvo'] + i * st) for i in range(len(P))], np.float64)[:, :3]
        bt = np.array([struct.unpack_from('<4h', mg, e[5]['alvo'] + i * st) for i in range(len(P))], np.float64)[:, :3]
        nrm = np.cross(tg, bt)                                      # normal externa = uso4 × uso5
        nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
        viz = arv.query_ball_point(P, dist + raio)
        coberto = np.array([bool(viz[i]) and _cruza(P[i], nrm[i], TA[viz[i]], TB[viz[i]], TC[viz[i]], dist)
                            for i in range(len(P))])
        T = np.array(idx).reshape(-1, 3)
        for _ in range(margem):                                     # fechamento: vértice isolado no meio
            cont = np.zeros(len(P)); viz_t = np.zeros(len(P))
            np.add.at(cont, T.ravel(), np.repeat(coberto[T].sum(1), 3))
            np.add.at(viz_t, T.ravel(), 3)
            coberto |= cont >= 0.85 * viz_t
        if y_max is not None:                                       # ex.: pescoço nunca (colarinho estreito)
            coberto &= P[:, 1] < y_max
        for s in m['subs']:
            loc = np.array(struct.unpack_from('<%dH' % (s['ntri'] * 3), mg, s['ind'])).reshape(-1, 3)
            glob = loc + s['base']
            esc = coberto[glob].all(1)
            if esc.any():
                loc[esc] = loc[esc][:, :1]                          # (a, a, a): degenerado
                mg[s['ind']:s['ind'] + s['ntri'] * 6] = loc.astype('<u2').tobytes()
                total += int(esc.sum())
    return bytes(mg), total
