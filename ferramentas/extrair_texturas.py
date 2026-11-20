"""Extrai as texturas DDS de um WAD do GoW III e gera PNGs de preview.

uso: python -I ferramentas/extrair_texturas.py <arquivo.WAD> <pasta_saida>
"""
import os, sys, struct, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wad

TEX_TAG = 0xd0001

def textures(data):
    for e in wad.parse(data):
        if e['tag'] == TEX_TAG and e['name'].lower().endswith('.dds'):
            body = data[e['data_off']:e['data_off'] + e['size']]
            dds = body.find(b'DDS ')
            if dds < 0:
                continue
            h, w = struct.unpack_from('<II', body, dds + 12)
            mips = struct.unpack_from('<I', body, dds + 28)[0]
            fourcc = body[dds + 84:dds + 88].decode('latin1')
            yield e, dds, w, h, mips, fourcc, body

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(out, 'dds'), exist_ok=True)
    os.makedirs(os.path.join(out, 'png'), exist_ok=True)
    data = open(src, 'rb').read()
    info = []
    from PIL import Image
    for e, dds, w, h, mips, fourcc, body in textures(data):
        name = e['name'][:-4]
        p = os.path.join(out, 'dds', name + '.dds')
        open(p, 'wb').write(body[dds:])
        ok = ''
        try:
            Image.open(p).save(os.path.join(out, 'png', name + '.png'))
        except Exception as ex:
            ok = str(ex)
        info.append(dict(nome=name, offset_wad=e['off'], preambulo=dds, largura=w, altura=h, mips=mips, formato=fourcc, erro_png=ok))
        print(f"{name:28s} {w:5d}x{h:<5d} {fourcc:5s} mips={mips} {ok}")
    json.dump(info, open(os.path.join(out, 'texturas.json'), 'w'), indent=1)
