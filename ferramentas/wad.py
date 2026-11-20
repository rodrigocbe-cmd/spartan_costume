"""Leitor/escritor de WAD do God of War III Remastered (PS4_LE).

Formato: sequência de entradas, cada uma com cabeçalho de 0x40 bytes:
  u32 tag, u32 size, char name[0x38]
seguido de `size` bytes de dados, alinhado a 16 bytes.
Exceção: tag 0 (ex.: "EntityCount") usa `size` como contador e não tem dados.
"""
import struct, sys

HDR = 0x40

def align(x, a=16):
    return (x + a - 1) & ~(a - 1)

def parse(data):
    off, out = 0, []
    while off + HDR <= len(data):
        tag, size = struct.unpack_from('<II', data, off)
        name = data[off+8:off+HDR].split(b'\0', 1)[0].decode('latin1')
        dsize = 0 if tag == 0 else size
        out.append(dict(off=off, tag=tag, size=dsize, count=size, name=name, data_off=off+HDR))
        off = align(off + HDR + dsize)
    return out

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    ents = parse(d)
    for e in ents:
        print(f"{e['off']:#010x} tag={e['tag']:#06x} size={e['size']:#010x} {e['name']}")
    print(len(ents), 'entradas; fim', hex(ents[-1]['data_off'] + ents[-1]['size']), 'arquivo', hex(len(d)))
