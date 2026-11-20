"""Codificação DDS (DXT1/DXT5) com mipmaps, no mesmo layout das texturas do GoW III."""
import io, struct
from PIL import Image

BLOCK = {'DXT1': 8, 'DXT5': 16}

def mip_sizes(w, h, mips, fmt):
    out = []
    for _ in range(mips):
        out.append(max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * BLOCK[fmt])
        w, h = max(1, w // 2), max(1, h // 2)
    return out

def encode_level(img, fmt):
    b = io.BytesIO()
    img.save(b, 'DDS', pixel_format=fmt)
    return b.getvalue()[128:]

def encode(img, fmt, mips):
    """Retorna só os dados de pixel (todos os mips) – o cabeçalho DDS original é mantido."""
    img = img.convert('RGBA')
    w, h = img.size
    parts = []
    for i in range(mips):
        lw, lh = max(1, w >> i), max(1, h >> i)
        lvl = img if i == 0 else img.resize((lw, lh), Image.LANCZOS)
        pw, ph = max(4, lw), max(4, lh)   # blocos 4x4 no mínimo
        if (pw, ph) != (lw, lh):
            lvl = lvl.resize((pw, ph), Image.LANCZOS)
        parts.append(encode_level(lvl, fmt))
    data = b''.join(parts)
    exp = sum(mip_sizes(w, h, mips, fmt))
    assert len(data) == exp, (len(data), exp)
    return data
