"""Gera um WAD novo substituindo texturas por PNGs editados (mesmo tamanho/formato).

uso: python -I ferramentas/reempacotar.py <WAD original> <pasta com PNGs> <WAD saída>
Os PNGs devem ter o nome da textura (ex.: TX4A104642.F3349159.png). As que não existirem
na pasta ficam como no original. O tamanho do WAD não muda (substituição no lugar).
"""
import os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import dds
from extrair_texturas import textures, nome_base

def rebuild(src_wad, png_dir, out_wad, verbose=True):
    data = bytearray(open(src_wad, 'rb').read())
    n = 0
    for e, off, w, h, mips, fmt, body in textures(bytes(data)):
        p = os.path.join(png_dir, nome_base(e['name']) + '.png')
        if not os.path.exists(p):
            continue
        img = Image.open(p)
        assert img.size == (w, h), f'{p}: tamanho {img.size} != {(w, h)}'
        pix = dds.encode(img, fmt, mips)
        start = e['data_off'] + off + 128
        assert start + len(pix) <= e['data_off'] + e['size'], 'dados maiores que a entrada'
        data[start:start + len(pix)] = pix
        n += 1
        if verbose:
            print('  substituída', e['name'], fmt, f'{w}x{h}')
    os.makedirs(os.path.dirname(os.path.abspath(out_wad)), exist_ok=True)
    open(out_wad, 'wb').write(data)
    return n

if __name__ == '__main__':
    print(rebuild(*sys.argv[1:4]), 'texturas substituídas')
