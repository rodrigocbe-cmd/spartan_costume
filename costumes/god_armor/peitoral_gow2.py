"""Peitoral da Armadura de Deus com o DESENHO DO GoW II sobre o colete do Dominus (pedido de 2026-11-22).

Referências: referencias/god_armor/cota_de_malha_bracos_pernas.jpg (arte oficial do GoW II) e peitoral.jpg.
Desenho: couraça roxo-escura com músculos (relevo do próprio colete do Dominus), gola dourada, um gancho
(chifre) dourado no alto de cada peitoral, flor-de-lis no centro, garras douradas sob os peitorais, faixa
grande em zigue-zague descendo pelo lado ESQUERDO do Kratos (x < 0), filete dourado na borda de baixo e faixa
grega na cintura. As costas ficam com o desenho do Dominus, só no roxo.

Como: cada texel da textura do colete (TXFC6E37EC, uma ilha só: frente embaixo do buraco do pescoço, costas
em cima, de cabeça para baixo) recebe a sua posição 3D (rasterização dos triângulos do MG do Dominus); o
desenho é feito numa tela 2D em VISTA DE FRENTE (metros) e amostrado em cada texel da frente.
Saídas (lidas por montagem.py, que troca as texturas copiadas do R_HERO06):
  texturas_montagem/TXFC6E37EC.E1F4DA0C.png (cor), TX9DC6B004.C880D376.png (normal: x no alfa, y no verde),
  TX08D5DF6D.A3494A18.png (especular).
uso: python -I costumes/god_armor/peitoral_gow2.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
import malha, montar_heroi   # noqa: E402

ORIG = os.path.join(RAIZ, 'original', 'R_HERO06', 'png')
SAIDA = os.path.join(AQUI, 'texturas_montagem')
COR, NORMAL, ESPEC = 'TXFC6E37EC.E1F4DA0C', 'TX9DC6B004.C880D376', 'TX08D5DF6D.A3494A18'

BASE = np.array([40, 35, 34]) / 255.0          # preto da couraça (peitoral original do port; = PRETO das ombreiras/cinturão)
OURO = np.array([0.80, 0.58, 0.24])            # mesmo dourado das ombreiras (texturas_armadura.OURO)
OURO_ESC = np.array([0.30, 0.20, 0.09])
ZONA = dict(x=0.205, y0=1.575, y1=2.13)        # área da frente redesenhada (o resto mantém o desenho do Dominus)
K = 2000                                       # px/m da tela do desenho
PEITO_Y0, PEITO_Y1 = 1.60, 2.10                # faixa de altura do desenho do peito
BORDA_DOMINUS_PX = 22                          # dourado do Dominus a menos disso da borda da ilha fica (bordas)
GOLA_PX = 16                                   # largura da gola em texels (~2 cm)
X0, Y1 = -0.32, 2.20
TELA = (int(0.64 * K), int(0.80 * K))


def mapa_texels(N=1024):
    """posição 3D de cada texel (NaN fora da ilha) e normal geométrica."""
    h = montar_heroi.heroi('06')
    pos = np.full((N, N, 3), np.nan)
    nrm = np.zeros((N, N, 3))
    for p in h['pecas']:
        if not (p['grupo'] == 17 and p['material'] in (6, 7)):
            continue
        _, uv, _ = malha.vertices(h['mg'], p['m'])
        uv = np.array(uv) % 1 * N
        P = p['P']
        for t in p['T']:
            if len(set(t)) < 3:
                continue
            a, b, c = uv[t]
            x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int)
            x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int)
            xs, ys = np.meshgrid(np.arange(max(x0, 0), min(x1 + 1, N)), np.arange(max(y0, 0), min(y1 + 1, N)))
            q = np.stack([xs.ravel() + .5, ys.ravel() + .5], 1)
            M = np.array([b - a, c - a]).T
            if abs(np.linalg.det(M)) < 1e-9:
                continue
            l = np.linalg.solve(M, (q - a).T).T
            l0 = 1 - l[:, 0] - l[:, 1]
            ok = (l0 >= -0.02) & (l[:, 0] >= -0.02) & (l[:, 1] >= -0.02)
            pts = l0[ok, None] * P[t[0]] + l[ok, 0, None] * P[t[1]] + l[ok, 1, None] * P[t[2]]
            n = np.cross(P[t[1]] - P[t[0]], P[t[2]] - P[t[0]])
            pos[ys.ravel()[ok], xs.ravel()[ok]] = pts
            nrm[ys.ravel()[ok], xs.ravel()[ok]] = n / (np.linalg.norm(n) + 1e-12)
    return pos, nrm


# --- desenho do peitoral ORIGINAL do GoW II (port: referencias/god_armor/port_gow2_god_armor_1_1, material
# chest_m, cor TXA950000B): transferido em 3D — cada texel do nosso colete pega o ponto mais próximo da couraça
# do port (mesmo esqueleto/escala do Kratos). Frente: dois cães em "S" virados um para o outro, flor-de-lis,
# leques nas laterais; costas: cabeça de carneiro com chifres. Texturas do port extraídas em original/port_gow2/png.
PORT_WAD = os.path.join(RAIZ, 'referencias', 'god_armor', 'port_gow2_god_armor_1_1', 'Game', 'EXEC', 'WAD', 'PS4_LE',
                        'R_HERO00.WAD')
PORT_COR = os.path.join(RAIZ, 'original', 'port_gow2', 'png', 'TXA950000B.C0570000.png')
PORT_MATERIAL = 11                              # chest_m do port
PORT_DIST_MAX = 0.02                            # m (no espaço ângulo×altura)
PORT_Y_TOPO, PORT_Y_BASE, NOSSO_Y_BASE = 2.06, 1.44, 1.60
CIL_CZ, CIL_R = 0.0, 0.17                       # eixo do tronco (z) e raio médio p/ converter ângulo em m


def mapa_port(N=(1024, 512)):
    """posição 3D de cada texel da couraça do port (textura reduzida a N)."""
    h = montar_heroi.heroi('00', caminho=PORT_WAD)
    W, H = N
    pos = np.full((H, W, 3), np.nan)
    for p in h['pecas']:
        if not (p['grupo'] == 21 and p['material'] == PORT_MATERIAL and len(p['T'])):
            continue
        _, uv, _ = malha.vertices(h['mg'], p['m'])
        uv = (np.array(uv) % 1) * np.array([W, H])
        P = p['P']
        for t in p['T']:
            if len(set(t)) < 3:
                continue
            a, b, c = uv[t]
            x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int)
            x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int)
            if x1 - x0 > W / 2 or y1 - y0 > H / 2:
                continue
            xs, ys = np.meshgrid(np.arange(max(x0, 0), min(x1 + 1, W)), np.arange(max(y0, 0), min(y1 + 1, H)))
            q = np.stack([xs.ravel() + .5, ys.ravel() + .5], 1)
            M = np.array([b - a, c - a]).T
            if abs(np.linalg.det(M)) < 1e-9:
                continue
            l = np.linalg.solve(M, (q - a).T).T
            l0 = 1 - l[:, 0] - l[:, 1]
            ok = (l0 >= -0.02) & (l[:, 0] >= -0.02) & (l[:, 1] >= -0.02)
            pos[ys.ravel()[ok], xs.ravel()[ok]] = (l0[ok, None] * P[t[0]] + l[ok, 0, None] * P[t[1]]
                                                   + l[ok, 1, None] * P[t[2]])
    return pos


def desenho_port(pos_nosso):
    """(ouro 0..1, tom do ouro relativo) para cada texel do nosso colete, tirados da couraça do port."""
    from scipy.spatial import cKDTree
    pp = mapa_port()
    cor = np.asarray(Image.open(PORT_COR).convert('RGB').resize((pp.shape[1], pp.shape[0]), Image.LANCZOS)).astype(np.float32) / 255
    mx, mn = cor.max(-1), cor.min(-1)
    s = (mx - mn) / np.maximum(mx, 1e-3)
    L = cor @ np.array([0.299, 0.587, 0.114])
    r, g, b = cor[..., 0], cor[..., 1], cor[..., 2]
    ouro = np.clip((s - 0.30) / 0.15, 0, 1) * np.clip((L - 0.12) / 0.08, 0, 1) * (r > b * 1.4)
    ouro = ndimage.gaussian_filter(ouro, 0.6)
    ok = ~np.isnan(pp[..., 0])
    # correspondência por (ângulo em volta do tronco, altura): não depende da espessura de cada couraça
    def cil(Q):
        return np.c_[np.arctan2(Q[:, 0], -(Q[:, 2] - CIL_CZ)) * CIL_R, Q[:, 1]]
    arv = cKDTree(cil(pp[ok]))
    vo, vl = ouro[ok], L[ok]
    alvo = ~np.isnan(pos_nosso[..., 0])
    Q = pos_nosso[alvo].copy()
    # altura: a couraça do original vai do pescoço (PORT_Y_TOPO) a PORT_Y_BASE; a nossa termina no filete
    Q[:, 1] = PORT_Y_TOPO - (PORT_Y_TOPO - Q[:, 1]) * (PORT_Y_TOPO - PORT_Y_BASE) / (PORT_Y_TOPO - NOSSO_Y_BASE)
    d, i = arv.query(cil(Q), k=4)
    w = 1 / np.maximum(d, 1e-4)
    w = w / w.sum(1, keepdims=True)
    o_out = np.zeros(pos_nosso.shape[:2], np.float32)
    l_out = np.zeros(pos_nosso.shape[:2], np.float32)
    perto = (d[:, 0] < PORT_DIST_MAX).astype(np.float32)
    o_out[alvo] = (vo[i] * w).sum(1) * perto
    l_out[alvo] = (vl[i] * w).sum(1)
    ref = np.median(vl[vo > 0.8]) if (vo > 0.8).any() else 0.5
    return o_out, l_out / max(ref, 1e-3)


def _m(x, y):
    return ((x - X0) * K, (Y1 - y) * K)


# --- desenho DECALCADO da referência de frente (referencias/god_armor/peitoral.jpg), em pixels dessa imagem ---
# (pedido de 2026-11-22: "extraia o desenho do original e desenhe por cima"). Esterno em x = 600, ponta do V da
# gola em y = 642; imagem: direita = lado ESQUERDO do Kratos (x < 0 no modelo).
DEC_CENTRO, DEC_GOLA = 600.0, 642.0
DEC_ESCALA_X = 0.00080                         # m/px na horizontal
DEC_ALTURAS = [(642, 2.015), (900, 1.815), (1300, 1.590)]   # (y na referência, Y no modelo): V da gola, patas, filete
# cão do lado direito do Kratos (lado esquerdo da imagem): corpo em C, cabeça no alto com o focinho para o
# centro, boca aberta e presa para baixo; o do outro lado é o espelho
DEC_CAO = [(442, 638), (432, 655), (423, 680), (416, 710), (415, 735), (419, 758), (428, 778), (442, 790), (458, 792),
           (470, 785), (478, 770), (484, 752), (472, 762), (460, 770), (448, 764), (440, 748), (438, 728), (443, 712),
           (453, 700), (468, 692), (490, 688), (506, 690), (512, 700), (515, 712), (520, 698), (527, 685), (534, 676),
           (537, 664), (533, 655), (522, 650), (505, 648), (488, 650), (470, 646), (455, 640)]
DEC_OLHO = (512, 664, 4.5, 3.5)
# pata sob o peitoral (faixa vinda do lado, dobrando para baixo até a garra)
DEC_PATA = [(375, 852), (400, 856), (440, 858), (480, 858), (502, 861), (522, 870), (537, 889), (552, 918), (540, 916),
            (524, 900), (510, 888), (494, 882), (470, 885), (440, 886), (400, 889), (378, 880)]
DEC_PATA2 = [(505, 885), (522, 902), (528, 935), (515, 918), (500, 898)]          # 2ª garra (para baixo)
# flor-de-lis no esterno
DEC_FLOR = [[(598, 722), (606, 745), (607, 775), (600, 815), (593, 840), (588, 815), (585, 775), (588, 745)],
            [(512, 797), (535, 798), (560, 812), (585, 835), (592, 858), (575, 850), (550, 835), (528, 815)],
            [(651, 806), (640, 815), (620, 830), (600, 850), (592, 858), (598, 838), (620, 818), (638, 808)]]
# parte de baixo (assimétrica): faixa lateral do lado esquerdo do Kratos com o "Z" e o raio diagonal,
# faixa de baixo que vira o filete da borda, faixa lateral do lado direito
DEC_BAIXO = [
    [(840, 900), (875, 900), (875, 1160), (830, 1150), (800, 1140), (760, 1150), (720, 1175), (690, 1200), (660, 1215),
     (645, 1222), (670, 1195), (700, 1165), (735, 1135), (745, 1105), (765, 1072), (790, 1085), (800, 1050),
     (808, 1000), (800, 960), (820, 920)],
    [(884, 1165), (870, 1190), (830, 1220), (780, 1245), (740, 1258), (700, 1268), (650, 1285), (600, 1295), (520, 1298),
     (470, 1288), (420, 1262), (380, 1222), (366, 1235), (410, 1278), (465, 1302), (520, 1312), (610, 1308),
     (660, 1298), (710, 1285), (760, 1270), (810, 1250), (850, 1228), (888, 1195)],
    [(356, 885), (372, 885), (380, 1000), (386, 1100), (394, 1180), (380, 1200), (368, 1100), (360, 1000)],
]
ESPELHO_Y = 1.80               # acima: o lado esquerdo do Kratos é o espelho do direito decalcado


def _dec(x, y):
    """pixel da referência -> (X, Y) do modelo."""
    ya, Ya = zip(*DEC_ALTURAS)
    return (-(x - DEC_CENTRO) * DEC_ESCALA_X, float(np.interp(y, ya, Ya)))


def desenho_decalque():
    img = Image.new('L', TELA, 0)
    d = ImageDraw.Draw(img)

    def poli(pts, espelhar):
        q = [_dec(x, y) for x, y in pts]
        d.polygon([_m(X, Y) for X, Y in q], fill=255)
        if espelhar:
            d.polygon([_m(-X, Y) for X, Y in q], fill=255)
    poli(DEC_CAO, True)
    poli(DEC_PATA, True)
    poli(DEC_PATA2, True)
    for f in DEC_FLOR:
        poli(f, False)
    for b in DEC_BAIXO:
        poli(b, False)
    x, y, rx, ry = DEC_OLHO
    for s in (1, -1):
        X, Y = _dec(x, y)
        X *= s
        (a0, b0), (a1, b1) = _m(X - rx * DEC_ESCALA_X, Y + ry * 0.00078), _m(X + rx * DEC_ESCALA_X, Y - ry * 0.00078)
        d.ellipse([a0, b0, a1, b1], fill=0)
    return np.asarray(img).astype(np.float32) / 255


def desenho():
    """Tela em vista de frente: máscara do dourado (0..1) e máscara das linhas escuras da grega."""
    img = Image.new('L', TELA, 0)
    d = ImageDraw.Draw(img)

    def poli(pts, espelhar=True):
        d.polygon([_m(x, y) for x, y in pts], fill=255)
        if espelhar:
            d.polygon([_m(-x, y) for x, y in pts], fill=255)

    def linha(pts, larg, espelhar=True):
        for s in ((1, -1) if espelhar else (1,)):
            q = [_m(s * x, y) for x, y in pts]
            d.line(q, fill=255, width=int(larg * K), joint='curve')
            for c in q:
                r = larg * K / 2
                d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255)

    # desenho DECALCADO da referência (cães, flor-de-lis, patas, faixas de baixo): ver desenho_decalque()
    arte = desenho_decalque()
    # filete dourado da borda de baixo (acima da grega)
    d.rectangle([_m(-0.30, 1.600), _m(0.30, 1.584)], fill=255)
    ouro = np.maximum(np.asarray(img).astype(np.float32) / 255, arte)
    # grega na faixa da cintura (linhas escuras sobre o dourado): meandro com período P
    grega = np.zeros(TELA[::-1], np.float32)
    P = 0.040
    yb0, yb1 = 1.515, 1.570
    g = Image.new('L', TELA, 0)
    dg = ImageDraw.Draw(g)
    lw = max(2, int(0.0045 * K))
    x = -0.30
    while x < 0.30:
        a, b = x, x + P
        h = yb1 - yb0
        pts = [(a, yb0 + 0.15 * h), (a, yb1 - 0.15 * h), (a + 0.75 * P, yb1 - 0.15 * h), (a + 0.75 * P, yb0 + 0.40 * h),
               (a + 0.30 * P, yb0 + 0.40 * h), (a + 0.30 * P, yb0 + 0.62 * h), (a + 0.50 * P, yb0 + 0.62 * h)]
        dg.line([_m(*p) for p in pts], fill=255, width=lw)
        dg.line([_m(a, yb0 + 0.15 * h), _m(b, yb0 + 0.15 * h)], fill=255, width=lw)
        x = b
    grega = np.asarray(g).astype(np.float32) / 255
    return ndimage.gaussian_filter(ouro, 1.2), ndimage.gaussian_filter(grega, 0.8)


def amostrar(tela, X, Y):
    cx = np.clip(((X - X0) * K).astype(int), 0, TELA[0] - 1)
    cy = np.clip(((Y1 - Y) * K).astype(int), 0, TELA[1] - 1)
    return tela[cy, cx]


def main():
    """Colete do Dominus INTEIRO (cores, bordas e faixas douradas, vermelho, costas, relevo); só o desenho do peito
    (as garras douradas do miolo da frente) é trocado pelo desenho do peito do GoW II (cães + flor-de-lis)."""
    os.makedirs(SAIDA, exist_ok=True)
    pos, nrm = mapa_texels()
    valido = ~np.isnan(pos[..., 0])
    P = np.nan_to_num(pos)
    X, Y, Z = P[..., 0], P[..., 1], P[..., 2]
    frente = valido & (Z < -0.02)
    borda = ndimage.distance_transform_edt(valido) < BORDA_DOMINUS_PX
    # miolo da frente = onde fica o desenho do peito (fora das bordas e acima da faixa da cintura do Dominus)
    miolo = frente & ~borda & (Y > PEITO_Y0) & (Y < PEITO_Y1)

    cor = np.asarray(Image.open(os.path.join(ORIG, COR + '.png')).convert('RGBA')).astype(np.float32) / 255
    rgb, al = cor[..., :3], cor[..., 3]
    L = rgb @ np.array([0.299, 0.587, 0.114])
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = (mx - mn) / np.maximum(mx, 1e-3)
    ouro_dom = np.clip((s - 0.30) / 0.15, 0, 1) * np.clip((L - 0.18) / 0.1, 0, 1)      # dourado do Dominus
    ouro_dom = ndimage.gaussian_filter(ouro_dom, 1.0)
    # desenho antigo do peito (garras + o contorno escuro delas), só no miolo da frente
    velho = ndimage.binary_dilation(ouro_dom > 0.25, iterations=3) & miolo
    velho = ndimage.gaussian_filter(velho.astype(np.float32), 1.5)

    def preencher(c, m, sigma=8, evitar=None):
        """Preenche a área m com a média da vizinhança fora dela (apaga o desenho velho)."""
        w = 1 - np.clip(m * 1.5, 0, 1)
        if evitar is not None:
            w = w * (1 - evitar)
        if c.ndim == 3:
            w = w[..., None]
        num = ndimage.gaussian_filter(c * w, (sigma, sigma, 0) if c.ndim == 3 else sigma)
        den = ndimage.gaussian_filter(w, (sigma, sigma, 0) if c.ndim == 3 else sigma)
        return num / np.maximum(den, 1e-3)
    # couraça preta no lugar das garras, com o "grão" da textura do próprio colete
    Lb = ndimage.gaussian_filter(L, 2.5)
    grao = np.clip(L / np.maximum(Lb, 1e-3), 0.85, 1.15)
    grao = np.where(ouro_dom > 0.2, 1.0, grao)
    todo_ouro = np.clip(ndimage.gaussian_filter((ouro_dom > 0.15).astype(np.float32), 2.0) * 3, 0, 1)
    liso = preencher(rgb, velho, 10, evitar=todo_ouro) * grao[..., None]
    base = rgb * (1 - velho[..., None]) + liso * velho[..., None]

    # desenho do peito do GoW II (cães + flor-de-lis), no dourado do próprio Dominus
    ouro_port, tom_port = desenho_port(pos)
    novo = ouro_port * miolo
    novo = ndimage.gaussian_filter(novo, 0.6)
    ouro_cor = np.median(rgb[(ouro_dom > 0.8) & valido], 0)
    tom = ouro_cor[None, None] * np.clip(tom_port, 0.4, 1.5)[..., None] * grao[..., None]
    final = base * (1 - novo[..., None]) + tom * novo[..., None]
    final = np.where(valido[..., None], final, rgb)
    Image.fromarray((np.concatenate([np.clip(final, 0, 1), al[..., None]], -1) * 255 + .5).astype(np.uint8),
                    'RGBA').save(os.path.join(SAIDA, COR + '.png'))

    # normal: o do Dominus; nas garras antigas o relevo é preenchido pela vizinhança (músculos ficam), e o relevo
    # do desenho novo é somado
    nm = np.asarray(Image.open(os.path.join(ORIG, NORMAL + '.png')).convert('RGBA')).astype(np.float32) / 255
    nx, ny = nm[..., 3] - 0.5, nm[..., 1] - 0.5
    nx = nx * (1 - velho) + preencher(nx, velho, 6) * velho
    ny = ny * (1 - velho) + preencher(ny, velho, 6) * velho
    Hd = ndimage.gaussian_filter(ouro_dom, 2.0)
    gx, gy = np.gradient(Hd, axis=1), np.gradient(Hd, axis=0)
    m = (np.abs(gx) + np.abs(gy)) > 0.02
    sx = np.sign(np.corrcoef(gx[m], nm[..., 3][m] - 0.5)[0, 1])
    sy = np.sign(np.corrcoef(gy[m], nm[..., 1][m] - 0.5)[0, 1])
    ganho = 0.5 / max(np.percentile(np.abs(np.r_[gx[m], gy[m]]), 95), 1e-3) *         np.percentile(np.abs(np.r_[nm[..., 3][m], nm[..., 1][m]] - 0.5), 95)
    Hn = ndimage.gaussian_filter(novo, 2.0) + ndimage.gaussian_filter((np.clip(tom_port, 0.3, 1.6) - 1) * novo, 1.0) * 0.5
    hx, hy = np.gradient(Hn, axis=1), np.gradient(Hn, axis=0)
    nx = nx + sx * hx * ganho * 2
    ny = ny + sy * hy * ganho * 2
    print('normal: sinais', sx, sy, 'ganho %.2f' % ganho)
    out = nm.copy()
    out[..., 3] = np.where(valido, np.clip(nx + 0.5, 0, 1), nm[..., 3])
    out[..., 1] = np.where(valido, np.clip(ny + 0.5, 0, 1), nm[..., 1])
    Image.fromarray((out * 255 + .5).astype(np.uint8), 'RGBA').save(os.path.join(SAIDA, NORMAL + '.png'))

    # especular: o do Dominus; garras antigas -> couraça, desenho novo -> brilho do dourado do Dominus
    sp = np.asarray(Image.open(os.path.join(ORIG, ESPEC + '.png')).convert('RGBA')).astype(np.float32) / 255
    spc = sp[..., :3].mean(-1)
    sp_ouro = np.median(spc[valido & (ouro_dom > 0.7)])
    spc = spc * (1 - velho) + preencher(spc, velho, 6) * velho
    spc = spc * (1 - novo) + sp_ouro * novo
    sp[..., 0] = sp[..., 1] = sp[..., 2] = np.clip(spc, 0, 1)
    Image.fromarray((sp * 255 + .5).astype(np.uint8), 'RGBA').save(os.path.join(SAIDA, ESPEC + '.png'))
    print('ok')


if __name__ == '__main__':
    main()
