"""Texturas da Armadura do Deus da Guerra (tom "meio-termo": dourado um pouco mais escuro e gasto,
pátina leve). Gera em costumes/god_armor/texturas/R_HERO00/:

- TXE90D274D (material fleece, 1024²) = ATLAS das peças novas:
    quadrante sup. esquerdo  = ombreira de carneiro (SC ampliado + metal procedural)
    metade direita           = peitoral (projeção cilíndrica em volta do tronco)
- TX3DEC657A (braçadeiras/cinto/correntes): tudo dourado (elos claros sobre fundo dourado escuro)
- TXE8CC240F / TX2E5E7D75 / TX5F3FCC5C (normal, especular, oclusão do fleece): gerados do atlas
- TXE3FF895B (botas/grevas + asas): dourado
- TX4D95EEC1 / TX5512508B (saia): vermelho mantido, grega e detalhes claros dourados
Pele e tatuagem: originais (como no GoW II).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'costumes', 'dark_odyssey'))
import recolorir as R   # noqa: E402  (funções hsv, lum, tingir, pecas, suave, carregar)

SAIDA = os.path.join(AQUI, 'texturas', 'R_HERO00')
SC = os.path.join(RAIZ, 'referencias', 'god_armor', 'soulcalibur_bd', 'kratos_2p_god_armor')
OURO = np.array([0.80, 0.58, 0.24])        # meio-termo
OURO_ESC = np.array([0.20, 0.14, 0.07])
PATINA = np.array([0.33, 0.40, 0.28])
rng = np.random.default_rng(7)


def metal(h, w, seed=7):
    r = np.random.default_rng(seed)
    n = sum(ndimage.gaussian_filter(r.standard_normal((h, w)), s) * k for s, k in ((1.2, 0.5), (4, 1.0), (12, 1.5)))
    n /= np.abs(n).max()
    ris = ndimage.gaussian_filter(r.standard_normal((h, w)) * (r.random((h, w)) > 0.995), (0.6, 12))
    ris /= np.abs(ris).max() + 1e-9
    return n, ris


def colorir(L, n, ris, seed=3):
    r = np.random.default_rng(seed)
    Lc = np.clip(0.18 + 0.8 * L + 0.06 * n + 0.05 * ris, 0, 1)
    cor = OURO_ESC + (OURO - OURO_ESC) * (Lc[..., None] ** 1.1)
    H, W = L.shape
    p = np.clip((0.45 - Lc) / 0.45, 0, 1) * np.clip(ndimage.gaussian_filter(r.random((H, W)), 30) * 3 - 1.2, 0, 1)
    return cor * (1 - 0.6 * p[..., None]) + PATINA * Lc[..., None] * 0.6 * p[..., None]


# vermelho e preto das ombreiras = tons do colete do Dominus (pedido do usuário; TXFC6E37EC: vermelho mediana
# (82,25,16), preto ~(33,28,27)..(60,56,57))
VERMELHO = np.array([82, 25, 16]) / 255.0
CHIFRE = (0.45, 0.54, 0.27)          # chifre em espiral na textura da ombreira do SC: centro (u, v_png), raio
PRETO = np.array([40, 35, 34]) / 255.0


def regioes_ombreira(tam, png='09e06a70a8d42785d872cffe.png'):
    """Máscaras suaves (vermelho, preto) de uma textura do SC: vermelho = áreas cor de vinho (cor puxada p/ o
    vermelho, suavizada); preto = sombras fundas; o resto é metal."""
    sc = np.asarray(Image.open(os.path.join(SC, png)).convert('RGB')).astype(np.float32)
    sig = 2.0 * sc.shape[0] / 64
    r, g, b = [ndimage.gaussian_filter(sc[..., i], sig) for i in range(3)]
    L = 0.299 * r + 0.587 * g + 0.114 * b
    verm = ((r / (g + 1) > 1.38) & (L < 115)).astype(np.float32)
    preto = ((L < 48) & (verm < 0.5)).astype(np.float32)
    amp = lambda m: ndimage.gaussian_filter(
        np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((tam, tam), Image.BICUBIC)).astype(np.float32) / 255, 2.0)
    return amp(verm), amp(preto)


def ombreira(tam=512, png='09e06a70a8d42785d872cffe.png'):
    ram = Image.open(os.path.join(SC, png)).convert('RGB')
    ram = ram.resize((tam, tam), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.3))
    L = np.asarray(ram).astype(np.float32) @ [0.299, 0.587, 0.114] / 255
    L = np.clip((L - np.percentile(L, 2)) / (np.percentile(L, 98) - np.percentile(L, 2)), 0, 1)
    L = np.clip(L + (L - ndimage.gaussian_filter(L, 10)) * 0.8, 0, 1)
    n, ris = metal(tam, tam, 7)
    ouro = colorir(L, n, ris)
    mv, mp = regioes_ombreira(tam, png)
    vermelho = VERMELHO * (0.55 + 0.9 * L)[..., None]
    preto = PRETO * (0.6 + 0.9 * L)[..., None]
    out = ouro * (1 - mv - mp)[..., None] + vermelho * mv[..., None] + preto * mp[..., None]
    if png == '09e06a70a8d42785d872cffe.png':
        # chifre em espiral do carneiro: sulcos entre os gomos em VERMELHO (arte do GoW II; teste 33)
        yy, xx = np.mgrid[0:tam, 0:tam] / tam
        chifre = np.clip((CHIFRE[2] - np.hypot(xx - CHIFRE[0], yy - CHIFRE[1])) / 0.03, 0, 1)
        sulco = (L - ndimage.gaussian_filter(L, tam * 0.025)) < -0.09
        ms = ndimage.gaussian_filter(sulco.astype(np.float32), 1.2) * chifre
        ms = np.clip(ms * 1.6, 0, 1)[..., None]
        out = out * (1 - ms) + VERMELHO * (0.8 + 0.6 * L)[..., None] * ms
    return out


def grega(w, h):
    """Faixa com a grega (meandro) — máscara 0..1."""
    m = np.zeros((h, w))
    p = h  # período = altura da faixa
    for x0 in range(0, w, p):
        u = lambda a, b, c, d: m.__setitem__((slice(int(b * h), int(d * h)), slice(x0 + int(a * p), x0 + int(c * p))), 1)
        u(0.0, 0.0, 0.9, 0.12); u(0.78, 0.0, 0.9, 0.75); u(0.25, 0.63, 0.9, 0.75); u(0.25, 0.3, 0.37, 0.75)
        u(0.25, 0.3, 0.62, 0.42); u(0.0, 0.0, 0.12, 1.0); u(0.0, 0.88, 1.0, 1.0)
    return m


def peitoral(w=512, h=1024):
    """Projeção cilíndrica: u=0..1 em volta do tronco (frente no centro), v=0 topo .. 1 base."""
    yy, xx = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    n, ris = metal(h, w, 11)
    L = np.full((h, w), 0.52)
    # relevo: placa central (frente) e linhas de musculatura estilizadas
    frente = np.exp(-((xx - 0.5) / 0.16) ** 2)
    L += 0.10 * frente
    crista = np.exp(-((xx - 0.5) / 0.006) ** 2) * (yy < 0.75)          # aresta central
    L += 0.25 * crista
    for cx in (0.42, 0.58):                                               # arco sob o peitoral
        r = np.hypot((xx - cx) / 0.075, (yy - 0.22) / 0.13)
        L -= 0.30 * np.exp(-((r - 1.0) / 0.06) ** 2) * (yy > 0.26) * (np.abs(xx - 0.5) > 0.012)
    for k in range(3):                                                    # gomos do abdome
        L -= 0.22 * np.exp(-((yy - (0.58 + 0.08 * k)) / 0.006) ** 2) * (np.abs(xx - 0.5) < 0.09)
    # bordas escuras (trim) em cima e embaixo + grega dourada embaixo
    borda = (yy < 0.035) | (yy > 0.965)
    L = np.where(borda, 0.25, L)
    faixa = (yy > 0.86) & (yy < 0.955)
    g = np.zeros((h, w))
    gh = int(0.095 * h)
    gm = grega(w, gh)
    g[int(0.86 * h):int(0.86 * h) + gh, :] = gm[:, :w]
    L = np.where(faixa, 0.30 + 0.55 * g, L)
    L = ndimage.gaussian_filter(L, 1.0)
    return colorir(np.clip(L, 0, 1), n, ris, 5)


def couro_tira(t=256):
    """Célula B: tira de couro vermelho (u = largura, v = comprimento) com borda e rebite dourados."""
    yy, xx = np.mgrid[0:t, 0:t] / t
    n, ris = metal(t, t, 21)
    base = VERMELHO * 1.33                     # vermelho do peitoral (como as tiras do cinto; teste 30)
    L = 0.75 + 0.12 * n + 0.08 * ndimage.gaussian_filter(rng.standard_normal((t, t)), (6, 1))
    cor = base * L[..., None]
    borda = ((xx < 0.12) | (xx > 0.88)) & (yy > 0.02)
    cor[borda] = base * 0.6 * (0.9 + 0.2 * n[borda, None])
    r = np.hypot(xx - 0.5, (yy - 0.14) * 1.0)
    rebite = r < 0.11
    cor[rebite] = OURO * (0.9 - 2.5 * r[rebite, None])
    return np.clip(cor, 0, 1)


def tira_fantasma(t=256):
    """Célula B (t x t): a faixa com rebite e ponta da tanga do Fantasma (TXA6C9CFBE, eixo diagonal; mesmas
    constantes de montagem.FAIXA_UV) em pé, couro no vermelho do peitoral e metal dourado — as tiras do braço
    ficam iguais às do cinto (teste 31). A faixa ocupa x de TIRA_X0 a TIRA_X1 da célula; topo em cima."""
    rgb = np.asarray(Image.open(os.path.join(RAIZ, 'original', 'R_HERO04', 'png', 'TXA6C9CFBE.9BA0F783.png'))
                     .convert('RGB')).astype(np.float32) / 255
    T0, Pn, meia = np.array([240., 575.]), np.array([185., 870.]), 16
    comp = np.linalg.norm(Pn - T0); d = (Pn - T0) / comp; perp = np.array([d[1], -d[0]])
    w = int(t * (TIRA_X1 - TIRA_X0))
    yy, xx = np.mgrid[0:t, 0:w].astype(np.float32)
    src = T0 + (yy / (t - 1) * comp)[..., None] * d + ((xx / (w - 1) * 2 - 1) * meia)[..., None] * perp
    am = lambda c: ndimage.map_coordinates(rgb[..., c], [src[..., 1], src[..., 0]], order=1, mode='nearest')
    f = np.stack([am(c) for c in range(3)], -1)
    mx, mn = f.max(-1), f.min(-1)
    s = (mx - mn) / np.maximum(mx, 1e-3)
    L = f @ np.array([0.299, 0.587, 0.114])
    metal = (np.clip((0.30 - s) / 0.12, 0, 1) * np.clip((L - 0.12) / 0.1, 0, 1))[..., None]
    ref = np.median(L[metal[..., 0] < 0.3])
    verm = np.clip(VERMELHO * (0.45 + 0.75 * L / ref)[..., None], 0, 1)
    ouro = np.clip(OURO * 1.15 * (L / max(np.median(L[metal[..., 0] > 0.5]) if (metal > 0.5).any() else 0.5, 1e-3))[..., None], 0, 1)
    cel = np.zeros((t, t, 3)); cel[:] = VERMELHO * 0.6
    cel[:, int(t * TIRA_X0):int(t * TIRA_X0) + w] = verm * (1 - metal) + ouro * metal
    return cel


TIRA_X0, TIRA_X1 = 0.30, 0.70          # faixa na célula B (fração da largura)


def malha_aco(t=256, anel=16):
    """Célula C: cota de malha (anéis de aço escuro)."""
    yy, xx = np.mgrid[0:t, 0:t].astype(float)
    off = (np.floor(yy / anel) % 2) * anel / 2
    cx = ((xx + off) % anel) - anel / 2; cy = (yy % anel) - anel / 2
    r = np.hypot(cx, cy * 1.3)
    aneis = np.exp(-((r - anel * 0.33) / (anel * 0.09)) ** 2)
    L = 0.12 + 0.55 * aneis
    return np.clip(np.array([0.55, 0.56, 0.60]) * L[..., None], 0, 1)


def atlas():
    A = np.zeros((1024, 1024, 3))
    A[:] = OURO * 0.5
    A[0:512, 0:512] = ombreira(512)
    A[:, 512:1024] = peitoral(512, 1024)
    # quadrante sup. dir.: textura do mat_12 do SC (2ª ombreira + faixas sob o carneiro), mesmas cores
    A[0:512, 512:1024] = ombreira(512, '09df94e0bf1453566579f9b1.png')
    A[512:1024, 0:512] = colorir(np.full((512, 512), 0.6), *metal(512, 512, 13))
    A[512:768, 256:512] = couro_tira(256)          # célula B: tiras de couro (pteruges)
    A[512:768, 256:512] = tira_fantasma(256)       # ... agora com o desenho das tiras do cinto (ponta + rebite)
    A[768:1024, 0:256] = malha_aco(256)            # célula C: gola de malha
    Image.fromarray((np.clip(A, 0, 1) * 255).astype(np.uint8)).save(os.path.join(SAIDA, 'TXE90D274D.FDB1BC40.png'))
    mapas_fleece(A)


def mapas_fleece(A, t=512):
    """Normal map, especular e oclusão do material fleece gerados do PRÓPRIO atlas — os originais
    (relevo da ombreira de pele) deixavam o peitoral "rachado" e estourado de brilho no jogo."""
    L = np.asarray(Image.fromarray((np.clip(A, 0, 1) * 255).astype(np.uint8)).resize((t, t), Image.BILINEAR))
    L = L.astype(np.float32) @ [0.299, 0.587, 0.114] / 255
    h = ndimage.gaussian_filter(L, 1.2)
    gy, gx = np.gradient(h)
    k = 3.0                                                    # relevo suave
    G = np.clip(0.5 + k * gy, 0.15, 0.85); X = np.clip(0.5 - k * gx, 0.15, 0.85)
    um = np.ones_like(G)
    nrm = np.stack([um, G, np.zeros_like(G), X], -1)          # DXT5: x no alfa, y no verde
    Image.fromarray((nrm * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(SAIDA, 'TXE8CC240F.71AB6FCD.png'))
    det = h - ndimage.gaussian_filter(h, 6)
    ao = np.clip(0.88 + 2.0 * det, 0.45, 1.0)
    spec = np.clip(0.10 + 0.40 * h + 1.0 * det, 0.03, 0.6)    # especular moderado (era ~0.5 médio)
    for nome, m in (('TX5F3FCC5C.F4343C17', ao), ('TX2E5E7D75.DA8083B2', spec)):
        g = np.repeat(m[..., None], 3, -1)
        salvar(nome, g, np.ones((t, t, 1)))


def salvar(nome, rgb, a):
    out = np.concatenate([np.clip(rgb, 0, 1), a], -1)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(SAIDA, nome + '.png'))


def ouro_lum(L, ref, contraste=1.1):
    return R.tingir(L, OURO * 1.15, ref, contraste)


def recolorir_pecas():
    # braçadeiras/cinto/correntes
    rgb, al = R.carregar('TX3DEC657A.5633D663')
    L = R.lum(rgb)
    cor = R.pecas(rgb, [(0.33, 0.0, 1.0, 0.52)])               # braçadeiras dos antebraços (correntes)
    ref = np.median(L[L > 0.1])
    h, s, v = R.hsv(rgb)
    elos = (1 - R.suave(s, 0.12, 0.25)) * cor                   # elos: dourado claro sobre fundo escuro
    fundo = R.tingir(L, OURO * 0.55, ref, 1.3)
    elo = ouro_lum(L, ref, 1.0)
    out = (fundo * (1 - elos[..., None]) + elo * elos[..., None]) * cor[..., None]
    out += ouro_lum(L, ref, 1.2) * (1 - cor[..., None])
    salvar('TX3DEC657A.5633D663', out, al)
    # botas / grevas + asas
    rgb, al = R.carregar('TXE3FF895B.EF07B012')
    L = R.lum(rgb)
    salvar('TXE3FF895B.EF07B012', ouro_lum(L, np.median(L[L > 0.05]), 1.0), al)
    # saia: vermelho mantido, partes claras (grega/rebites) douradas
    for n in ('TX4D95EEC1.E6645096', 'TX5512508B.F9EA0D02'):
        rgb, al = R.carregar(n)
        h, s, v = R.hsv(rgb)
        L = R.lum(rgb)
        claro = R.suave(L, 0.30, 0.50) * (1 - R.suave(s, 0.45, 0.75))
        salvar(n, rgb * (1 - claro[..., None]) + ouro_lum(L, 0.55, 0.9) * claro[..., None], al)


def pano_textura():
    """Pano vermelho novo (pano_cfg): trama do pano liso do Kratos; painel da frente com a grega clara numa faixa
    vertical na borda de fora + filetes em cima/embaixo; pano de trás liso com barra mais escura. Normal plano e
    especular baixo nos blocos."""
    import pano_cfg as PC
    rgb, al = R.carregar(PC.TEX)
    x0, y0, x1, y1 = PC.AMOSTRA_PANO
    amostra = rgb[y0:y1, x0:x1]
    # só o detalhe fino da trama (sem as dobras diagonais da amostra, que viravam listras)
    Ls = R.lum(amostra)
    hp = Ls - ndimage.gaussian_filter(Ls, 6)
    media = np.median(amostra.reshape(-1, 3), 0)
    tile = np.clip(media * (1 + 1.4 * hp)[..., None], 0, 1)
    claro = np.array([0.74, 0.56, 0.32])                       # grega bege-dourada como na arte

    def trama(w, h):
        reps = (int(np.ceil(h / tile.shape[0])) + 1, int(np.ceil(w / tile.shape[1])) + 1)
        t = np.concatenate([np.concatenate([tile if (i + j) % 2 == 0 else tile[::-1, ::-1] for j in range(reps[1])], 1)
                            for i in range(reps[0])], 0)
        return t[:h, :w]

    bx0, by0, bx1, by1 = PC.BLOCO_FRENTE
    w, h = bx1 - bx0, by1 - by0
    f = trama(w, h)
    bw = int(w * 0.30)                                          # faixa da grega (borda de fora, à esquerda)
    g = np.rot90(grega(h - 20, bw - 20))                        # meandro vertical
    m = np.zeros((h, w)); m[10:10 + g.shape[0], 10:10 + g.shape[1]] = g
    m[:, bw - 6:bw - 2] = 1; m[4:10, :] = 1; m[h - 10:h - 4, :] = 1   # filetes
    m = ndimage.gaussian_filter(m, 0.8)[..., None]
    L = R.lum(f)[..., None]
    f = f * (1 - m) + claro * (0.75 + 0.35 * L / max(float(np.median(L)), 1e-3)) * m
    rgb[by0:by1, bx0:bx1] = np.clip(f, 0, 1)

    bx0, by0, bx1, by1 = PC.BLOCO_TRAS
    w, h = bx1 - bx0, by1 - by0
    t = trama(w, h)
    barra = np.clip((np.arange(h) - (h - 40)) / 30, 0, 1)[:, None, None]
    rgb[by0:by1, bx0:bx1] = t * (1 - 0.35 * barra)
    salvar(PC.TEX, rgb, al)
    # normal plano e especular baixo nos blocos (texturas com metade da resolução)
    for nome, valor in (('TX587A1BF5.F8EE906B', None), ('TX0393CBA3.E2D1C1C7', 0.08)):
        a, aa = R.carregar(nome)
        H2, W2 = a.shape[:2]
        sx, sy = W2 / PC.TEX_TAM[0], H2 / PC.TEX_TAM[1]
        for bx0, by0, bx1, by1 in (PC.BLOCO_FRENTE, PC.BLOCO_TRAS):
            sl = (slice(int(by0 * sy), int(by1 * sy)), slice(int(bx0 * sx), int(bx1 * sx)))
            if valor is None:
                a[sl] = (1.0, 0.5, 0.0); aa[sl] = 0.5
            else:
                a[sl] = valor
        salvar(nome, a, aa)


def grevas():
    """Grevas/tornozeleiras (TXE3FF895B, cobre avermelhado no Kratos) -> dourado das ombreiras, como na arte
    do GoW II (pedido do usuário, teste 29); a tira de couro de cima fica a original."""
    rgb, al = R.carregar('TXE3FF895B.EF07B012')
    L = R.lum(rgb)
    tira = R.pecas(rgb, [(0.0, 0.0, 0.65, 0.18)], erosao=10)
    ref = np.median(L[L > 0.05])
    ouro = R.tingir(L, OURO * 1.05, ref, 1.1)
    ouro = 0.75 * ouro + 0.25 * rgb                  # "meio dourado": um pouco do cobre original (envelhecido)
    out = ouro * (1 - tira[..., None]) + rgb * tira[..., None]
    salvar('TXE3FF895B.EF07B012', out, al)


def armadura_dourada():
    """Placas de metal dos antebraços e das canelas + cinto (TX3DEC657A, cobre) -> dourado envelhecido (mesmo
    tom das grevas); os elos das correntes (cinza, pouco saturados) ficam com as cores originais (teste 32)."""
    rgb, al = R.carregar('TX3DEC657A.5633D663')
    h, s, v = R.hsv(rgb)
    L = R.lum(rgb)
    # elos: bege-acinzentado quase uniforme (~148,130,107: r/g ~1,14, g/b ~1,21); cobre: r/g 1,3..1,5.
    # (o critério antigo por saturação pegava só parte de cada elo -> bordas douradas; teste 35)
    r_, g_, b_ = [np.maximum(rgb[..., i], 1e-3) for i in range(3)]
    bege = (np.abs(r_ / g_ - 1.14) < 0.09) & (np.abs(g_ / b_ - 1.21) < 0.14) & (L > 0.2)
    bege = ndimage.binary_opening(bege, iterations=1)
    bege = ndimage.binary_closing(bege, iterations=2)
    elos = ndimage.gaussian_filter(ndimage.binary_dilation(bege, iterations=1).astype(np.float32), 0.7)
    elos = np.clip(elos * 1.5, 0, 1)[..., None]
    ref = np.median(L[(L > 0.08) & (elos[..., 0] < 0.2)])
    ouro = 0.75 * R.tingir(L, OURO * 1.05, ref, 1.1) + 0.25 * rgb
    salvar('TX3DEC657A.5633D663', ouro * (1 - elos) + rgb * elos, al)


if __name__ == '__main__':
    # plano de 2026-11-21: braçadeiras, luvas, botas e saia voltam a ser as do Kratos padrão (sem
    # recolorir); só as texturas do material fleece (ombreiras de carneiro) são geradas aqui.
    if os.path.isdir(SAIDA):
        for f in os.listdir(SAIDA):
            os.remove(os.path.join(SAIDA, f))
    os.makedirs(SAIDA, exist_ok=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    atlas()
    grevas()
    armadura_dourada()
    pano_textura()                         # antes da cota/manoplas (elas repintam a mão em TX5512508B)
    import cota_malha                      # cota de malha de bronze nos braços e pernas (pele)
    cota_malha.gerar()
    print('texturas em', SAIDA)
