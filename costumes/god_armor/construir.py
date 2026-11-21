"""Constrói o MG do Kratos com as peças da Armadura do Deus da Guerra (geometria própria).

Peças (grupos rígidos reaproveitados — ver CLAUDE.md "Regras validadas no jogo"):
  grupo 9  ← ombreira direita (carneiro)   osso 0x61 gldnFlcShould1 (auxiliar → espaço LOCAL)
  grupo 6  ← ombreira esquerda (espelho)   osso 0x82 JOLeftUpperArm1Twist1 (pele → espaço do MODELO)
  grupos 7, 10, 11, 12 (resto do Velo de Ouro) ← ocultos (1 triângulo degenerado)
Vértices: pos + uso4 (tangente) + uso5 (bitangente) com normal EXTERNA = uso4 × uso5;
triângulos do GoW III em ordem HORÁRIA (produto vetorial aponta p/ dentro); UV no arquivo = (u, 2 - v_obj).
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
sys.path.insert(0, AQUI)
import malha, malha_escrita as W, esqueleto, obj, encaixe   # noqa: E402

# Ajuste da ombreira (espaço do modelo, pose T, lado direito). Com o braço abaixado:
# -x (em direção ao pescoço) = SOBE no ombro; +y = vai para fora; -z = para a frente.
ESCALA_OMBREIRA = 0.97
DESLOC_OMBREIRA = np.array([-0.03, 0.015, -0.04])   # teste 5 era [+0.05, +0.04, 0] com escala 1.05

OBJ_SC = os.path.join(RAIZ, 'referencias', 'god_armor', 'soulcalibur_bd', 'kratos_2p_god_armor', 'Kratos God Armor.obj')


def normais_suaves(P, T, fn=None, limiar=0.5, tol=1e-4):
    """Normal por vértice somando as faces de TODOS os vértices na mesma posição (solda as costuras
    de UV, evitando o sombreamento facetado), só entre faces com ângulo parecido (dot > limiar) —
    peças de dupla face (frente/verso) não se anulam."""
    if fn is None:
        fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    fu = fn / (np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12)
    _, grp = np.unique(np.round(P / tol).astype(np.int64), axis=0, return_inverse=True)
    grp = grp.ravel()
    inc = [[] for _ in range(len(P))]
    for f, t in enumerate(T):
        for v in t:
            inc[v].append(f)
    faces_grp = {}
    for v in range(len(P)):
        faces_grp.setdefault(grp[v], []).extend(inc[v])
    N = np.zeros_like(P)
    for v in range(len(P)):
        if not inc[v]:
            N[v] = [0, 1, 0]; continue
        propria = fu[inc[v]].sum(0)
        fs = np.unique(faces_grp[grp[v]])
        ok = fu[fs] @ (propria / (np.linalg.norm(propria) + 1e-12)) > limiar
        N[v] = fn[fs][ok].sum(0)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


def referencial(P, T, UV):
    """Normal, tangente e bitangente por vértice (espaço de P)."""
    N = np.zeros_like(P); Tg = np.zeros_like(P)
    p0, p1, p2 = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    d1, d2 = UV[T[:, 1]] - UV[T[:, 0]], UV[T[:, 2]] - UV[T[:, 0]]
    det = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    det[np.abs(det) < 1e-12] = 1e-12
    tf = ((p1 - p0) * d2[:, 1:2] - (p2 - p0) * d1[:, 1:2]) / det[:, None]
    for k in range(3):
        np.add.at(Tg, T[:, k], tf)
    N = normais_suaves(P, T, fn)
    Tg = Tg - N * (Tg * N).sum(1, keepdims=True)
    ruim = np.linalg.norm(Tg, axis=1) < 1e-8
    Tg[ruim] = np.cross(N[ruim], [0, 1, 0]) + 1e-6
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-12
    B = np.cross(N, Tg)                 # uso4 × uso5 = Tg × (N × Tg) = N (externa)
    return N, Tg, B


def empacotar(v):
    return np.c_[np.round(np.clip(v, -1, 1) * 32767), np.full(len(v), 32767)].astype('<i2')


def peca(mg, grupo, osso, espaco_local, sk, P_modelo, T, UV_obj, material=4):
    """Grava a peça (P em espaço do modelo, pose T) no grupo, convertendo p/ o espaço certo.
    T em ordem anti-horária (normal para fora); é gravado em ordem horária (convenção do jogo)."""
    Wb = sk['mundo'][osso]
    if espaco_local:
        P = esqueleto.aplicar(np.linalg.inv(Wb), P_modelo)
    else:
        P = P_modelo
    UVf = np.c_[UV_obj[:, 0], 2.0 - UV_obj[:, 1]]
    N, Tg, B = referencial(P, T, np.c_[UV_obj[:, 0], 1.0 - UV_obj[:, 1]])
    return W.substituir_grupo_no_lugar(mg, grupo, 9, osso, material, P, empacotar(Tg), empacotar(B), UVf,
                                       T[:, [0, 2, 1]], vertices_no_lugar=False)


def ocultar(mg, grupo, osso):
    P = np.zeros((3, 3)); T = np.array([[0, 1, 2]])
    z = np.tile([0, 0, 0, 32767], (3, 1)).astype('<i2')
    return W.substituir_grupo_no_lugar(mg, grupo, 9, osso, 4, P, z, z, np.zeros((3, 2)), T)


def ombreiras_sc():
    """Ombreira direita do SC (mat_15, x>0) já encaixada no Kratos (espaço do modelo, pose T)."""
    V, VT, partes = obj.ler(OBJ_SC)
    ts = [t for t in partes['mat_15.020'] if V[[v for v, _ in t]][:, 0].mean() > 0]
    # desfaz o compartilhamento de vértices (cada vértice com seu UV)
    pares = {}
    P, UV, T = [], [], []
    for t in ts:
        tri = []
        for v, u in t:
            k = (v, u)
            if k not in pares:
                pares[k] = len(P); P.append(V[v]); UV.append(VT[u])
            tri.append(pares[k])
        T.append(tri)
    P, UV, T = np.array(P), np.array(UV), np.array(T)
    # atlas: ombreira no quadrante superior esquerdo (v_png = 1 - v_obj)
    UV = np.c_[UV[:, 0] * 0.5, 1 - (1 - UV[:, 1]) * 0.5]
    return P, UV, T


# Peitoral: casca da pele do tronco (grupo 21), deslocada p/ fora, simplificada e dividida em 4 partes.
REGIAO_TRONCO = dict(xmax=0.29, ymin=1.48, ymax=2.00, pescoco_x=0.11, pescoco_y=1.93)
DESLOC_PEITORAL = 0.045
CORTE_Y = 1.72
PARTES_PEITORAL = [  # (grupo, osso, limite de triângulos, metade de cima?, lado x>=0?)
    (11, 0x4, 205, True, False), (12, 0x4, 205, True, True),     # resto do limite (289/286) = meia-gola
    (7, 0x3, 209, False, False), (10, 0x3, 144, False, True)]


def pele_tronco(mg_ref):
    Ps, Ts, base = [], [], 0
    r = REGIAO_TRONCO
    for m in malha.ler(mg_ref):
        if m['grupo'] != 21 or m['stride'] != 40:
            continue
        p, _, i = malha.vertices(mg_ref, m)
        P = np.array(p); T = np.array(i).reshape(-1, 3)
        c = P[T].mean(1)
        sel = (np.abs(c[:, 0]) < r['xmax']) & (c[:, 1] > r['ymin']) & (c[:, 1] < r['ymax']) &               ~((np.abs(c[:, 0]) < r['pescoco_x']) & (c[:, 1] > r['pescoco_y']))
        if sel.any():
            Ps.append(P); Ts.append(T[sel] + base); base += len(P)
    P = np.vstack(Ps); T = np.vstack(Ts)
    # solda vértices duplicados nas costuras das submalhas (senão cada cópia desloca diferente)
    _, inv = np.unique(np.round(P / 1e-5).astype(np.int64), axis=0, return_inverse=True)
    T = inv.ravel()[T]
    P = _primeiros(P, inv.ravel())
    T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    usados = np.unique(T)
    mapa = -np.ones(len(P), int); mapa[usados] = np.arange(len(usados))
    return P[usados], mapa[T]


def _primeiros(P, inv):
    Q = np.zeros((inv.max() + 1, 3)); Q[inv] = P
    return Q


def normais_externas(P, T, cz):
    N = np.zeros_like(P)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    for k in range(3):
        np.add.at(N, T[:, k], fn)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    radial = np.c_[P[:, 0], np.zeros(len(P)), P[:, 2] - cz]
    sinal = np.sign((N * radial).sum(1).mean()) or 1
    return N * sinal


def simplificar(P, T, celula):
    """Agrupamento de vértices em grade (célula em metros). Devolve (Q, T)."""
    chave = np.floor(P / celula).astype(np.int64)
    _, inv = np.unique(chave, axis=0, return_inverse=True)
    inv = inv.ravel()
    n = inv.max() + 1
    Q = np.zeros((n, 3)); cnt = np.zeros(n)
    np.add.at(Q, inv, P); np.add.at(cnt, inv, 1)
    Q /= cnt[:, None]
    T2 = inv[T]
    ok = (T2[:, 0] != T2[:, 1]) & (T2[:, 1] != T2[:, 2]) & (T2[:, 0] != T2[:, 2])
    T2 = T2[ok]
    _, idx = np.unique(np.sort(T2, 1), axis=0, return_index=True)
    T2 = T2[np.sort(idx)]
    usados = np.unique(T2)
    mapa = -np.ones(n, int); mapa[usados] = np.arange(len(usados))
    return Q[usados], mapa[T2]


def suavizar(Q, T, iters=2, k=0.5):
    """Laplaciano leve; vértices da borda ficam fixos."""
    from collections import Counter
    arestas = Counter(tuple(sorted(e)) for t in T for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])))
    borda = np.zeros(len(Q), bool)
    for (a, b), n in arestas.items():
        if n == 1:
            borda[a] = borda[b] = True
    viz = [[] for _ in range(len(Q))]
    for a, b in arestas:
        viz[a].append(b); viz[b].append(a)
    for _ in range(iters):
        m = np.array([Q[v].mean(0) if v else q for q, v in zip(Q, viz)])
        Q = np.where(borda[:, None], Q, Q + k * (m - Q))
    return Q


def _compactar(Q, T):
    usados = np.unique(T)
    mapa = -np.ones(len(Q), int); mapa[usados] = np.arange(len(usados))
    return Q[usados], mapa[T], usados


def peitoral_partes(mg_ref):
    """Devolve [(grupo, osso, Q, NQ, T)] e cz. A casca é simplificada UMA vez e depois dividida
    (bordas compartilhadas entre as partes = sem frestas)."""
    P, T = pele_tronco(mg_ref)
    cz = P[:, 2].mean()
    P = P + normais_externas(P, T, cz) * DESLOC_PEITORAL
    lim = {g: l for g, _, l, _, _ in PARTES_PEITORAL}
    cima_max = sum(l for _, _, l, c, _ in PARTES_PEITORAL if c)
    baixo_max = sum(l for _, _, l, c, _ in PARTES_PEITORAL if not c)
    lo, hi, melhor = 0.003, 0.08, None
    for _ in range(20):                                       # busca binária na célula
        mid = (lo + hi) / 2
        Q, Tq = simplificar(P, T, mid)
        cy = Q[Tq].mean(1)[:, 1]
        if (cy >= CORTE_Y).sum() <= cima_max and (cy < CORTE_Y).sum() <= baixo_max:
            melhor = (Q, Tq); hi = mid
        else:
            lo = mid
    Q, Tq = melhor
    Q = suavizar(Q, Tq)
    NQ = normais_externas(Q, Tq, cz)
    c = Q[Tq].mean(1)
    out = []
    for cima in (True, False):
        esq, dir_ = [(g, o) for g, o, _, cc, d in PARTES_PEITORAL if cc == cima and not d][0],                     [(g, o) for g, o, _, cc, d in PARTES_PEITORAL if cc == cima and d][0]
        idx = np.flatnonzero((c[:, 1] >= CORTE_Y) == cima)
        idx = idx[np.argsort(c[idx, 0])]                      # da esquerda (x<0) para a direita
        n = len(idx)
        k = int((c[idx, 0] < 0).sum())                        # divisão no meio, ajustada aos limites
        k = min(max(k, n - lim[dir_[0]]), lim[esq[0]])
        for (g, osso), sel in ((esq, idx[:k]), (dir_, idx[k:])):
            Qp, Tp, us = _compactar(Q, Tq[sel])
            out.append((g, osso, Qp, NQ[us], Tp))
    return out, cz


def uv_cilindrico(Pc, cz):
    """u = ângulo em volta do tronco (frente no centro) → metade direita do atlas; v do topo à base."""
    ang = np.arctan2(Pc[..., 0], -(Pc[..., 2] - cz))            # 0 na frente (-z)
    u = 0.5 + ang / (2 * np.pi)
    v = (REGIAO_TRONCO['ymax'] + 0.03 - Pc[..., 1]) / (REGIAO_TRONCO['ymax'] - REGIAO_TRONCO['ymin'] + 0.06)
    return np.clip(0.5 + u * 0.5, 0.501, 0.999), np.clip(v, 0.001, 0.999)


def arrays_peitoral(Q, NQ, T, cz, celula_uv=None):
    """Vértices não compartilhados por triângulo + UV cilíndrica (sem costura). Devolve (P, UVobj, T)."""
    T = T.copy()
    fn = np.cross(Q[T[:, 1]] - Q[T[:, 0]], Q[T[:, 2]] - Q[T[:, 0]])
    inv = (fn * NQ[T].mean(1)).sum(1) < 0
    T[inv] = T[inv][:, [0, 2, 1]]                                  # anti-horário = normal p/ fora
    Pc = Q[T]                                                      # (m,3,3)
    u, v = uv_cilindrico(Pc, cz)
    for k in range(len(T)):                                        # triângulo atravessando a costura de trás
        if u[k].max() - u[k].min() > 0.25:
            u[k] = np.where(u[k] < 0.75, 0.999, u[k])
    P = Pc.reshape(-1, 3)
    if celula_uv is not None:                                      # remapeia p/ uma célula do atlas
        (u0, u1), (v0, v1) = celula_uv
        u = u0 + (u - 0.5) / 0.5 * (u1 - u0)
        v = v0 + v * (v1 - v0)
    UVobj = np.c_[u.ravel(), 1 - v.ravel()]
    Tn = np.arange(len(P)).reshape(-1, 3)
    return P, UVobj, Tn


def construir(mg, sk, mg_ref=None):
    mg_ref = mg_ref or mg
    G = {m['grupo']: m for m in malha.ler(mg_ref)}
    pp, _, _ = malha.vertices(mg_ref, G[9])
    pad = esqueleto.aplicar(sk['mundo'][0x61], np.array(pp))
    Psc, UV, T = ombreiras_sc()
    eixo = np.array([-0.115, -0.864, -0.49])
    R = encaixe.rot_a_para_b(eixo, np.array([1.0, 0, 0]))
    Q = (Psc * encaixe.ESCALA_SC * ESCALA_OMBREIRA) @ R
    Pd = Q - Q.mean(0) + pad.mean(0) + DESLOC_OMBREIRA
    M = np.array([-1.0, 1, 1])
    Pe = Pd * M
    mg = peca(mg, 9, 0x61, True, sk, Pd, T, UV)
    mg = peca(mg, 6, 0x82, False, sk, Pe, T[:, [0, 2, 1]], UV)
    partes, cz = peitoral_partes(mg_ref)
    # gola de malha (célula C do atlas), dividida em metades esq./dir. junto das placas do peito
    Pg, Tg = gola(mg_ref, cz)
    cg = Pg[Tg].mean(1)
    for g, osso, Q, NQ, Tp in partes:
        P1, U1, T1 = arrays_peitoral(Q, NQ, Tp, cz)
        if g in (11, 12):
            lado = cg[:, 0] >= 0 if g == 12 else cg[:, 0] < 0
            limite = {11: 289, 12: 286}[g] - len(Tp)
            lo, hi, melhor = 0.002, 0.06, None
            for _ in range(18):
                mid = (lo + hi) / 2
                Qg, Tq = simplificar(Pg, Tg[lado], mid)
                if len(Tq) <= limite:
                    melhor = (Qg, Tq); hi = mid
                else:
                    lo = mid
            Qg, Tq = melhor
            P2, U2, T2 = arrays_peitoral(Qg, normais_externas(Qg, Tq, cz), Tq, cz, celula_uv=((0.0, 0.25), (0.75, 1.0)))
            assert len(T1) + len(T2) <= {11: 289, 12: 286}[g], (g, len(T1), len(T2))
            P1 = np.vstack([P1, P2]); U1 = np.vstack([U1, U2]); T1 = np.vstack([T1, T2 + len(T1) * 3])
        mg = peca(mg, g, osso, False, sk, P1, T1, U1)
    # tiras de couro (grupo 18, antes placa de canela; osso da pelve, espaço do modelo)
    Pp, Up, Tp = pteruges()
    mg = peca(mg, 18, 0x1, False, sk, Pp, Tp, Up)
    # braçadeiras (8/13, espaço local dos ossos ArmArmor) e grevas (16/19, placa de metal; modelo)
    mg = _editar_posicoes(mg, mg_ref, 8, bracadeira)
    mg = _editar_posicoes(mg, mg_ref, 13, bracadeira)
    mg = _editar_posicoes(mg, mg_ref, 16, greva(+1), so_material=5)
    mg = _editar_posicoes(mg, mg_ref, 19, greva(-1), so_material=5)
    return mg


# ---------------------------------------------------------------- braçadeiras e grevas (edição no lugar)
def _editar_posicoes(mg, mg_ref, grupo, func, so_material=None):
    """Altera posições dos vértices existentes do grupo (sem trocar descritor/normais/UV)."""
    import struct
    mg = bytearray(mg)
    for m in malha.ler(mg_ref):
        if m['grupo'] != grupo:
            continue
        p0 = m['ents'][0]['pos']
        if so_material is not None and (struct.unpack_from('<I', mg_ref, p0 - 0x24)[0] >> 16) != so_material:
            continue
        e0 = m['ents'][0]['alvo']; st = m['stride']
        P = np.array([struct.unpack_from('<3f', mg_ref, e0 + i * st) for i in range(m['total'])])
        Q = func(P)
        for i in range(m['total']):
            struct.pack_into('<3f', mg, e0 + i * st, *Q[i])
    return bytes(mg)


BRACADEIRA = dict(base=1.14, cotovelo=0.22)     # alargamento radial; extra na ponta do cotovelo
GREVA = dict(base=1.10, joelho=0.22, altura=1.10)


def bracadeira(P):
    """Espaço local do osso ArmArmor*: eixo do antebraço = y (0 = cotovelo, ~0.44 = punho)."""
    c = np.array([np.median(P[:, 0]), 0, np.median(P[:, 2])])
    t = np.clip(P[:, 1] / 0.44, 0, 1)
    f = BRACADEIRA['base'] + BRACADEIRA['cotovelo'] * (1 - t) ** 2
    Q = P.copy()
    Q[:, [0, 2]] = c[[0, 2]] + (P[:, [0, 2]] - c[[0, 2]]) * f[:, None]
    return Q


def greva(lado):
    """Espaço do modelo: eixo da perna do joelho (0.768) ao tornozelo (0.118)."""
    xj = 0.136 * lado
    def f(P):
        y = P[:, 1]
        t = np.clip((y - 0.118) / (0.768 - 0.118), 0, 1)        # 0 tornozelo .. 1 joelho
        eixo = np.c_[np.full(len(P), xj), y, -0.061 * t + 0.024 * (1 - t)]
        topo = y.max()
        fr = GREVA['base'] + GREVA['joelho'] * np.clip((t - 0.6) / 0.4, 0, 1) ** 2
        Q = eixo + (P - eixo) * np.c_[fr, np.ones(len(P)), fr]
        # prolonga o topo para cobrir o joelho (estica a parte de cima)
        alto = y > 0.35
        Q[alto, 1] = 0.35 + (y[alto] - 0.35) * GREVA['altura']
        return Q
    return f


# ---------------------------------------------------------------- tiras de couro (pteruges)
def pteruges(n=13, raio=0.235, cz=-0.03, y0=1.40, comp=0.30, larg=0.065, abertura=0.05):
    """Tiras retangulares em volta da cintura (frente e lados), espaço do modelo. UV na célula B do atlas."""
    P, UV, T = [], [], []
    for k in range(n):
        a = np.radians(-125 + 250 * k / (n - 1))                 # 0 = frente (-z)
        d = np.array([np.sin(a), 0, -np.cos(a)]); lat = np.array([np.cos(a), 0, np.sin(a)])
        b = len(P)
        for j, (y, r) in enumerate(((y0, raio), (y0 - comp / 2, raio + abertura * 0.5), (y0 - comp, raio + abertura))):
            for s in (-1, 1):
                P.append(np.array([0, y, cz]) + d * r + lat * s * larg / 2)
                UV.append((0.25 + (0.5 + 0.45 * s) * 0.25, 1 - (0.5 + 0.25 * j / 2 * 0.9 + 0.01)))
        for j in range(2):
            i0 = b + 2 * j
            T += [[i0, i0 + 1, i0 + 3], [i0, i0 + 3, i0 + 2]]
    P = np.array(P); UV = np.array(UV); T = np.array(T)
    # garante ordem anti-horária com normal para fora
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    rad = P[T].mean(1) - np.array([0, 0, cz]); rad[:, 1] = 0
    inv = (fn * rad).sum(1) < 0
    T[inv] = T[inv][:, [0, 2, 1]]
    # face de trás (vista de dentro da saia)
    T = np.vstack([T, T[:, [0, 2, 1]]])
    return P, UV, T


# ---------------------------------------------------------------- gola de malha
REGIAO_GOLA = dict(xmax=0.17, ymin=1.92, ymax=2.07)


def gola(mg_ref, cz):
    Ps, Ts, base = [], [], 0
    r = REGIAO_GOLA
    for m in malha.ler(mg_ref):
        if m['grupo'] != 21 or m['stride'] != 40:
            continue
        p, _, i = malha.vertices(mg_ref, m)
        P = np.array(p); T = np.array(i).reshape(-1, 3)
        c = P[T].mean(1)
        sel = (np.abs(c[:, 0]) < r['xmax']) & (c[:, 1] > r['ymin']) & (c[:, 1] < r['ymax'])
        if sel.any():
            Ps.append(P); Ts.append(T[sel] + base); base += len(P)
    P = np.vstack(Ps); T = np.vstack(Ts)
    usados = np.unique(T); mapa = -np.ones(len(P), int); mapa[usados] = np.arange(len(usados))
    P, T = P[usados], mapa[T]
    N = normais_externas(P, T, cz)
    return P + N * 0.012, T
