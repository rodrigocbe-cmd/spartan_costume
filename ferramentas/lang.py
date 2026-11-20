"""Textos do jogo (R_LANG_*.WAD → entrada MSGS_TXT).

Formato do MSGS_TXT (UTF-8, CRLF, terminado em \\0):
    "<cap_ids> <cap_linhas>"          capacidades usadas pelo carregador do eboot
    "*<id>*[TAG]"                     início de mensagem (TAG opcional, ex.: DLC3)
    linhas de texto...
O carregador aloca (cap_ids+1) entradas de ID e cap_linhas ponteiros de linha
(sem checar limite), por isso as capacidades são aumentadas junto com o texto.

Trajes: mensagens 20000+N →  índice do traje (R_Hero%02d e tabela de bônus no R_PERM),
TRUE/FALSE (desbloqueado), nome, imagem (heroImageNN do COSTUMEIMAGES.WAD), descrição.
"""
import re
import struct

from wad import parse, align, HDR


def ler_msgs(wad_bytes):
    for e in parse(wad_bytes):
        if e['name'] == 'MSGS_TXT':
            return e, wad_bytes[e['data_off']:e['data_off'] + e['size']]
    raise ValueError('MSGS_TXT não encontrado')


def inserir_mensagem(wad_bytes, msg_id, linhas, tag=''):
    """Devolve um novo WAD com a mensagem inserida em ordem de ID (substitui se já existir)."""
    e, txt = ler_msgs(wad_bytes)
    corpo = txt.rstrip(b'\x00')
    bom = b''
    if corpo.startswith(b'\xef\xbb\xbf'):
        bom, corpo = corpo[:3], corpo[3:]
    cab, resto = corpo.split(b'\r\n', 1)
    cap_ids, cap_lin = map(int, cab.split())
    blocos = re.split(rb'\r\n(?=\*\d+\*)', resto.rstrip(b'\r\n'))
    novo = ('*%d*%s\r\n' % (msg_id, tag)).encode() + '\r\n'.join(linhas).encode('utf-8')
    ids = [int(re.match(rb'\*(\d+)\*', b).group(1)) for b in blocos]
    if msg_id in ids:
        blocos[ids.index(msg_id)] = novo
    else:
        pos = next((i for i, x in enumerate(ids) if x > msg_id), len(blocos))
        blocos.insert(pos, novo)
        cap_ids += 1
    cap_lin += len(linhas)
    corpo = bom + ('%d %d' % (cap_ids, cap_lin)).encode() + b'\r\n' + b'\r\n'.join(blocos) + b'\r\n\x00'
    return substituir_dados(wad_bytes, e, corpo)


def substituir_dados(wad_bytes, e, dados):
    """Troca os dados de uma entrada (tamanho pode mudar); entradas seguintes são deslocadas."""
    ini = e['off']
    fim_antigo = align(e['data_off'] + e['size'])
    cab = bytearray(wad_bytes[ini:ini + HDR])
    struct.pack_into('<I', cab, 4, len(dados))
    bloco = bytes(cab) + dados
    bloco += b'\x00' * (align(len(bloco)) - len(bloco))
    return wad_bytes[:ini] + bloco + wad_bytes[fim_antigo:]
