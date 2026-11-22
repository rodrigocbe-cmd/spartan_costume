"""Ajustes não-textura do Deus da Guerra (rodado pelo build depois das texturas): monta o Kratos com peças
de outros trajes do jogo (montagem.py). O WAD muda de tamanho."""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import montagem  # noqa: E402


def processar(nome_wad, dados):
    if not nome_wad.startswith('R_HERO'):
        return dados
    return montagem.montar(dados, log=lambda *a: print(*a))
