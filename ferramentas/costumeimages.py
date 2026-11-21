"""Imagens do menu de trajes (COSTUMEIMAGES.WAD).

O menu (script SMI_Shell do SHELL.WAD) mostra, para o traje de índice K, o objeto
`gocostumeK` deste WAD (nome de script "costumeK"). Cada imagem é um grupo:
  textura TX…dds (256x512 DXT5, sem mipmaps) → material MAT_ubershaderN (cita a textura
  pelo nome) → malha MG_<hash>_0 / MDL_<hash> (quadro) → objeto gocostumeK
  (+ objeto sem nome com "costumeK", SCP_costumeK) → referência "gocostumeK" na lista de UI.
O jogo original tem gocostume0..7. `adicionar_imagem` clona o grupo do traje 7 para um
índice novo, com uma textura nova.
"""
import io
import struct
import zlib

from PIL import Image

import dds
from wad import parse, align, HDR

MODELO = 7   # grupo usado como molde


def _blocos(d):
    """Lista de (entrada, bytes do bloco completo: cabeçalho + dados + alinhamento)."""
    es = parse(d)
    out = []
    for e in es:
        fim = align(e['data_off'] + e['size'])
        out.append([e, bytearray(d[e['off']:fim])])
    return out


def _renomear(bloco, novo_nome):
    n = novo_nome.encode('latin1')
    assert len(n) < HDR - 8
    bloco[8:HDR] = n + b'\x00' * (HDR - 8 - len(n))


def _troca(bloco, velho, novo, inicio=HDR):
    assert len(velho) == len(novo)
    i = bloco.find(velho, inicio)
    assert i >= 0, velho
    bloco[i:i + len(velho)] = novo


def nome_textura(indice):
    h1 = zlib.crc32(b'gow3costumes:costume%d' % indice) & 0xffffffff
    h2 = zlib.crc32(b'gow3costumes:imagem%d' % indice) & 0xffffffff
    return 'TX%08X.%08X.dds' % (h1, h2)


def hash_modelo(indice):
    # mesmo padrão dos originais (e075da3c..3b = costume0..7: último byte = 0x0c ^ dígito)
    if indice <= 9:
        return 0xe075da00 | (0x0c ^ (0x30 + indice))
    return 0xe075d000 | (indice & 0xff)          # índices >= 10: nomes próprios (sem colisão)


def adicionar_imagem(d, indice, imagem_rgba):
    """Devolve um COSTUMEIMAGES.WAD novo com gocostume<indice> usando a imagem dada (PIL RGBA 256x512)."""
    bl = _blocos(d)
    nomes = [b[0]['name'] for b in bl]
    assert 'gocostume%d' % indice not in nomes, 'já existe'
    pos = {(b[0]['name'], b[0]['tag']): i for i, b in enumerate(bl)}

    # --- textura (clona a do traje 7, pelo material dele)
    mat_m = bl[pos[('MAT_ubershader%d' % (MODELO + 1), 0x560001)]][1]
    i_tex = mat_m.find(b'TX', HDR)
    tex_velho = bytes(mat_m[i_tex:i_tex + 23]).decode()
    tex_novo = nome_textura(indice)
    i_bt = next(i for i, b in enumerate(bl) if b[0]['name'] == tex_velho)
    bt = bytearray(bl[i_bt][1])
    _renomear(bt, tex_novo)
    _troca(bt, tex_velho.encode(), tex_novo.encode())
    k = bt.find(b'DDS ', HDR)
    h, w = struct.unpack_from('<II', bt, k + 12)
    assert (w, h) == imagem_rgba.size, (w, h)
    pix = dds.encode_level(imagem_rgba.convert('RGBA'), 'DXT5')
    assert len(pix) == w * h, len(pix)
    bt[k + 128:k + 128 + len(pix)] = pix
    ultimo_tx = max(i for i, b in enumerate(bl) if b[0]['tag'] == 0xd0001 and b[0]['name'].startswith('TX'))

    # --- material
    mat_nome_m = 'MAT_ubershader%d' % (MODELO + 1)
    mat_nome = 'MAT_ubershader%d' % (indice + 1)
    i_mat = pos[(mat_nome_m, 0x560001)]
    grupo_mat = [bytearray(bl[i_mat - 1][1]), bytearray(bl[i_mat][1]), bytearray(bl[i_mat + 1][1])]
    _renomear(grupo_mat[1], mat_nome); _renomear(grupo_mat[2], mat_nome)
    _troca(grupo_mat[1], tex_velho.encode(), tex_novo.encode())
    ultimo_mat = max(i for i, b in enumerate(bl) if b[0]['name'].startswith('MAT_ubershader') and b[0]['tag'] == 0x3)

    # --- malha + objeto (MG_… até o GroupEnd do gocostume)
    hm = '%08x' % hash_modelo(MODELO)
    hn = '%08x' % hash_modelo(indice)
    i_mg = pos[('MG_%s_0' % hm, 0x520001)]
    i_fim = pos[('SCP_costume%d' % MODELO, 0xd0001)] + 2
    grupo_obj = []
    for e, b in bl[i_mg:i_fim + 1]:
        b = bytearray(b)
        n = e['name']
        n = n.replace(hm, hn).replace(mat_nome_m, mat_nome)
        n = n.replace('gocostume%d' % MODELO, 'gocostume%d' % indice).replace('SCP_costume%d' % MODELO, 'SCP_costume%d' % indice)
        _renomear(b, n)
        if e['tag'] == 0x1f0001 and e['name'] == '':
            velho = b'costume%d' % MODELO
            novo = b'costume%d' % indice
            # o campo de nome é fixo (preenchido com zeros): grava o nome novo ocupando os zeros
            _troca(b, velho + b'\x00' * (len(novo) - len(velho) + 1), novo + b'\x00')
        if e['name'] == 'gocostume%d' % MODELO and e['tag'] == 0x1f0001:
            num = struct.unpack_from('<H', b, HDR + 0x3c)[0]
            maior = max(struct.unpack_from('<H', bb, HDR + 0x3c)[0] for ee, bb in bl
                        if ee['name'].startswith('gocostume') and ee['tag'] == 0x1f0001)
            struct.pack_into('<H', b, HDR + 0x3c, maior + 1)
        grupo_obj.append(b)
    i_ultimo_obj = max(i for i, b in enumerate(bl) if b[0]['name'].startswith('SCP_costume')) + 2

    # --- referência na lista de UI
    i_ref = max(i for i, b in enumerate(bl) if b[0]['name'].startswith('gocostume') and b[0]['tag'] == 0x1)
    ref = bytearray(bl[i_ref][1]); _renomear(ref, 'gocostume%d' % indice)

    # --- DC_WAD 0x9000c: número de objetos de jogo
    i_dc = pos[(nomes[[b[0]['tag'] for b in bl].index(0x9000c)], 0x9000c)]
    dc = bl[i_dc][1]
    n_obj = struct.unpack_from('<I', dc, HDR + 8)[0]
    struct.pack_into('<I', dc, HDR + 8, n_obj + 1)

    # monta (inserções de trás para a frente para não deslocar índices)
    novos = [b for _, b in bl]
    for i_depois, itens in sorted([(i_ref, [ref]), (i_ultimo_obj, grupo_obj), (ultimo_mat, grupo_mat),
                                   (ultimo_tx, [bt])], key=lambda x: -x[0]):
        novos[i_depois + 1:i_depois + 1] = itens
    out = b''.join(bytes(b) for b in novos)
    out += b'\x00' * (align(len(out)) - len(out))
    return out
