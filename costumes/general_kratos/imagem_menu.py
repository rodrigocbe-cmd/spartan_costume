"""Imagem do menu do General Kratos e do General Kratos (armadura): a imagem OFICIAL do traje base
(COSTUMEIMAGES: Kratos padrão / Dominus — mesma pose e posição) com a pele pintada como nas texturas
(recolorir.py): ganho por canal pele do Kratos → pele do Deimos (R_HERO07); tatuagem, roupas e lâminas
ficam iguais. Pele/tatuagem detectadas por `dark_odyssey/imagem_menu.mascaras_kratos` (Kratos) ou só pela
cor (Dominus, cujo traje cobre o tronco).
uso: python -I costumes/general_kratos/imagem_menu.py  -> menu/imagem_menu.png dos dois trajes"""
import os
import sys
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'costumes', 'dark_odyssey'))
import imagem_menu as M          # noqa: E402  (dark_odyssey)

# mesmo ganho das texturas: pele mediana Kratos TX27CF5CC1 (156,142,132) -> Deimos TX856D597B (109,85,71)
GANHO = np.array([109, 85, 71]) / np.array([156, 142, 132])
CLAREAR = 1.15     # a imagem do menu é bem escura; o ganho puro deixa a pele quase preta

IMAGENS = {   # destino -> imagem do traje base
    os.path.join(AQUI, 'menu'): ('TXAEF04C75.F52173F8.png', True),                                     # Kratos
    os.path.join(RAIZ, 'costumes', 'general_kratos_armadura', 'menu'): ('TX55B4239D.7ECA9FFA.png', False),  # Dominus
}


def gerar(orig, destino, kratos):
    rgb, a = M.carregar(orig)
    if kratos:
        m = M.mascaras_kratos(rgb, a)
    else:
        m = dict(zip(('pele', 'tatuagem'), M.pele_e_tatuagem(rgb, a)))
    pele = m['pele'] * (1 - m['tatuagem']) * M.R.suave(a, 0.6, 0.95)
    nova = np.clip(rgb * GANHO * CLAREAR, 0, 1)
    out = M.mistura(rgb, nova, pele)
    M.salvar(out, a, destino, orig)


def main():
    for destino, (nome, kratos) in IMAGENS.items():
        gerar(os.path.join(M.PNG_MENU, nome), destino, kratos)
    print('ok')


if __name__ == '__main__':
    main()
