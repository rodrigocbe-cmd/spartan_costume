"""Imagem do menu de trajes (256x512, DXT5 com alfa) da Odisseia Sombria.

Parte da imagem OFICIAL do Kratos padrão (COSTUMEIMAGES.WAD → TXAEF04C75, gocostume0) — mesma pose,
posição e iluminação das outras imagens do menu — e repinta cada parte com as cores das texturas do traje
(paleta de recolorir.py): pele cinza-carvão, tatuagem dourada, saia preta com grega dourada, ombreira,
cinto, braçadeiras, grevas e lâminas douradas.

As partes vêm de `mascaras_kratos` (polígonos na imagem + cor), também usadas pelo General Kratos.

uso: python -I costumes/dark_odyssey/imagem_menu.py
Gera: costumes/dark_odyssey/menu/imagem_menu.png (+ preview_menu.png)
"""
import os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recolorir as R

AQUI = os.path.dirname(os.path.abspath(__file__))
PNG_MENU = os.path.join(R.RAIZ, 'original', 'COSTUMEIMAGES', 'png')
ORIG = os.path.join(PNG_MENU, 'TXAEF04C75.F52173F8.png')        # gocostume0 (Kratos padrão)
SAIDA = os.path.join(AQUI, 'menu')

# partes da imagem do Kratos padrão (pixels da imagem 256x512)
POLIGONOS_KRATOS = {
    'ombreira': [(84, 127), (98, 123), (115, 127), (108, 140), (101, 156), (98, 182), (97, 212), (64, 214),
                 (69, 198), (77, 180), (80, 160), (83, 145)],
    'cinto': [(98, 206), (166, 203), (168, 229), (99, 231)],
    'saia': [(98, 229), (134, 229), (136, 250), (130, 262), (128, 300), (102, 304), (94, 272)],
    'saia_tras': [(134, 229), (170, 228), (176, 250), (168, 262), (150, 254), (136, 252)],
    'bracadeira_dir': [(168, 208), (201, 210), (203, 250), (196, 292), (176, 292), (170, 250)],
    'bracadeira_esq': [(66, 212), (97, 212), (95, 236), (86, 254), (70, 254), (64, 236)],
    'lamina_esq': [(50, 222), (64, 216), (82, 248), (80, 292), (58, 294), (48, 262)],
    'lamina_dir': [(128, 262), (137, 262), (140, 280), (168, 279), (171, 300), (162, 322), (142, 320), (131, 300)],
    'bota_esq': [(74, 318), (112, 318), (110, 392), (52, 394), (52, 374), (76, 360)],
    'bota_dir': [(146, 332), (182, 330), (192, 402), (190, 442), (156, 442), (158, 400), (150, 350)],
}


def poligono(shape, pts, sigma=0.7):
    m = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return ndimage.gaussian_filter(np.asarray(m).astype(np.float32) / 255, sigma)


def carregar(caminho):
    im = np.asarray(Image.open(caminho).convert('RGBA')).astype(np.float32) / 255
    return im[..., :3], im[..., 3]


def pele_e_tatuagem(rgb, a, fora=None):
    """Pele = tons pouco saturados e quentes (a imagem é escura e avermelhada); tatuagem = pele com r/g bem
    acima da pele em volta. `fora` = máscara do que não pode ser pele (peças)."""
    h, s, v = R.hsv(rgb)
    L = R.lum(rgb)
    quente = ((h < 0.11) | (h > 0.90)).astype(np.float32)
    corpo = R.suave(a, 0.75, 0.95)
    fora = np.zeros_like(a) if fora is None else fora
    pele = (1 - R.suave(s, 0.40, 0.50)) * R.suave(L, 0.015, 0.04) * quente * corpo * (1 - fora)
    # zona da pele = pele com os buracos fechados (a tatuagem é um "buraco" saturado dentro dela)
    zona = ndimage.binary_closing(pele > 0.5, iterations=7)
    zona = ndimage.binary_fill_holes(zona) & (fora < 0.5) & (corpo > 0.5)
    vermelho = ((h < 0.06) | (h > 0.92)).astype(np.float32)
    tat = zona * vermelho * R.suave(s, 0.40, 0.50) * R.suave(L, 0.008, 0.03)
    tat = ndimage.gaussian_filter(ndimage.median_filter(tat, 3), 0.6)
    pele = np.maximum(pele, zona * (1 - tat))
    return np.clip(pele, 0, 1), np.clip(tat, 0, 1)


def mascaras_kratos(rgb, a):
    m = {k: poligono(rgb.shape, p) for k, p in POLIGONOS_KRATOS.items()}
    pecas = np.clip(sum(m.values()), 0, 1)
    h, s, v = R.hsv(rgb)
    # na ombreira só o metal (saturado) é peça; a pele do braço atrás dela fica pele
    metal_ombro = m['ombreira'] * R.suave(s, 0.42, 0.55)
    fora = np.clip(pecas - m['ombreira'] + metal_ombro, 0, 1)
    # nas botas/lâmina da coxa, joelhos e dedos claros e pouco saturados são pele
    L = R.lum(rgb)
    claro = R.suave(L, 0.05, 0.10) * (1 - R.suave(s, 0.40, 0.55))
    for k in ('bota_esq', 'bota_dir', 'lamina_dir'):
        fora = fora - m[k] * claro
    fora = np.clip(fora, 0, 1)
    pele, tat = pele_e_tatuagem(rgb, a, fora)
    m['metal_ombro'] = metal_ombro
    m['pele'], m['tatuagem'] = pele, tat
    return m


def mistura(base, nova, m):
    m = np.clip(m, 0, 1)[..., None]
    return base * (1 - m) + nova * m


def salvar(rgb, a, destino, orig=ORIG):
    os.makedirs(destino, exist_ok=True)
    res = np.concatenate([np.clip(rgb, 0, 1), a[..., None]], -1)
    Image.fromarray((res * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(destino, 'imagem_menu.png'))
    o = Image.open(orig).convert('RGBA')
    n = Image.open(os.path.join(destino, 'imagem_menu.png'))
    W, H = o.size
    prev = Image.new('RGBA', (W * 2 + 8, H), (120, 10, 10, 255))
    prev.alpha_composite(o, (0, 0)); prev.alpha_composite(n, (W + 8, 0))
    prev.resize((prev.width * 2, H * 2)).save(os.path.join(destino, 'preview_menu.png'))


def main():
    rgb, a = carregar(ORIG)
    m = mascaras_kratos(rgb, a)
    L = R.lum(rgb)
    opaco = R.suave(a, 0.6, 0.95)          # o halo (sombra) em volta do corpo fica como está
    ref = float(np.median(L[m['pele'] > 0.8]))
    out = rgb.copy()

    def peca(mask, cor, brilho, contraste=1.0, base=None):
        """Tinge mantendo a luz/sombra da imagem (luminância relativa à pele)."""
        mask = mask * opaco
        Lb = L if base is None else base
        r = ref          # mesma escala para todas as peças: escuro continua escuro
        nova = R.tingir(Lb, cor * brilho, r, contraste)
        nova = nova / (1 + 0.6 * np.maximum(nova.max(-1, keepdims=True) - 0.6, 0))   # brilhos sem estourar
        return mistura(out, nova, mask)

    sem_pele = 1 - m['pele']
    out = peca(m['pele'] * (1 - m['tatuagem']), R.PELE * np.array([1.0, 1.0, 1.04]), 0.9)
    out = peca(m['tatuagem'], R.TATUAGEM, 1.2, 0.8)
    out = peca(m['metal_ombro'], R.OURO, 1.0)
    out = peca(m['cinto'] * sem_pele, R.OURO, 1.6, 0.85)
    # saia: tecido vermelho -> preto; grega (clara) -> dourada
    grega = R.suave(L, 0.10, 0.16)
    for k in ('saia', 'saia_tras'):
        out = peca(m[k] * (1 - grega), R.PRETO, 4.0, 0.8)
        out = peca(m[k] * grega, R.OURO, 1.8, 0.8)
    for k in ('bracadeira_dir', 'bracadeira_esq'):
        out = peca(m[k] * sem_pele, np.array([0.30, 0.28, 0.25]), 2.4, 0.9)
    for k in ('lamina_esq', 'lamina_dir'):
        out = peca(m[k] * sem_pele, R.OURO, 1.6, 0.9)
    for k in ('bota_esq', 'bota_dir'):
        out = peca(m[k] * sem_pele, R.OURO, 1.1, 0.9)
    salvar(out, a, SAIDA)
    print('ok (pele ref %.3f)' % ref)


if __name__ == '__main__':
    main()
