"""Odisseia Sombria, ajustes não-textura: curvas de cor das partículas das lâminas (fogo e faíscas) -> dourado.
As texturas das lâminas vêm de recolorir.py (pastas texturas/R_W_EXPLOSIVEk)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ferramentas'))
import particulas  # noqa: E402


def processar(nome_wad, dados):
    if nome_wad.startswith('R_W_EXPLOSIVE'):
        dados, _ = particulas.dourar_wad(dados)
    return dados
