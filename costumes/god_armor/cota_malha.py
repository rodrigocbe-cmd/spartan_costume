"""Cota de malha de AÇO NEGRO (pedido do usuário; antes bronze) nos braços e nas pernas do Kratos (Deus da Guerra; referência:
referencias/god_armor/cota_de_malha_bracos_pernas.jpg — arte do GoW II).

A malha é colada ao corpo, então é só TEXTURA (sem geometria nova): as regiões de braço e de perna das
texturas da pele recebem anéis de bronze (cor), relevo (normal map), brilho (especular) e a camada "pálida"
(5º slot do material) no mesmo tom. Máscaras em UV rasterizadas a partir dos triângulos da pele:
  braços  = conjuntos chest_m (textura do corpo TX27CF5CC1) com |x| > LIMITE_BRACO (pose T);
  pernas  = conjunto head_m das pernas (parte de baixo da textura da cabeça TX4A104642) com y < LIMITE_PERNA.
Antebraços e canelas ficam sob as braçadeiras/grevas; mãos, pés, rosto e peito não mudam.

uso: chamado por texturas_armadura.py (ou python -I costumes/god_armor/cota_malha.py)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
import malha, montar_heroi  # noqa: E402

ORIG = os.path.join(RAIZ, 'original', 'R_HERO00', 'png')
SAIDA = os.path.join(AQUI, 'texturas', 'R_HERO00')

LIMITE_BRACO = 0.24      # |x| na pose T: inclui a axila/trás do ombro (teste 19); o tronco aí fica sob o colete
LIMITE_PERNA = 1.30      # y: do quadril (sob a tanga) para baixo
# pescoço (pedido do usuário): faixa de baixo até um pouco abaixo do meio (~1/4 do pescoço visível).
# Pescoço visível ~y 2,05 (sobre o colarinho do colete, que sobe até 2,09 na frente / 2,16 atrás) .. ~2,20.
LIMITE_PESCOCO = 2.07    # y do topo da malha no pescoço (teste 36: 2,11 alto demais)
PESCOCO_X = 0.13         # |x| máximo (fora disso é ombro/trapézio, sob o colete)
QUEIXO_Z = -0.12         # z < isso = queixo/rosto (fica de fora)
# atrás o colarinho do colete sobe até ~2,16: a malha da nuca vai mais alto para aparecer acima dele (teste 28)
LIMITE_PESCOCO_COSTAS = 2.168   # teste 35/36: mais baixo; o colarinho de trás vai a ~2,16
NUCA_Z0, NUCA_Z1 = -0.10, -0.02   # limite sobe de LIMITE_PESCOCO (z<=Z0) a LIMITE_PESCOCO_COSTAS (z>=Z1)
ANEL_CM = 3.0            # período dos anéis (cm no corpo); 1,5 parecia tecido no jogo (teste 19)
BRONZE = np.array([0.17, 0.155, 0.15])        # aço negro do colete do Dominus (TXFC6E37EC: 33,28,27 .. 60,56,57)
BRONZE_CLARO = np.array([0.42, 0.40, 0.40])   # brilho do aço nos anéis
FUNDO = np.array([0.03, 0.027, 0.026])

# textura de cor -> (normal, especular, 5º slot "pálido") do mesmo material (MAT chest_m / head_m)
TEXTURAS = {
    'TX27CF5CC1.AD3FCC3E': dict(normal='TX27586F46.42C0C6FA', spec='TX4C116490.A6CAABD9', palida='TX60366B5B.8595A315'),
    'TX4A104642.F3349159': dict(normal='TX64D510EB.E179CD6F', spec='TX4395E116.C8DD1FEE', palida='TXBEB53958.0FB769D9'),
}


def carregar(nome):
    return np.asarray(Image.open(os.path.join(ORIG, nome + '.png')).convert('RGBA')).astype(np.float32) / 255


def salvar(nome, rgba):
    os.makedirs(SAIDA, exist_ok=True)
    Image.fromarray((np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(SAIDA, nome + '.png'))


def mascaras():
    """{textura de cor: [(região, máscara HxW 0..1, px por metro), ...]} (região = braco/perna/pescoco;
    cada região tem a própria densidade de texels, para os anéis terem o mesmo tamanho no corpo)"""
    h = montar_heroi.heroi('00')
    alvo = {11: 'TX27CF5CC1.AD3FCC3E', 13: 'TX27CF5CC1.AD3FCC3E', 14: 'TX27CF5CC1.AD3FCC3E',
            10: 'TX4A104642.F3349159'}
    tam = {k: Image.open(os.path.join(ORIG, k + '.png')).size for k in set(alvo.values())}
    imgs, dens = {}, {}
    for p in h['pecas']:
        if p['grupo'] != 21 or p['material'] not in (10, 11):        # mãos (13/14) ficam de fora
            continue
        nome = alvo[p['material']]
        W, H = tam[nome]
        _, uv, _ = malha.vertices(h['mg'], p['m'])
        uv = np.array(uv)
        px = np.c_[(uv[:, 0] % 1) * W, (uv[:, 1] % 1) * H]
        for t in p['T']:
            c = p['P'][t].mean(0)
            # transição suave pela lateral do pescoço (teste 29: atrás da orelha ficava sem malha)
            k = np.clip((c[2] - NUCA_Z0) / (NUCA_Z1 - NUCA_Z0), 0, 1)
            lim = LIMITE_PESCOCO + (LIMITE_PESCOCO_COSTAS - LIMITE_PESCOCO) * k
            if 1.98 < c[1] < lim and abs(c[0]) < PESCOCO_X and c[2] > QUEIXO_Z:
                reg = 'pescoco'
            elif p['material'] == 11 and abs(c[0]) > LIMITE_BRACO:
                reg = 'braco'
            elif p['material'] == 11 and c[1] < 1.98:
                # tronco inteiro abaixo do pescoço: fica sob o colete, mas aparece nas cavas (axila) e entre o
                # colete e o cinto -> malha também (teste 24: axila com cor de pele)
                reg = 'tronco'
            elif p['material'] == 10 and 0.12 < c[1] < LIMITE_PERNA:          # pernas (sem os pés)
                reg = 'perna'
            else:
                continue
            chave = (nome, reg)
            if chave not in imgs:
                imgs[chave] = Image.new('L', tam[nome], 0); dens[chave] = []
            dr = ImageDraw.Draw(imgs[chave])
            q = px[t]
            if np.ptp(q[:, 0]) > W / 2 or np.ptp(q[:, 1]) > H / 2:         # triângulo na costura da repetição
                continue
            dr.polygon([tuple(x) for x in q], fill=255)
            a3 = np.linalg.norm(np.cross(*(p['P'][t[1:]] - p['P'][t[0]])))
            e1, e2 = q[1] - q[0], q[2] - q[0]
            a2 = abs(e1[0] * e2[1] - e1[1] * e2[0])
            if a3 > 1e-6:
                dens[chave].append(np.sqrt(a2 / a3))
    out = {}
    for (nome, reg), im in imgs.items():
        m = np.asarray(im).astype(np.float32) / 255
        m = ndimage.binary_dilation(m > 0.5, iterations=2)                  # cobre as bordas das ilhas
        out.setdefault(nome, []).append((reg, ndimage.gaussian_filter(m.astype(np.float32), 1.5),
                                         float(np.median(dens[(nome, reg)]))))
    return out


def aneis(H, W, periodo):
    """Altura (0..1) de uma malha de anéis entrelaçados (fileiras desencontradas) e máscara dos anéis."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fila = np.floor(yy / (periodo * 0.5))
    xs = xx + (fila % 2) * periodo * 0.5
    cx = (xs % periodo) - periodo / 2
    cy = (yy % (periodo * 0.5)) - periodo * 0.25
    r = np.hypot(cx, cy * 1.6)
    R0, esp = periodo * 0.34, periodo * 0.11
    altura = np.clip(1 - ((r - R0) / esp) ** 2, 0, 1)
    return altura


def cota(nome_cor, regioes):
    t = TEXTURAS[nome_cor]
    cor = carregar(nome_cor)
    H, W = cor.shape[:2]
    alt = np.zeros((H, W), np.float32)
    mask = np.zeros((H, W), np.float32)
    periodos = {}
    for reg, m_r, ppm in regioes:
        periodo = max(4.0, ppm * ANEL_CM / 100)
        periodos[reg] = periodo
        alt = np.where(m_r > mask, aneis(H, W, periodo), alt)
        mask = np.maximum(mask, m_r)
    ruido = ndimage.gaussian_filter(np.random.default_rng(5).random((H, W)), 2.0)
    alt = alt ** 0.7                                              # anel mais cheio, fresta escura nítida
    luz = 0.45 + 0.9 * alt + 0.25 * (ruido - 0.5)
    malha_rgb = FUNDO * (1 - alt[..., None]) + (BRONZE * (1 - alt[..., None] * 0.5) + BRONZE_CLARO * alt[..., None] * 0.5) * luz[..., None]
    m = mask[..., None]
    cor[..., :3] = cor[..., :3] * (1 - m) + malha_rgb * m
    salvar(nome_cor, cor)
    # normal map (DXT5: x no alfa, y no verde; plano = 127)
    nrm = carregar(t['normal'])
    hn, wn = nrm.shape[:2]
    a2 = np.asarray(Image.fromarray((alt * 255).astype(np.uint8)).resize((wn, hn), Image.BILINEAR)).astype(np.float32) / 255
    m2 = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((wn, hn), Image.BILINEAR)).astype(np.float32) / 255
    gy, gx = np.gradient(ndimage.gaussian_filter(a2, 0.6))
    k = 2.4                                                       # relevo mais forte (anéis maiores)
    ny = np.clip(0.5 + k * gy, 0, 1); nx = np.clip(0.5 - k * gx, 0, 1)
    nrm[..., 1] = nrm[..., 1] * (1 - m2) + ny * m2
    nrm[..., 3] = nrm[..., 3] * (1 - m2) + nx * m2
    salvar(t['normal'], nrm)
    # especular: anéis de metal brilham, frestas não
    sp = carregar(t['spec'])
    hs, ws = sp.shape[:2]
    a3 = np.asarray(Image.fromarray((alt * 255).astype(np.uint8)).resize((ws, hs), Image.BILINEAR)).astype(np.float32) / 255
    m3 = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((ws, hs), Image.BILINEAR)).astype(np.float32) / 255
    s = (0.12 + 0.45 * a3)[..., None]
    sp[..., :3] = sp[..., :3] * (1 - m3[..., None]) + s * m3[..., None]
    salvar(t['spec'], sp)
    # camada "pálida" (5º slot): bronze escuro (senão o azulado da pele cinza aparece na malha)
    pal = carregar(t['palida'])
    hp, wp = pal.shape[:2]
    mp = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((wp, hp), Image.BILINEAR)).astype(np.float32) / 255
    mr = np.asarray(Image.fromarray((np.clip(malha_rgb, 0, 1) * 255).astype(np.uint8)).resize((wp, hp), Image.BILINEAR)).astype(np.float32) / 255
    pal[..., :3] = pal[..., :3] * (1 - mp[..., None]) + mr * 0.8 * mp[..., None]
    salvar(t['palida'], pal)
    return mask, periodos


def gerar():
    for nome, regioes in mascaras().items():
        mask, per = cota(nome, regioes)
        print('  cota de malha em %s: %.0f%% da textura; anel (px): %s'
              % (nome, 100 * float((mask > 0.5).mean()), {k: round(v, 1) for k, v in per.items()}))
    manoplas()


# ------------------------------------------------------------------ manoplas (mãos em armadura de placas)
# Referência: arte do GoW II — placas douradas articuladas no dorso e nos dedos, vermelho perto do punho.
# A mão do Kratos = DEDOS/polegar (chest_m-0/-1, região própria de TX27CF5CC1; as duas mãos usam a mesma
# região espelhada) + FAIXAS DE PANO do dorso/punho (cloth_m com x > 0,9, ilha da mão em TX5512508B — a mesma
# textura das faixas dos pés, que ficam). Pinta pela mão direita (pose T: dedos ao longo de +x, dorso = +y).
PLACA_M = 0.04            # comprimento de cada placa (m) ao longo da mão/dedo (2,2 cm ficava detalhado demais, teste 35)
PUNHO_X = 1.00            # nas faixas do dorso: x < isso = punho (vermelho); dorso da mão dourado
COURO_PALMA = np.array([0.14, 0.09, 0.07])
OURO_PLACA = np.array([0.80, 0.58, 0.24])
VERM_PLACA = np.array([82, 25, 16]) / 255.0
MAOS = [
    # material, x mínimo, textura de cor, normal, especular, pálida
    (13, 0.9, 'TX27CF5CC1.AD3FCC3E', 'TX27586F46.42C0C6FA', 'TX4C116490.A6CAABD9', 'TX60366B5B.8595A315'),
    (8, 0.9, 'TX5512508B.F9EA0D02', 'TX587A1BF5.F8EE906B', 'TX0393CBA3.E2D1C1C7', None),
]


def _rasterizar(material, x_min, nome_cor):
    """Mapas em UV (H x W) da mão direita para o material: máscara, x (ao longo da mão) e normal y."""
    import struct
    h = montar_heroi.heroi('00')
    W, H = Image.open(os.path.join(ORIG, nome_cor + '.png')).size
    masc = np.zeros((H, W), np.float32); X = np.zeros((H, W), np.float32); NY = np.zeros((H, W), np.float32)
    for p in h['pecas']:
        if p['grupo'] != 21 or p['material'] != material or p['P'][:, 0].max() < x_min:
            continue
        m = p['m']; mg = h['mg']; st = m['stride']; e = {x['uso']: x for x in m['ents']}
        P = p['P']
        tg = np.array([struct.unpack_from('<4h', mg, e[4]['alvo'] + i * st) for i in range(len(P))], float)[:, :3]
        bt = np.array([struct.unpack_from('<4h', mg, e[5]['alvo'] + i * st) for i in range(len(P))], float)[:, :3]
        n = np.cross(tg, bt); n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        _, uv, _ = malha.vertices(mg, m)
        uv = np.array(uv)
        px = np.c_[(uv[:, 0] % 1) * W, (uv[:, 1] % 1) * H]
        for t in p['T']:
            if P[t, 0].mean() < x_min:
                continue
            q = px[t]
            if np.ptp(q[:, 0]) > W / 2 or np.ptp(q[:, 1]) > H / 2:
                continue
            x0, y0 = np.floor(q.min(0)).astype(int); x1, y1 = np.ceil(q.max(0)).astype(int)
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (q[1, 1] - q[2, 1]) * (q[0, 0] - q[2, 0]) + (q[2, 0] - q[1, 0]) * (q[0, 1] - q[2, 1])
            if abs(d) < 1e-9:
                continue
            w0 = ((q[1, 1] - q[2, 1]) * (gx - q[2, 0]) + (q[2, 0] - q[1, 0]) * (gy - q[2, 1])) / d
            w1 = ((q[2, 1] - q[0, 1]) * (gx - q[2, 0]) + (q[0, 0] - q[2, 0]) * (gy - q[2, 1])) / d
            w2 = 1 - w0 - w1
            den = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
            yy, xx = (gy[den] - 0.5).astype(int) % H, (gx[den] - 0.5).astype(int) % W
            masc[yy, xx] = 1
            X[yy, xx] = (w0 * P[t[0], 0] + w1 * P[t[1], 0] + w2 * P[t[2], 0])[den]
            NY[yy, xx] = (w0 * n[t[0], 1] + w1 * n[t[1], 1] + w2 * n[t[2], 1])[den]
    return masc, X, NY


def _atual(n):
    f = os.path.join(SAIDA, n + '.png')
    return np.asarray(Image.open(f).convert('RGBA')).astype(np.float32) / 255 if os.path.exists(f) else carregar(n)


def _reduz(a, alvo):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize(alvo, Image.BILINEAR)).astype(np.float32) / 255


def manoplas():
    for material, x_min, cor_n, nrm_n, spec_n, pal_n in MAOS:
        masc, X, NY = _rasterizar(material, x_min, cor_n)
        m = ndimage.gaussian_filter(ndimage.binary_dilation(masc > 0.5, iterations=2).astype(np.float32), 1.0)
        fase = (X / PLACA_M) % 1.0
        altura = np.clip(fase * 1.2, 0, 1) * (fase < 0.9)            # placas sobrepostas (rampa + fresta)
        fresta = (fase > 0.9).astype(np.float32)[..., None]
        placa = OURO_PLACA * (0.55 + 0.55 * altura)[..., None]
        placa = placa * (1 - fresta) + np.array([0.12, 0.08, 0.04]) * fresta
        if material == 8:                                            # dorso: punho vermelho
            vm = ndimage.gaussian_filter(((X < PUNHO_X) & (masc > 0)).astype(np.float32), 1.5)[..., None]
            placa = placa * (1 - vm) + VERM_PLACA * (0.7 + 0.5 * altura)[..., None] * vm
        palma = ndimage.gaussian_filter(((NY < -0.45) & (masc > 0)).astype(np.float32), 1.5)[..., None]
        placa = placa * (1 - palma) + COURO_PALMA * (0.8 + 0.3 * altura)[..., None] * palma
        cor = _atual(cor_n)
        cor[..., :3] = cor[..., :3] * (1 - m[..., None]) + placa * m[..., None]
        salvar(cor_n, cor)
        nrm = _atual(nrm_n); hn, wn = nrm.shape[:2]
        a2 = _reduz(altura, (wn, hn)); m2 = _reduz(m, (wn, hn))
        gy, gx = np.gradient(ndimage.gaussian_filter(a2, 0.8))
        nrm[..., 1] = nrm[..., 1] * (1 - m2) + np.clip(0.5 + 2.0 * gy, 0, 1) * m2
        nrm[..., 3] = nrm[..., 3] * (1 - m2) + np.clip(0.5 - 2.0 * gx, 0, 1) * m2
        salvar(nrm_n, nrm)
        sp = _atual(spec_n); hs, ws = sp.shape[:2]
        m3 = _reduz(m, (ws, hs)); a3 = _reduz(altura, (ws, hs)); p3 = _reduz(palma[..., 0], (ws, hs))
        sv = (0.2 + 0.5 * a3) * (1 - p3) + 0.06 * p3
        sp[..., :3] = sp[..., :3] * (1 - m3[..., None]) + sv[..., None] * m3[..., None]
        salvar(spec_n, sp)
        if pal_n:
            pal = _atual(pal_n); hp, wp = pal.shape[:2]
            mp = _reduz(m, (wp, hp)); cp = _reduz(placa, (wp, hp))
            pal[..., :3] = pal[..., :3] * (1 - mp[..., None]) + cp * 0.85 * mp[..., None]
            salvar(pal_n, pal)
        print('  manoplas: %s (material %d) %.1f%% da textura' % (cor_n[:10], material, 100 * float((m > 0.5).mean())))


if __name__ == '__main__':
    gerar()
