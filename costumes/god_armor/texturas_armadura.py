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


def ombreira(tam=512):
    ram = Image.open(os.path.join(SC, '09e06a70a8d42785d872cffe.png')).convert('RGB')
    ram = ram.resize((tam, tam), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.3))
    L = np.asarray(ram).astype(np.float32) @ [0.299, 0.587, 0.114] / 255
    L = np.clip((L - np.percentile(L, 2)) / (np.percentile(L, 98) - np.percentile(L, 2)), 0, 1)
    L = np.clip(L + (L - ndimage.gaussian_filter(L, 10)) * 0.8, 0, 1)
    n, ris = metal(tam, tam, 7)
    return colorir(L, n, ris)


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
    base = np.array([0.42, 0.08, 0.07])
    L = 0.75 + 0.12 * n + 0.08 * ndimage.gaussian_filter(rng.standard_normal((t, t)), (6, 1))
    cor = base * L[..., None]
    borda = ((xx < 0.12) | (xx > 0.88)) & (yy > 0.02)
    cor[borda] = (OURO * (0.7 + 0.2 * n[borda, None]))
    r = np.hypot(xx - 0.5, (yy - 0.14) * 1.0)
    rebite = r < 0.11
    cor[rebite] = OURO * (0.9 - 2.5 * r[rebite, None])
    return np.clip(cor, 0, 1)


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
    A[512:1024, 0:512] = colorir(np.full((512, 512), 0.6), *metal(512, 512, 13))
    A[512:768, 256:512] = couro_tira(256)          # célula B: tiras de couro (pteruges)
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


if __name__ == '__main__':
    os.makedirs(SAIDA, exist_ok=True)
    atlas()
    recolorir_pecas()
    print('texturas em', SAIDA)
