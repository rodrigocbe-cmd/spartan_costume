"""Ajustes do traje que não são texturas, aplicados pelo build depois das texturas.

processar(nome_wad, dados) -> dados   (mesmo tamanho; o build empacota só os trechos alterados)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ferramentas'))
import particulas


def processar(nome_wad, dados):
    if nome_wad.startswith('R_W_EXPLOSIVE'):
        # fogo e faíscas das lâminas: curvas de cor das partículas -> dourado
        dados, _ = particulas.dourar_wad(dados)
    return dados
