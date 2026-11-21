"""Renderizador simples (z-buffer + Lambert) para conferir peças 3D sem abrir o jogo.

uso: render(objetos, guinada_graus, arfagem_graus, tam=(w,h)) -> PIL.Image
objetos = [(vertices (n,3), triângulos (m,3), cor (r,g,b)), ...]
Convenção do GoW III: y para cima, frente do Kratos = -z.
"""
import numpy as np
from PIL import Image


def _rot(guinada, arfagem):
    a, b = np.radians(guinada), np.radians(arfagem)
    ry = np.array([[np.cos(a), 0, -np.sin(a)], [0, 1, 0], [np.sin(a), 0, np.cos(a)]])
    rx = np.array([[1, 0, 0], [0, np.cos(b), np.sin(b)], [0, -np.sin(b), np.cos(b)]])
    return ry @ rx


def render(objetos, guinada=0, arfagem=0, tam=(600, 800), centro=None, escala=None, fundo=(25, 25, 25)):
    W, H = tam
    R = _rot(guinada, arfagem)
    todos = np.vstack([np.asarray(v, float) for v, t, c in objetos])
    if centro is None:
        centro = (todos.min(0) + todos.max(0)) / 2
    vis = (todos - centro) @ R
    if escala is None:
        escala = 0.9 * min(W / max(np.ptp(vis[:, 0]), 1e-6), H / max(np.ptp(vis[:, 1]), 1e-6))
    zbuf = np.full((H, W), np.inf)
    img = np.zeros((H, W, 3))
    img[:] = np.array(fundo) / 255
    luz = np.array([0.4, 0.6, -0.7]); luz /= np.linalg.norm(luz)
    for v, t, cor in objetos:
        p = (np.asarray(v, float) - centro) @ R
        sx = W / 2 + p[:, 0] * escala
        sy = H / 2 - p[:, 1] * escala
        sz = -p[:, 2]                           # câmera olhando para +z do Kratos (de frente = -z)
        t = np.asarray(t)
        n = np.cross(p[t[:, 1]] - p[t[:, 0]], p[t[:, 2]] - p[t[:, 0]])
        nn = np.linalg.norm(n, axis=1, keepdims=True); nn[nn == 0] = 1
        n = n / nn
        lum = np.clip(np.abs(n @ (luz @ R)), 0, 1) * 0.75 + 0.25
        c = np.array(cor) / 255
        for k, (a, b, d) in enumerate(t):
            xs = np.array([sx[a], sx[b], sx[d]]); ys = np.array([sy[a], sy[b], sy[d]]); zs = np.array([sz[a], sz[b], sz[d]])
            x0, x1 = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
            y0, y1 = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
            if x0 > x1 or y0 > y1:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(den) < 1e-9:
                continue
            w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / den
            w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / den
            w2 = 1 - w0 - w1
            dentro = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            if not dentro.any():
                continue
            z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            m = dentro & (z < sub)
            sub[m] = z[m]
            img[y0:y1 + 1, x0:x1 + 1][m] = c * lum[k]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def kratos(b, sk, grupos_excluir=(), grupos_modelo=()):
    """Malhas do Kratos (MG) montadas na pose de ligação: [(v, t, cor)].
    grupos_modelo = grupos rígidos gravados em espaço do modelo (ex.: peças da armadura em ossos JO…)."""
    import malha, esqueleto
    out = []
    for m in malha.ler(b):
        if m['grupo'] in grupos_excluir:
            continue
        pos, _, idx = malha.vertices(b, m)
        pos = np.array(pos)
        if m['stride'] == 40 or m['grupo'] in (0, 5, 20, 21) or m['grupo'] in grupos_modelo:
            w = pos                                  # pele/modelo
        else:
            w = esqueleto.aplicar(sk['mundo'][m['osso']], pos)
        out.append((w, np.array(idx).reshape(-1, 3), (170, 160, 150)))
    return out
