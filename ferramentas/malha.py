"""Leitura de malhas MG (tag 0x520001) do GoW III Remastered — em engenharia reversa.

Formato conhecido até agora (ver CLAUDE.md):
- Grupos (partes) listados em +0x18 (u32, até 0xffff).
- Em cada grupo, "malhas" com entradas de stream de 12 B:
    s32 offset (relativo à própria entrada), u8 a, u8 uso, u8 tipo, u8 b, u32 bytes
  uso 1 / tipo 7 = posição float3 (vértice de stride variável); uso 0x0f = UV float2 (stream próprio).
- Após as entradas: u32 nº de vértices, u32 (nº de triângulos << 8 | flags), u32 ?, u32 ?, índices u16.

uso: python -I ferramentas/malha.py <MG.bin> <pasta_saida>   → um .obj por malha encontrada
"""
import os
import struct
import sys


def grupos(b):
    n = struct.unpack_from('<H', b, 8)[0]
    return list(struct.unpack_from('<%dI' % n, b, 0x18))


def entradas_stream(b, ini):
    """Lê entradas de stream consecutivas a partir de ini. Devolve lista de dicts e o fim."""
    out = []
    p = ini
    while p + 12 <= len(b):
        off, a, uso, tipo, bb, tam = struct.unpack_from('<iBBBBI', b, p)
        alvo = p + off
        if not (0 < alvo < len(b)) or not (0 <= tam < len(b)) or not (1 <= uso <= 0x20) or bb == 0:
            break
        out.append(dict(pos=p, alvo=alvo, a=a, uso=uso, tipo=tipo, b=bb, tam=tam))
        p += 12
    return out, p


def malhas(b, gini, gfim):
    """Procura conjuntos de streams (posição uso1/tipo7) dentro do grupo. Cada conjunto tem um
    buffer de vértices compartilhado e N submalhas: cabeçalhos de 16 B logo após as entradas
    (u32 nv, u32 ntri<<8|flags, u32 offset relativo até os índices, u32 ?)."""
    nsub_grupo = struct.unpack_from('<H', b, gini + 16)[0]
    res = []
    p = gini
    while p < gfim - 12:
        if b[p + 5] == 1 and b[p + 6] == 7:
            ents, fim = entradas_stream(b, p)
            uv = [e for e in ents if e['uso'] == 0x0f]
            if ents and ents[0]['uso'] == 1 and uv:
                stride = ents[0]['b'] * 4               # último byte da entrada = stride em dwords
                total = ents[0]['tam'] // stride if stride else 0
                subs = []
                q = fim
                base = 0
                while base < total:
                    nv, tf, rel, extra = struct.unpack_from('<IIiI', b, q)
                    if not (0 < nv <= total - base) or (tf >> 8) == 0:
                        break
                    subs.append(dict(nv=nv, ntri=tf >> 8, flags=tf & 0xff, ind=q + 8 + rel,
                                     extra=extra, base=base))
                    base += nv
                    q += 16
                if subs:
                    res.append(dict(ents=ents, total=total, stride=stride, uv=uv[0], subs=subs))
                    ultimo = subs[-1]
                    p = (ultimo['ind'] + ultimo['ntri'] * 6 + 3) & ~3
                    continue
        p += 4
    return res


def ler(b):
    gs = grupos(b)
    out = []
    vr = struct.unpack_from('<I', b, 4)[0]
    for gi, g in enumerate(gs):
        maiores = [x for x in gs + [vr, len(b)] if x > g]
        fim = min(maiores)
        osso = struct.unpack_from('<I', b, g + 8)[0]
        for m in malhas(b, g, fim):
            m['grupo'] = gi
            m['osso'] = osso
            out.append(m)
    return out


def vertices(b, m):
    e0 = m['ents'][0]
    st = m['stride']
    pos = [struct.unpack_from('<3f', b, e0['alvo'] + i * st) for i in range(m['total'])]
    us = m['uv']['b'] * 4
    uv = [struct.unpack_from('<2f', b, m['uv']['alvo'] + i * us) for i in range(m['total'])]
    idx = []
    for sm in m['subs']:
        loc = struct.unpack_from('<%dH' % (sm['ntri'] * 3), b, sm['ind'])
        idx += [x + sm['base'] for x in loc]
    return pos, uv, idx


def salvar_obj(caminho, pos, uv, idx):
    with open(caminho, 'w') as f:
        for x, y, z in pos:
            f.write(f'v {x:.6f} {y:.6f} {z:.6f}\n')
        if uv:
            for u, v in uv:
                f.write(f'vt {u:.6f} {v:.6f}\n')
        for i in range(0, len(idx), 3):
            a, c, d = idx[i] + 1, idx[i + 1] + 1, idx[i + 2] + 1
            f.write(f'f {a}/{a} {c}/{c} {d}/{d}\n' if uv else f'f {a} {c} {d}\n')


if __name__ == '__main__':
    b = open(sys.argv[1], 'rb').read()
    os.makedirs(sys.argv[2], exist_ok=True)
    for k, m in enumerate(ler(b)):
        pos, uv, idx = vertices(b, m)
        ok = max(idx) < m['total']
        xs = [p[0] for p in pos]; ys = [p[1] for p in pos]; zs = [p[2] for p in pos]
        print(f"malha {k:2d} grupo {m['grupo']:2d} osso {m['osso']:#x} vért {m['total']:5d} "
              f"sub {[(s['nv'], s['ntri'], hex(s['flags'])) for s in m['subs']]} stride {m['stride']} idx_ok {ok} "
              f"bbox x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}]")
        salvar_obj(os.path.join(sys.argv[2], f'malha{k:02d}_g{m["grupo"]:02d}.obj'), pos, uv, idx)
