"""Geração dos arquivos dos trajes em SLOTS NOVOS (sem substituir trajes do jogo).

Cada traje (costumes/<id>/costume.json) gera seus WADs (texturas + pos_wad.py) — o WAD do Kratos
vai para R_HERO<índice>.WAD. Os arquivos COMPARTILHADOS dependem do conjunto instalado:
  R_PERM.WAD (bônus), R_LANG_*.WAD (+ DLC6/R_LANG_EN) com as mensagens 2000N, COSTUMEIMAGES.WAD
  (+ DLC6) com gocostumeK.
Os índices são atribuídos em sequência a partir de PRIMEIRO_INDICE, na ordem do pacote, para a
lista do menu nunca ter buracos.
Caminhos são relativos à pasta EXEC do jogo.
"""
import glob
import importlib.util
import json
import os
import struct

from PIL import Image

import costumeimages
import lang
from reempacotar import rebuild

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
JOGO = os.environ.get('GOW3_JOGO', r'C:\Users\rodri\Downloads\ShadPS4 Output\CUSA01623\EXEC')
PRIMEIRO_INDICE = 9                 # trajes oficiais: 0..8
PRIMEIRA_MSG = 20000 - 1            # mensagem = 19999 + índice (índice 9 -> 20008)
TABELA_BONUS = 0x26813f8            # R_PERM.WAD: 16 registros de 7 floats
MAX_INDICE = 15
W = 'WAD/PS4_LE/'
D6 = 'DLC/DLC6/WAD/PS4_LE/'
IMAGEM_PADRAO = os.path.join(RAIZ, 'original', 'COSTUMEIMAGES', 'png', 'TXAEF04C75.F52173F8.png')


def meta(cid):
    cdir = os.path.join(RAIZ, 'costumes', cid)
    m = json.load(open(os.path.join(cdir, 'costume.json'), encoding='utf-8'))
    m['_dir'] = cdir
    m.setdefault('slot', True)          # False = item sem traje (ex.: lâminas, valem para todos)
    return m


def com_slot(ids):
    return [c for c in ids if meta(c)['slot']]


def ler_jogo(rel):
    return open(os.path.join(JOGO, rel), 'rb').read()


def _hook(cdir):
    f = os.path.join(cdir, 'pos_wad.py')
    if not os.path.exists(f):
        return None
    spec = importlib.util.spec_from_file_location('pos_wad_' + os.path.basename(cdir), f)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def arquivos_traje(cid):
    """[(fonte, destino, bytes)]; destino 'slot' = R_HERO<índice>.WAD."""
    m = meta(cid)
    pos = _hook(m['_dir'])
    out = []
    for w in m['wads']:
        dst = os.path.join(RAIZ, 'build', cid, w['base'])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        rebuild(os.path.join(JOGO, W + w['base']), os.path.normpath(os.path.join(m['_dir'], 'texturas', w['texturas'])), dst, verbose=False)
        dados = open(dst, 'rb').read()
        if pos is not None:
            dados = pos.processar(w['base'][:-4], dados)
            open(dst, 'wb').write(dados)
        out.append((W + w['base'], w['destino'], dados))
    return out


def destino(d, indice):
    return W + ('R_HERO%02d.WAD' % indice if d == 'slot' else d)


# idioma do arquivo R_LANG_<código> -> textos_jogo; na falta, o "vizinho" e depois inglês
VIZINHO = {'PT': 'BR', 'BR': 'PT', 'UK': 'EN', 'LA': 'ES', 'ES': 'LA'}


def _linhas(m, indice, codigo, texto_original):
    t = m['textos_jogo']
    for c in (codigo, VIZINHO.get(codigo), 'EN'):
        if c in t:
            nome, *desc = t[c]
            linhas = [str(indice), 'TRUE', nome, 'heroImage%02d' % indice] + desc
            # a fonte do jogo pode não ter todos os caracteres (idiomas asiáticos): só usa o texto
            # se todos os caracteres já aparecem no arquivo original daquele idioma
            faltam = set(''.join(linhas)) - set(texto_original)
            if not faltam:
                return linhas[:4] + _quebrar(desc, _largura_max(texto_original))
            print(ascii('  aviso: %s/%s sem os caracteres %s -> proximo idioma' % (m['id'], c, ''.join(sorted(faltam)))))
    raise ValueError('sem texto para ' + m['id'])


def _largura_max(texto_original):
    """Maior linha de descrição dos trajes oficiais (mensagens 20000..20007) desse idioma."""
    import re
    maior = 0
    for mid in range(20000, 20008):
        r = re.search(r'\*%d\*[^\r\n]*\r\n(.*?)(?=\r\n\*\d+\*)' % mid, texto_original, re.S)
        if r:
            maior = max([maior] + [len(x) for x in r.group(1).split('\r\n')[4:]])
    return maior


def _quebrar(desc, largura):
    """Quebra (em espaços) as linhas maiores que as oficiais — como o jogo faz no traje Deimos."""
    import textwrap
    out = []
    for linha in desc:
        if len(linha) <= largura or ' ' not in linha:
            out.append(linha)
        else:
            n = -(-len(linha) // largura)                       # nº de linhas; divide equilibrado
            out += textwrap.wrap(linha, width=min(largura, -(-len(linha) // n) + 8))
    return out


def _imagem(m):
    p = os.path.join(m['_dir'], m.get('imagem_menu', 'menu/imagem_menu.png'))
    return Image.open(p if os.path.exists(p) else IMAGEM_PADRAO).convert('RGBA')


def compartilhados(ids):
    """[(fonte, destino, bytes, opcional)] para os trajes COM SLOT `ids` (na ordem do pacote)."""
    ms = [(PRIMEIRO_INDICE + i, meta(c)) for i, c in enumerate(ids)]
    assert ms[-1][0] <= MAX_INDICE
    out = []
    perm = bytearray(ler_jogo(W + 'R_PERM.WAD'))
    for i, m in ms:
        assert struct.unpack_from('<7f', perm, TABELA_BONUS + i * 0x1c)[6] == 0
        struct.pack_into('<7f', perm, TABELA_BONUS + i * 0x1c, *m['bonus'])
    out.append((W + 'R_PERM.WAD', W + 'R_PERM.WAD', bytes(perm), False))
    langs = [W + os.path.basename(f) for f in sorted(glob.glob(os.path.join(JOGO, W, 'R_LANG_*.WAD')))]
    for rel in langs + [D6 + 'R_LANG_EN.WAD']:
        codigo = os.path.basename(rel)[7:9]                  # BR, PT, EN, ES, ... (idioma do jogo)
        d = ler_jogo(rel)
        original = lang.ler_msgs(d)[1].decode('utf-8')
        for i, m in ms:
            d = lang.inserir_mensagem(d, PRIMEIRA_MSG + i, _linhas(m, i, codigo, original))
        out.append((rel, rel, d, rel.startswith('DLC')))
    for rel in (W + 'COSTUMEIMAGES.WAD', D6 + 'COSTUMEIMAGES.WAD'):
        d = ler_jogo(rel)
        for i, m in ms:
            d = costumeimages.adicionar_imagem(d, i, _imagem(m))
        out.append((rel, rel, d, rel.startswith('DLC')))
    return out
