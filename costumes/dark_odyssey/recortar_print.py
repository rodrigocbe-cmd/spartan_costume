"""Recorta o Kratos (Odisseia Sombria) de um print do menu de trajes com GrabCut (OpenCV)
e gera a imagem do menu (256x512 RGBA, mesmo enquadramento das imagens oficiais).

uso: python costumes/dark_odyssey/recortar_print.py <print.png>
(precisa de opencv-python-headless; rodar sem -I por causa do site do usuário)
Gera: costumes/dark_odyssey/menu/imagem_menu.png e preview_menu.png
"""
import os, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, 'menu')

# Dicas para o print de referência (645x1040). Coordenadas em pixels (x0, y0, x1, y1).
RET = (115, 45, 565, 1020)
CERTO_KRATOS = [(325, 70, 370, 150), (300, 160, 420, 330), (260, 340, 400, 480), (455, 380, 490, 520),
                (160, 480, 180, 550), (230, 330, 280, 420),
                (215, 590, 275, 690), (215, 700, 280, 860), (150, 862, 250, 888),   # perna/pé esquerdos
                (400, 650, 440, 715), (400, 730, 470, 930), (445, 950, 495, 1010),  # perna/pé direitos
                (345, 560, 430, 640)]                                               # lâmina na cintura
CERTO_FUNDO = [(115, 45, 190, 170), (115, 175, 175, 420), (520, 45, 565, 330), (510, 560, 565, 1020),
               (292, 700, 380, 1040), (100, 600, 190, 840), (500, 660, 565, 900),
               (100, 905, 420, 1040), (510, 900, 565, 1040), (288, 615, 330, 690)]


def recortar(caminho):
    im = cv2.imread(caminho)
    H, W = im.shape[:2]
    mask = np.full((H, W), cv2.GC_BGD, np.uint8)
    x0, y0, x1, y1 = RET
    mask[y0:y1, x0:x1] = cv2.GC_PR_FGD
    for x0, y0, x1, y1 in CERTO_KRATOS:
        mask[y0:y1, x0:x1] = cv2.GC_FGD
    for x0, y0, x1, y1 in CERTO_FUNDO:
        mask[y0:y1, x0:x1] = cv2.GC_BGD
    bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(im, mask, None, bgd, fgd, 10, cv2.GC_INIT_WITH_MASK)
    m = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    # mantém só regiões que tocam as marcações de "certo Kratos"
    n, lab, _, _ = cv2.connectedComponentsWithStats(m)
    manter = set()
    for x0, y0, x1, y1 in CERTO_KRATOS:
        manter |= set(np.unique(lab[y0:y1, x0:x1])) - {0}
    m = np.where(np.isin(lab, list(manter)), 255, 0).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    return im, m


def main(caminho):
    im, m = recortar(caminho)
    os.makedirs(SAIDA, exist_ok=True)
    cv2.imwrite(os.path.join(SAIDA, 'mascara_grabcut.png'), m)
    # borda suave + leve halo escuro (como as imagens oficiais)
    alfa = cv2.GaussianBlur(m, (0, 0), 1.2).astype(np.float32) / 255
    sombra = cv2.GaussianBlur(cv2.dilate(m, np.ones((9, 9), np.uint8)), (0, 0), 6).astype(np.float32) / 255
    rgb = im[..., ::-1].astype(np.float32) / 255
    # runas vermelhas das lâminas (print da v0.2) -> laranja-dourado, como na v0.3
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32)
    verm = (((hsv[..., 0] < 8) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 120) & (hsv[..., 2] > 60)).astype(np.float32)
    verm = cv2.GaussianBlur(verm, (0, 0), 0.8)[..., None]
    fogo = np.array([1.0, 0.62, 0.15]) * rgb.max(-1, keepdims=True)
    rgb = rgb * (1 - verm) + fogo * verm
    A = np.maximum(alfa, sombra * 0.55)
    cor = rgb * (alfa / np.maximum(A, 1e-4))[..., None]          # halo = preto
    rgba = np.concatenate([cor, A[..., None]], -1)
    # enquadramento: mesmo tamanho relativo das imagens oficiais (Kratos ~ 68% da altura, centrado)
    ys, xs = np.where(m > 0)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    alt = y1 - y0
    esc = (512 * 0.66) / alt
    from PIL import Image
    img = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA')
    img = img.resize((int(img.width * esc), int(img.height * esc)), Image.LANCZOS)
    cx, cy = (x0 + x1) / 2 * esc, (y0 + y1) / 2 * esc
    tela = Image.new('RGBA', (256, 512), (0, 0, 0, 0))
    tela.paste(img, (int(round(128 - cx)), int(round(512 * 0.535 - cy))), img)
    tela.save(os.path.join(SAIDA, 'imagem_menu.png'))
    prev = Image.new('RGBA', (256, 512), (120, 10, 10, 255))
    prev.alpha_composite(tela)
    prev.resize((512, 1024)).save(os.path.join(SAIDA, 'preview_menu.png'))
    print('ok')


if __name__ == '__main__':
    main(sys.argv[1])
