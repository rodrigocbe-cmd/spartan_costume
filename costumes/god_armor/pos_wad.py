"""Ajustes não-textura da Armadura do Deus da Guerra (rodado pelo build depois das texturas):
troca a malha MG do Kratos pela malha com as peças novas (o WAD muda de tamanho)."""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
sys.path.insert(0, AQUI)
import wad, lang, esqueleto, construir  # noqa: E402


def processar(nome_wad, dados):
    if not nome_wad.startswith('R_HERO'):
        return dados
    sk = esqueleto.ler(open(os.path.join(RAIZ, 'original', 'gohero_dados.bin'), 'rb').read())
    e = [e for e in wad.parse(dados) if e['name'] == 'MG_b826bd6e_0' and e['tag'] == 0x520001][0]
    nb = construir.construir(dados[e['data_off']:e['data_off'] + e['size']], sk)
    return lang.substituir_dados(dados, e, nb)
