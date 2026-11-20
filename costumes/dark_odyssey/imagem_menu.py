"""Imagem do menu de trajes (256x512, DXT5 com alfa) da Odisseia Sombria.

Parte da imagem oficial do Kratos padrão (COSTUMEIMAGES.WAD → TXAEF04C75, gocostume0),
que já tem a pose/iluminação das outras imagens, e recolore por cor + região.

uso: python -I costumes/dark_odyssey/imagem_menu.py
Gera: costumes/dark_odyssey/menu/imagem_menu.png (+ preview_menu.png)
"""
import os
import numpy as np
from PIL import Image
import recolorir as R

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(R.RAIZ, 'original', 'COSTUMEIMAGES', 'png', 'TXAEF04C75.F52173F8.png')
SAIDA = os.path.join(AQUI, 'menu')


def main():
    im = np.asarray(Image.open(ORIG).convert('RGBA')).astype(np.float32) / 255
    rgb, a = im[..., :3], im[..., 3:]
    H, W = rgb.shape[:2]
    h, s, v = R.hsv(rgb)
    L = R.lum(rgb)
    yy, xx = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]

    from scipy import ndimage
    corpo = R.suave(a[..., 0], 0.45, 0.85)                                 # ignora sombra/halo
    def regiao(boxes, sigma=2.0):
        return ndimage.gaussian_filter(R.caixa(rgb.shape, boxes), sigma) * corpo

    vermelho = ((h < 0.05) | (h > 0.93)).astype(np.float32)
    amarelo = ((h >= 0.06) & (h < 0.17)).astype(np.float32)
    pele = (1 - R.suave(s, 0.30, 0.42)) * R.suave(v, 0.28, 0.45) * corpo   # cinza/rosado claro
    tat = vermelho * R.suave(s, 0.42, 0.55) * (1 - R.suave(L, 0.40, 0.55)) * regiao([(0.0, 0.0, 1.0, 0.415)], 1.0)
    ombro = regiao([(0.15, 0.22, 0.42, 0.42)]) * amarelo * R.suave(s, 0.3, 0.5)
    braceletes = regiao([(0.26, 0.38, 0.42, 0.47), (0.64, 0.40, 0.82, 0.56)])
    lamina_esq = regiao([(0.18, 0.43, 0.33, 0.58)])
    lamina_dir = regiao([(0.50, 0.48, 0.68, 0.65)]) * np.maximum(vermelho * R.suave(s, 0.3, 0.5), 1 - R.suave(L, 0.15, 0.3))
    lamina = np.maximum(lamina_esq, lamina_dir)
    saia = regiao([(0.36, 0.44, 0.58, 0.64)]) * (1 - lamina)
    cinto = regiao([(0.38, 0.40, 0.66, 0.445)], 1.0)
    grevas = regiao([(0.0, 0.62, 1.0, 1.0)]) * R.suave(s, 0.2, 0.4)

    out = rgb.copy()
    ref_pele = np.median(L[(pele > 0.8)])
    out = mistura(out, R.tingir(L, R.PELE * 1.25, ref_pele, 1.2), pele * (1 - tat))
    out = mistura(out, R.tingir(0.5 * L + 0.5 * 0.4, R.TATUAGEM, 0.4, 1.0), tat)
    out = mistura(out, R.tingir(L, R.OURO * 1.1, 0.55, 1.0), ombro)
    out = mistura(out, R.tingir(L, R.PRETO * 1.4, 0.25, 1.0), braceletes * (1 - pele) * (1 - lamina))
    claro = R.suave(L, 0.20, 0.34)
    out = mistura(out, R.tingir(L, R.PRETO * 1.3, 0.15, 1.0), saia * (1 - claro) * (1 - pele))
    out = mistura(out, R.tingir(L, R.OURO, 0.40, 1.0), saia * claro * (1 - pele))
    out = mistura(out, R.tingir(0.6 * L + 0.4 * 0.3, R.OURO, 0.3, 1.0), np.maximum(cinto, grevas * (1 - pele)))
    out = mistura(out, R.tingir(0.5 * L + 0.5 * 0.35, R.OURO, 0.35, 1.1), lamina * (1 - pele))

    os.makedirs(SAIDA, exist_ok=True)
    res = np.concatenate([np.clip(out, 0, 1), a], -1)
    Image.fromarray((res * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(SAIDA, 'imagem_menu.png'))
    # preview sobre o quadro vermelho do menu
    prev = Image.new('RGBA', (W * 2 + 8, H), (120, 10, 10, 255))
    o = Image.open(ORIG).convert('RGBA')
    n = Image.open(os.path.join(SAIDA, 'imagem_menu.png'))
    prev.alpha_composite(o, (0, 0)); prev.alpha_composite(n, (W + 8, 0))
    prev.resize((prev.width * 2, H * 2)).save(os.path.join(SAIDA, 'preview_menu.png'))
    print('ok')


def mistura(base, nova, m):
    m = np.clip(m, 0, 1)[..., None]
    return base * (1 - m) + nova * m


if __name__ == '__main__':
    main()
