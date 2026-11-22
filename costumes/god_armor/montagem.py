"""Deus da Guerra = Kratos padrão (R_HERO00) + peças de outros trajes do jogo (plano do usuário, 2026-11-21).

  - tanga + cinto do FANTASMA DO CAOS (R_HERO04, material skirt_m: cinto rígido no JOBack1 + 11 malhas com
    pesos nos ossos de saia dele); parte metálica dourada no tom da armadura;
  - peitoral + ombros do DOMINUS (R_HERO06, grupo da pele: materiais kratos06skirt_fancy_m e fancy_mred;
    só ossos do corpo);
  - braçadeiras, luvas, tornozeleiras e calçados do Kratos padrão (ficam como estão);
  - ombreiras de carneiro já construídas (construir.so_ombreiras: grupos 9/6; resto do Velo oculto);
  - SAI: pano vermelho do Kratos (skirt_cloth_m, fica para depois) e o cinto do Kratos (grupo 14).

Como (ver CLAUDE.md):
  * materiais + texturas + shaders copiados dos WADs doadores (wad_edicao.copiar_material) e acrescentados à
    lista do modelo (16 blocos de variantes; bloco 9 = _sw20) -> índices 16, 17, 18;
  * esqueleto: juntas de saia 160..223 (nomes, matrizes, poses inversas) e os 2 SCR_cloth vêm do Fantasma
    (cada traje usa essas juntas com outros nomes/posições; os ossos do corpo são iguais em todos);
  * malha: peças extraídas dos MG doadores com os pesos originais (malha_transplante.extrair) e gravadas
    em grupos livres do Kratos: 14 (cinto do Kratos) <- tanga do Fantasma, 18 (ShinArmor) <- peitoral do
    Dominus; descritores num espaço aberto antes da região de vértices.
"""
import os
import sys

import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
sys.path.insert(0, AQUI)
import esqueleto, malha, malha_transplante as MT, wad_edicao as WE, dds  # noqa: E402
from extrair_texturas import textures  # noqa: E402

MG_K, MDL_K = 'MG_b826bd6e_0', 'MDL_b826bd6e'
JUNTAS_SAIA = range(160, 224)
OURO = np.array([0.80, 0.58, 0.24])          # mesmo dourado das ombreiras (texturas_armadura.OURO)
TEX_SAIA_COR = 'TXA6C9CFBE.9BA0F783.dds'     # cor da tanga/cinto do Fantasma


def _ler_jogo(nome):
    import trajes
    return trajes.ler_jogo(trajes.W + nome)


def _mg(w, nome):
    return w.dados(w.idx(nome, 0x520001))


def _esqueleto(w):
    i = [k for k, (e, b) in enumerate(w.blocos) if e['tag'] == 0x1f0001 and e['name'] == '' and len(b) > 0x9000][0]
    return i, w.dados(i)


def _faixa_vermelha(out, metal):
    """Copia a faixa com rebite (eixo diagonal da textura) para a área livre, deitada, com o couro em
    vermelho do peitoral (rebites continuam dourados)."""
    from scipy import ndimage
    H, W = out.shape[:2]
    T0, Pn = np.array(FAIXA_UV['topo'], float), np.array(FAIXA_UV['ponta'], float)
    comp = np.linalg.norm(Pn - T0)
    dirv = (Pn - T0) / comp; perp = np.array([dirv[1], -dirv[0]])
    m = FAIXA_UV['meia']
    xs = np.arange(int(comp)); ys = np.arange(-m, m)
    gx, gy = np.meshgrid(xs, ys)
    src = T0[None, None, :] + gx[..., None] * dirv + gy[..., None] * perp        # (px x, px y) na original
    amostra = lambda img: ndimage.map_coordinates(img, [src[..., 1], src[..., 0]], order=1, mode='nearest')
    rgb = np.stack([amostra(out[..., c]) for c in range(3)], -1)
    met = amostra(metal)[..., None]
    L = rgb @ np.array([0.299, 0.587, 0.114])
    ref = np.median(L[met[..., 0] < 0.3])
    verm = np.clip(VERMELHO_PEITO * (0.45 + 0.75 * L / max(ref, 1e-3))[..., None], 0, 1)
    nova = verm * (1 - met) + rgb * met
    x0, yc = FAIXA_VERMELHA['x0'], FAIXA_VERMELHA['y']
    out = out.copy()
    out[yc - m:yc + m, x0:x0 + nova.shape[1]] = nova
    return out


def _trocar_textura(w, nome, png):
    """Troca os pixels (todos os mips) da textura `nome` (sem .dds) do WAD pela imagem `png` (mesmo tamanho)."""
    i = w.idx(nome + '.dds', 0xd0001)
    bloco = bytes(w.blocos[i][1])
    (e, off, tw, th, mips, fmt, body), = list(textures(bloco))
    img = Image.open(png).convert('RGBA')
    assert img.size == (tw, th), (nome, img.size, (tw, th))
    pix = dds.encode(img, fmt, mips)
    b = bytearray(bloco)
    ini = e['data_off'] + off + 128
    b[ini:ini + len(pix)] = pix
    w.blocos[i][1] = b


def _peitoral_gow2(w, log):
    """Texturas do colete do Dominus com o desenho do GoW II (geradas por peitoral_gow2.py)."""
    import peitoral_gow2 as PG
    for nome in (PG.COR, PG.NORMAL, PG.ESPEC):
        png = os.path.join(PG.SAIDA, nome + '.png')
        if not os.path.exists(png):
            log('  AVISO: %s não gerado (rode peitoral_gow2.py)' % png)
            return
        _trocar_textura(w, nome, png)
    log('  peitoral: desenho do GoW II (cor, normal, especular)')


def _dourar_metal(w, log):
    """Cinto/faixas/rebites de metal (prateado, pouco saturado) da tanga -> dourado; couro fica."""
    i = w.idx(TEX_SAIA_COR, 0xd0001)
    bloco = bytes(w.blocos[i][1])
    (e, off, tw, th, mips, fmt, body), = list(textures(bloco))
    png = os.path.join(RAIZ, 'original', 'R_HERO04', 'png', TEX_SAIA_COR[:-4] + '.png')
    rgb = np.asarray(Image.open(png).convert('RGB')).astype(np.float32) / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    s = (mx - mn) / np.maximum(mx, 1e-3)
    L = rgb @ np.array([0.299, 0.587, 0.114])
    metal = np.clip((0.30 - s) / 0.12, 0, 1) * np.clip((L - 0.12) / 0.1, 0, 1)
    from scipy import ndimage
    metal = ndimage.gaussian_filter(metal, 1.0)[..., None]
    ref = np.median(L[metal[..., 0] > 0.8]) if (metal > 0.8).any() else 0.5
    ouro = np.clip(OURO * 1.15 * (L / ref)[..., None] ** 1.1, 0, 1)
    out = rgb * (1 - metal) + ouro * metal
    # faixas do avental da frente (as diagonais com rebites, à esquerda da textura) também em vermelho (teste 31)
    x1, y0, y1 = AREA_FAIXAS_FRENTE
    L2 = out[y0:y1, :x1] @ np.array([0.299, 0.587, 0.114])
    m2 = metal[y0:y1, :x1]
    ref2 = np.median(L2[m2[..., 0] < 0.3])
    verm = np.clip(VERMELHO_PEITO * (0.45 + 0.75 * L2 / max(ref2, 1e-3))[..., None], 0, 1)
    out[y0:y1, :x1] = verm * (1 - m2) + out[y0:y1, :x1] * m2
    out = _faixa_vermelha(out, metal[..., 0])
    # cinturão: painel central (oval com arabescos) no PRETO do peitoral, borda/nervura douradas (teste 34)
    H, W = out.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x0, x1, yc, r = PAINEL_CINTO
    dx = np.clip(xx, x0 + r, x1 - r) - xx
    dist = np.hypot(dx, yy - yc)                           # cápsula (retângulo com pontas redondas)
    mp = np.clip((r - 6 - dist) / 3, 0, 1)[..., None]      # 6 px para dentro: a nervura fica dourada
    Lp = rgb @ np.array([0.299, 0.587, 0.114])
    sel = mp[..., 0] > 0.5
    Ln = Lp / max(np.median(Lp[sel]), 1e-3)
    preto = np.clip(PRETO_PEITO * (0.55 + 0.6 * Ln)[..., None], 0, 1)
    out = out * (1 - mp) + preto * mp
    img = Image.fromarray((out * 255 + 0.5).astype(np.uint8)).convert('RGBA')
    pix = dds.encode(img, fmt, mips)
    b = bytearray(bloco)
    ini = e['data_off'] + off + 128
    b[ini:ini + len(pix)] = pix
    w.blocos[i][1] = b
    log('  metal da tanga dourado (%d%% da textura)' % round(100 * float((metal > 0.5).mean())))


FOLGA_PANO = 0.015        # pano vermelho fica 1,5 cm por DENTRO da tanga onde ela cobre
FOLGA_CORPO = 0.006       # ... sem chegar a menos de 6 mm da pele
SOBRA_PANO = 0.05         # fica só o pano abaixo de (barra da tanga + 5 cm); o resto, escondido, sai


# --- tanga: sem o painel de trás (cobria a bunda) + faixas de couro em volta (pedido de 2026-11-21)
PECAS_TRAS = {2, 3, 11, 12, 13}          # índices (ordem de extrair) dos painéis de trás da tanga do Fantasma
PECAS_LADO = {6, 10}                     # laterais (substituídas pelas faixas; elas acompanhavam a coxa)
FAIXAS = dict(n=16, largura=0.06, ang_min=65.0, y_topo=1.46, y_base=1.12, folga=0.008)
# uma faixa com rebite na textura da tanga (TXA6C9CFBE, 1024 px): eixo topo -> ponta, meia largura
FAIXA_UV = dict(topo=(240, 575), ponta=(185, 870), meia=16, tam=1024)
# cópia VERMELHA dessa faixa (pedido do usuário, teste 29) numa área livre da textura (canto inf. esq.),
# deitada: topo em x0, ponta em x0+comprimento, centro em y. As faixas penduradas usam a cópia (a original
# também é usada pelas faixas do avental da frente, que ficam como estão)
FAIXA_VERMELHA = dict(x0=40, y=936)
VERMELHO_PEITO = np.array([82, 25, 16]) / 255.0       # vermelho do colete do Dominus
AREA_FAIXAS_FRENTE = (375, 430, 890)                   # x < 375, 430 <= y < 890 (px): faixas do avental da frente
PRETO_PEITO = np.array([40, 35, 34]) / 255.0           # preto do colete do Dominus
PAINEL_CINTO = (45, 978, 318, 76)                      # cápsula do painel com arabescos do cinturão: x0, x1, y centro, raio (px)


def _faixas(angulos, y_topo, y_base, folga, ref_pecas, registro, larg=None):
    """Faixas (face dupla, UV na cópia vermelha) nos `angulos` (rad, 0 = frente, + = lado direito do Kratos),
    seguindo a superfície das `ref_pecas` + folga; pesos = os do vértice mais próximo delas (k=1)."""
    import construir
    from scipy.spatial import cKDTree
    ref = np.vstack([c['pos'] for c in ref_pecas])
    cz = -0.03
    ang = lambda Q: np.arctan2(Q[:, 0], -(Q[:, 2] - cz))
    rad = lambda Q: np.hypot(Q[:, 0], Q[:, 2] - cz)
    arv = cKDTree(np.c_[ang(ref) * 0.25, ref[:, 1]])
    T0, Pn = np.array(FAIXA_UV['topo'], float), np.array(FAIXA_UV['ponta'], float)
    comp = np.linalg.norm(Pn - T0)
    T0 = np.array([FAIXA_VERMELHA['x0'], FAIXA_VERMELHA['y']], float)     # usa a cópia vermelha deitada
    eixo = np.array([comp, 0.0]); perp = np.array([0.0, float(FAIXA_UV['meia'])])
    largura = larg or FAIXAS['largura']
    linhas = 6
    P, UV, T = [], [], []
    for a in angulos:
        d = np.array([np.sin(a), 0, -np.cos(a)]); lat = np.array([np.cos(a), 0, np.sin(a)])
        base = len(P)
        for j in range(linhas):
            t = j / (linhas - 1)
            y = y_topo + (y_base - y_topo) * t
            _, ii = arv.query([a * 0.25, y], k=4)
            r = rad(ref)[ii].max() + folga + 0.01 * t                     # leve abertura para baixo
            c = np.array([0, y, cz]) + d * r
            for sgn in (-1, 1):
                P.append(c + lat * sgn * largura / 2)
                q = T0 + eixo * t + perp * sgn
                UV.append((q[0] / FAIXA_UV['tam'], q[1] / FAIXA_UV['tam']))
        for j in range(linhas - 1):
            i0 = base + 2 * j
            T += [[i0, i0 + 1, i0 + 3], [i0, i0 + 3, i0 + 2]]
    P, UV, T = np.array(P), np.array(UV), np.array(T)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    radv = P[T].mean(1) - np.array([0, 0, cz]); radv[:, 1] = 0
    inv = (fn * radv).sum(1) < 0
    T[inv] = T[inv][:, [0, 2, 1]]                                  # anti-horário = normal para fora
    N, Tg, B = construir.referencial(P, T, UV)                     # só a face de fora (dupla anularia)
    T = np.vstack([T, T[:, [0, 2, 1]]])                            # face de trás
    c = dict(pos=P, tan=construir.empacotar(Tg), bit=construir.empacotar(B), uv=UV,
             ossos=np.zeros((len(P), 4), np.int64), pesos=np.zeros((len(P), 4), np.int64),
             tris=T[:, [0, 2, 1]], material=None, registro=registro, caudas={}, origem=('faixas',))
    # pesos = os do vértice MAIS PRÓXIMO das peças de referência (k=1, sem média): cada faixa se move como a
    # parte da tanga original no mesmo lugar (média entre peças/cinto rígido fazia tremer e entrar na coxa)
    MT.repesar([c], ref_pecas, k=1)
    return c


# faixas sobre a coxa ESQUERDA (x < 0): a tanga do Fantasma só tem faixas sobre a direita (peças 8/9); teste 33
FAIXAS_COXA_ESQ = dict(ang=(-58.0, -15.0), n=4, y_topo=1.46, y_base=1.03, folga=0.012)


def faixas_couro(saia_toda, log):
    """Faixas de couro penduradas nos lados e atrás (substituem painel de trás e laterais) + faixas na frente
    da coxa esquerda, por cima do avental."""
    f = FAIXAS
    removidas = [saia_toda[k] for k in sorted(PECAS_TRAS | PECAS_LADO)]
    lados = np.r_[np.linspace(np.radians(f['ang_min']), np.pi, f['n'] // 2 + 1)[:-1],
                  -np.linspace(np.radians(f['ang_min']), np.pi, f['n'] // 2 + 1)[1:]]
    c1 = _faixas(lados, f['y_topo'], f['y_base'], f['folga'], removidas, saia_toda[6]['registro'])
    e = FAIXAS_COXA_ESQ
    frente = np.radians(np.linspace(e['ang'][0], e['ang'][1], e['n']))
    c2 = _faixas(frente, e['y_topo'], e['y_base'], e['folga'], [saia_toda[4], saia_toda[7]], saia_toda[6]['registro'])
    log('  faixas de couro: %d (lados/costas, y %.2f..%.2f) + %d na coxa esquerda (y %.2f..%.2f)'
        % (len(lados), f['y_topo'], f['y_base'], len(frente), e['y_topo'], e['y_base']))
    return [c1, c2]


def _pano(cfg, ref_pecas, bloco, registro):
    """Pano em grade (colunas x linhas) num setor de ângulos, do cinto até o joelho, seguindo a superfície das
    `ref_pecas` + folga (abrindo um pouco para baixo); UV no `bloco` da textura do pano; pesos k=1 das peças."""
    import construir
    import pano_cfg as PC
    from scipy.spatial import cKDTree
    ref = np.vstack([c['pos'] for c in ref_pecas])
    cz = -0.03

    def ang(Q):        # 0 = frente, + = lado direito; contínuo de -90° a 270° (volta pela direita e pelas costas)
        a = np.arctan2(Q[:, 0], -(Q[:, 2] - cz))
        return np.where(a < -np.pi / 2, a + 2 * np.pi, a)
    rad = lambda Q: np.hypot(Q[:, 0], Q[:, 2] - cz)
    arv = cKDTree(np.c_[ang(ref) * 0.25, ref[:, 1]])
    # bordas (ângulo no topo e na barra: inclinadas como no pano original) e barra y(ângulo)
    a0t, a1t = np.radians(cfg['ang_topo'])
    a0b, a1b = np.radians(cfg['ang_base'])
    barra_a, barra_y = np.radians([p[0] for p in PC.BARRA]), np.array([p[1] for p in PC.BARRA])
    nc, nl = cfg['colunas'], cfg['linhas']
    bx0, by0, bx1, by1 = bloco
    W, H = PC.TEX_TAM
    P, UV = [], []
    for j in range(nl):
        t = j / (nl - 1)
        a0, a1 = a0t + (a0b - a0t) * t, a1t + (a1b - a1t) * t
        for i in range(nc + 1):
            s = i / nc
            a = a0 + (a1 - a0) * s
            y = PC.Y_TOPO + (np.interp(a, barra_a, barra_y) - PC.Y_TOPO) * t
            _, ii = arv.query([a * 0.25, min(y, ref[:, 1].max())], k=4)
            folga = np.interp(a, np.radians([f[0] for f in cfg['folga']]), [f[1] for f in cfg['folga']])
            r = rad(ref)[ii].max() + folga + 0.02 * t
            P.append(np.array([np.sin(a) * r, y, cz - np.cos(a) * r]))
            UV.append(((bx0 + (bx1 - bx0) * s) / W, (by0 + (by1 - by0) * t) / H))
    P, UV = np.array(P), np.array(UV)
    T = []
    for j in range(nl - 1):
        for i in range(nc):
            k = j * (nc + 1) + i
            T += [[k, k + 1, k + nc + 2], [k, k + nc + 2, k + nc + 1]]
    T = np.array(T)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    radv = P[T].mean(1) - np.array([0, 0, cz]); radv[:, 1] = 0
    inv = (fn * radv).sum(1) < 0
    T[inv] = T[inv][:, [0, 2, 1]]                                  # anti-horário = normal para fora
    N, Tg, B = construir.referencial(P, T, UV)                     # só a face de fora
    T = np.vstack([T, T[:, [0, 2, 1]]])                            # face de dentro
    c = dict(pos=P, tan=construir.empacotar(Tg), bit=construir.empacotar(B), uv=UV,
             ossos=np.zeros((len(P), 4), np.int64), pesos=np.zeros((len(P), 4), np.int64),
             tris=T[:, [0, 2, 1]], material=PC.MATERIAL, registro=registro, caudas={}, origem=('pano',))
    MT.repesar([c], ref_pecas, k=1)
    return c


def pano_novo(saia_toda, faixas, log):
    """Pano vermelho novo (pano_cfg), na posição e inclinação do pano original do Kratos: começa na frente, um
    pouco à esquerda do centro (painel com a grega, por cima do avental/faixas, borda inclinada para a direita ao
    descer), dá a volta pela direita e pelas costas (por cima das faixas de couro) com a barra subindo, até o quadril
    esquerdo."""
    import pano_cfg as PC
    frente_ref = [saia_toda[k] for k in (4, 5, 7, 8, 9)] + faixas[1:]
    tras_ref = [saia_toda[k] for k in sorted(PECAS_TRAS | PECAS_LADO)]
    reg = saia_toda[6]['registro']
    tras_ref = tras_ref + [saia_toda[k] for k in (4, 5, 7, 8, 9)] + faixas[:1]   # por cima do avental e das faixas
    f = _pano(PC.FRENTE, frente_ref, PC.BLOCO_FRENTE, reg)
    t = _pano(PC.TRAS, tras_ref, PC.BLOCO_TRAS, reg)
    log('  pano vermelho novo: frente %d tri, trás %d tri (material %d)' % (len(f['tris']), len(t['tris']), PC.MATERIAL))
    return [f, t]


def pano_vermelho(mg_k, saia, sk_k, log):
    """Pano vermelho do Kratos (skirt_cloth_m, material 15 do grupo da pele) por BAIXO da tanga do Fantasma:
    onde a tanga cobre, o pano é puxado para dentro (raio da tanga - FOLGA_PANO, sem entrar no corpo); abaixo
    da barra volta à forma original. Pesos copiados da tanga (ossos de saia do Fantasma)."""
    from scipy.spatial import cKDTree
    pano = MT.extrair(mg_k, sk_k, lambda m: m['grupo'] == 21 and m['material'] == 15)
    S = np.vstack([c['pos'] for c in saia])
    pele = MT.extrair(mg_k, sk_k, lambda m: m['grupo'] == 21 and m['material'] in (10, 11))
    C = np.vstack([c['pos'] for c in pele])
    cz = -0.03
    ang = lambda Q: np.arctan2(Q[:, 0], -(Q[:, 2] - cz))
    rad = lambda Q: np.hypot(Q[:, 0], Q[:, 2] - cz)
    # raio da tanga e do corpo por (ângulo, altura)
    esc = np.array([0.25, 1.0])                             # 1 rad de ângulo ~ 25 cm
    arv_s = cKDTree(np.c_[ang(S) * esc[0], S[:, 1]])
    perto_corpo = np.abs(C[:, 1] - 1.2) < 0.45
    Cb = C[perto_corpo]
    arv_c = cKDTree(np.c_[ang(Cb) * esc[0], Cb[:, 1]])
    y_barra = np.percentile(S[:, 1], 2)                     # barra da tanga
    mexidos = 0
    for c in pano:
        P = c['pos']
        q = np.c_[ang(P) * esc[0], P[:, 1]]
        _, i_s = arv_s.query(q, k=4)
        r_s = rad(S)[i_s].min(1)
        _, i_c = arv_c.query(q, k=4)
        r_c = rad(Cb)[i_c].max(1)
        alvo = np.maximum(np.minimum(rad(P), r_s - FOLGA_PANO), r_c + FOLGA_CORPO)
        t = np.clip((P[:, 1] - (y_barra - 0.06)) / 0.08, 0, 1)    # 0 abaixo da barra .. 1 coberto
        novo = rad(P) + (alvo - rad(P)) * t
        f = novo / np.maximum(rad(P), 1e-6)
        Q = P.copy()
        Q[:, 0] = P[:, 0] * f
        Q[:, 2] = cz + (P[:, 2] - cz) * f
        mexidos += int((np.abs(f - 1) > 1e-3).sum())
        c['pos'] = Q
    # o que fica totalmente sob a tanga não aparece e encostaria nela (corpo e tanga muito próximos): sai
    tirados = 0
    for c in pano:
        manter = (c['pos'][c['tris']][:, :, 1] < y_barra + SOBRA_PANO).any(1)
        tirados += int((~manter).sum())
        tp = c['tris'][manter]
        vs = np.unique(tp)
        mapa = -np.ones(len(c['pos']), np.int64); mapa[vs] = np.arange(len(vs))
        for k in ('pos', 'tan', 'bit', 'uv', 'ossos', 'pesos'):
            c[k] = c[k][vs]
        c['tris'] = mapa[tp]
    pano = [c for c in pano if len(c['tris'])]
    log('  pano vermelho: %d triângulos sob a tanga removidos' % tirados)
    MT.repesar(pano, saia)
    log('  pano vermelho: %d partes, %d triângulos (%d vértices puxados p/ dentro da tanga; barra y=%.2f)'
        % (len(pano), sum(len(c['tris']) for c in pano), mexidos, y_barra))
    return pano


# --- física nas tiras do braço (teste: 1 tira, braço direito) ------------------------------------------------
# Não há cadeia de saia livre: a cadeia da frente-DIREITA (177..182) passa a ser filha do osso do braço; os
# vértices da tanga/pano que a usavam vão para a cadeia do centro (171..176). (Teste 1 usou a 165: é o 1º campo
# do cabeçalho do SCR_cloth [âncora da simulação?] -> o pano da frente inteiro ficou "em pé", seguindo o braço.)
CADEIA_BRACO = dict(raiz=177, n=6, substituta=171, pai=0x60, tira=4)
# esferas de colisão no braço (osso, posição no espaço do modelo [pose T], raio): a tira não entra no braço
ESFERAS_BRACO = [(0x60, (0.40, 1.955, 0.02), 0.075), (0x60, (0.48, 1.955, 0.02), 0.07),
                 (0x60, (0.56, 1.955, 0.02), 0.065)]


def _cadeia_braco_esqueleto(b, pontos):
    """Religa a cadeia CADEIA_BRACO ao osso do braço e põe as juntas em `pontos` (modelo, pose T)."""
    import struct
    cb = CADEIA_BRACO
    d = bytearray(b)
    n, i_nomes, loc, inv = esqueleto._offsets(b)
    sk = esqueleto.ler(b)
    js = list(range(cb['raiz'], cb['raiz'] + cb['n']))

    def H(j):
        return list(struct.unpack_from('<4H', d, 0x14 + 8 * j))

    def put(j, v):
        struct.pack_into('<4H', d, 0x14 + 8 * j, *v)
    # tira as juntas da lista de filhos do pai antigo (são irmãs consecutivas: raiz..raiz+5 -> próxima)
    pai_velho = sk['pais'][js[0]]
    hv = H(pai_velho)
    depois = H(js[-1])[2]
    if hv[1] == js[0]:
        hv[1] = depois
        put(pai_velho, hv)
    else:
        a = hv[1]
        while H(a)[2] != js[0]:
            a = H(a)[2]
            assert a != 0xffff, 'cadeia não encontrada entre os filhos do pai antigo'
        ha = H(a)
        ha[2] = depois
        put(a, ha)
    # e põe como primeiros filhos do osso do braço
    hp = H(cb['pai'])
    hl = H(js[-1])
    hl[2] = hp[1]
    put(js[-1], hl)
    hp[1] = js[0]
    put(cb['pai'], hp)
    for j in js:
        h = H(j)
        h[3] = cb['pai']
        put(j, h)
    # matrizes: eixo Y da junta = contra o sentido da cadeia (como nas juntas da saia)
    Gp = sk['mundo'][cb['pai']]
    for k, j in enumerate(js):
        a, b2 = (k, k + 1) if k + 1 < len(pontos) else (k - 1, k)
        dirc = pontos[b2] - pontos[a]
        y = -dirc / np.linalg.norm(dirc)
        x = np.cross(y, np.array([0, 0, 1.0]))
        x /= np.linalg.norm(x)
        z = np.cross(x, y)
        G = np.eye(4)
        G[0, :3], G[1, :3], G[2, :3], G[3, :3] = x, y, z, pontos[k]
        L = G @ np.linalg.inv(Gp)
        d[loc + j * 64:loc + (j + 1) * 64] = L.astype('<f4').tobytes()
        d[inv + j * 64:inv + (j + 1) * 64] = np.linalg.inv(G).astype('<f4').tobytes()
    return bytes(d)


def _cadeia_braco_scr(dados, sk):
    """SCR_cloth da frente + esferas de colisão no braço (posição no espaço local do osso)."""
    import struct
    d = bytearray(dados)
    nr = struct.unpack_from('<i', d, 0x84)[0]
    ne = struct.unpack_from('<i', d, 0x94)[0]
    o = 0xb0 + 4 * nr + 24 * ne
    ids = [struct.unpack_from('<i', d, 0xb0 + 4 * nr + 24 * k + 20)[0] for k in range(ne)]
    extra = b''
    for k, (osso, pos, r) in enumerate(ESFERAS_BRACO):
        pl = esqueleto.aplicar(np.linalg.inv(sk['mundo'][osso]), np.array([pos]))[0]
        extra += struct.pack('<4f2i', *pl, r, osso, max(ids) + 1 + k)
    struct.pack_into('<i', d, 0x94, ne + len(ESFERAS_BRACO))
    return bytes(d[:o]) + extra + bytes(d[o:])


def tira_braco_fisica(sk, obst, registro, log):
    """A tira CADEIA_BRACO['tira'] do braço direito como conjunto com pesos na cadeia; devolve (conjunto, juntas)."""
    import construir
    cb = CADEIA_BRACO
    P, UV, T = construir.tiras_braco(sk, obst)
    k, nt = cb['tira'], construir.TIRAS_BRACO['n']
    v = np.arange(5 * k, 5 * k + 5)
    rows = [3 * k + i for i in range(3)] + [3 * nt + 3 * k + i for i in range(3)]
    Pv, UVv = P[v], UV[v]
    Tv = np.searchsorted(v, T[rows])
    # linha central: base, meio (linha s1) e ponta
    eixo_pts = np.array([(Pv[0] + Pv[1]) / 2, (Pv[2] + Pv[3]) / 2, Pv[4]])
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(eixo_pts, axis=0), axis=1))]
    d0 = (eixo_pts[1] - eixo_pts[0]) / np.linalg.norm(eixo_pts[1] - eixo_pts[0])
    raiz = eixo_pts[0] - d0 * 0.03
    pts = np.array([raiz] + [np.array([np.interp(s, seg, eixo_pts[:, c]) for c in range(3)])
                             for s in np.linspace(0, seg[-1], cb['n'] - 1)])
    # pesos: entre as 2 juntas mais próximas
    ossos = np.zeros((len(Pv), 4), np.int64)
    pesos = np.zeros((len(Pv), 4), np.int64)
    for i, q in enumerate(Pv):
        dist = np.linalg.norm(pts - q, axis=1)
        a, b = np.argsort(dist)[:2]
        wa = dist[b] / (dist[a] + dist[b])
        ossos[i, :2] = cb['raiz'] + a, cb['raiz'] + b
        pesos[i, 0] = int(round(255 * wa))
        pesos[i, 1] = 255 - pesos[i, 0]
    N, Tg, B = construir.referencial(Pv, Tv[:3], UVv)
    c = dict(pos=Pv, tan=construir.empacotar(Tg), bit=construir.empacotar(B), uv=UVv, ossos=ossos, pesos=pesos,
             tris=Tv, material=4, registro=registro, caudas={}, origem=('tira_braco',))
    log('  física na tira do braço direito: cadeia %d..%d religada ao osso 0x%x, %d tri'
        % (cb['raiz'], cb['raiz'] + cb['n'] - 1, cb['pai'], len(Tv)))
    return c, pts


def _trocar_cadeia(conjuntos):
    """Vértices que usavam a cadeia do braço passam para a cadeia substituta (mesmo nível)."""
    cb = CADEIA_BRACO
    for c in conjuntos:
        o, w = c['ossos'], c['pesos']
        m = (o >= cb['raiz']) & (o < cb['raiz'] + cb['n']) & (w > 0)
        o[m] = o[m] - cb['raiz'] + cb['substituta']
        for i in np.where(m.any(1))[0]:          # dois pesos no mesmo osso: soma
            acc = {}
            for oo, pp in zip(o[i], w[i]):
                if pp:
                    acc[int(oo)] = acc.get(int(oo), 0) + int(pp)
            it = sorted(acc.items(), key=lambda x: -x[1])[:4]
            o[i] = 0
            w[i] = 0
            for kk, (oo, pp) in enumerate(it):
                o[i, kk] = oo
                w[i, kk] = pp


def montar(dados, log=print, etapas=('materiais', 'esqueleto', 'malha', 'pano_novo', 'fisica_braco')):   # 'pano' = pano vermelho (deixava o FPS baixo, teste 18)
    import construir
    w = WE.Wad(dados)
    w04 = WE.Wad(_ler_jogo('R_HERO04.WAD'))
    w06 = WE.Wad(_ler_jogo('R_HERO06.WAD'))

    # 1) materiais (+ texturas/shaders) e lista do modelo
    for doador, nomes in ((w04, ['skirt_m', 'skirt_m_sw20']),
                          (w06, ['kratos06skirt_fancy_m', 'kratos06skirt_fancy_m_sw20', 'fancy_mred', 'fancy_mred_sw20'])):
        for n in nomes:
            WE.copiar_material(w, doador, 'templatens:' + n, log)
    base = ['templatens:skirt_m', 'templatens:kratos06skirt_fancy_m', 'templatens:fancy_mred']
    idx = WE.acrescentar_materiais(w, MG_K, MDL_K, base, variantes={9: {m: m + '_sw20' for m in base}})
    M_SAIA, M_FANCY, M_RED = idx
    log('  materiais novos:', dict(zip(base, idx)))
    _dourar_metal(w, log)
    _peitoral_gow2(w, log)
    if 'esqueleto' not in etapas and 'malha' not in etapas:
        WE.atualizar_matx(w, log)
        return w.bytes()

    # 2) esqueleto: juntas de saia e scripts de tecido do Fantasma
    i_sk, sk_k = _esqueleto(w)
    _, sk_04b = _esqueleto(w04)
    _, sk_06b = _esqueleto(w06)
    novo_sk = esqueleto.copiar_juntas(sk_k, sk_04b, JUNTAS_SAIA)
    w.trocar_dados(i_sk, novo_sk)
    for k in range(2):
        i_d = [i for i, (e, b) in enumerate(w.blocos) if 'SCR_cloth' in e['name']][k]
        i_o = [i for i, (e, b) in enumerate(w04.blocos) if 'SCR_cloth' in e['name']][k]
        scr = w04.dados(i_o)
        if 'fisica_braco' in etapas and k == 0:
            scr = _cadeia_braco_scr(scr, esqueleto.ler(sk_k))
        w.trocar_dados(i_d, scr)
    log('  esqueleto: juntas %d..%d e SCR_cloth do Fantasma' % (JUNTAS_SAIA[0], JUNTAS_SAIA[-1]))

    # 3) malha
    i_mg = w.idx(MG_K, 0x520001)
    mg = w.dados(i_mg)
    dados_mg_original = mg
    sk = esqueleto.ler(novo_sk)
    # tiras do braço ficam por cima da pele E do colete do Dominus (teste 32): obstáculos = pele + peitoral
    peito_obs = MT.extrair(_mg(w06, 'MG_382512b6_0'), esqueleto.ler(sk_06b),
                           lambda m: m['grupo'] == 17 and m['material'] in (6, 7))
    pele = [np.array(malha.vertices(mg, m)[0]) for m in malha.ler_com_material(mg)
            if m['grupo'] == 21 and m['material'] in (10, 11)]
    obst = np.vstack(pele + [c['pos'] for c in peito_obs])
    fisica = 'fisica_braco' in etapas
    mg = construir.so_ombreiras(mg, esqueleto.ler(sk_k), mg, obstaculos=obst,
                                sem_tira_dir=CADEIA_BRACO['tira'] if fisica else None)
    mg, n = MT.esconder(mg, lambda m: m['grupo'] == 21 and m['material'] == 15)      # pano vermelho
    log('  pano vermelho do Kratos escondido (%d triângulos)' % n)
    saia = MT.extrair(_mg(w04, 'MG_f402a4e_0'), esqueleto.ler(sk_04b), lambda m: m['material'] == 6)
    for c in saia:
        c['material'] = M_SAIA
    faixas = faixas_couro(saia, log)
    for c in faixas:
        c['material'] = M_SAIA
    pano = pano_novo(saia, faixas, log) if 'pano_novo' in etapas else []   # pano vermelho novo (frente + trás)
    saia = [c for k, c in enumerate(saia) if k not in PECAS_TRAS | PECAS_LADO] + faixas + pano
    log('  tanga: painel de trás e laterais trocados por faixas (peças %s)' % sorted(PECAS_TRAS | PECAS_LADO))
    peito = MT.extrair(_mg(w06, 'MG_382512b6_0'), esqueleto.ler(sk_06b),
                       lambda m: m['grupo'] == 17 and m['material'] in (6, 7))
    for c in peito:
        c['material'] = M_FANCY if c['material'] == 6 else M_RED
    log('  tanga do Fantasma: %d partes, %d triângulos' % (len(saia), sum(len(c['tris']) for c in saia)))
    log('  peitoral do Dominus: %d partes, %d triângulos' % (len(peito), sum(len(c['tris']) for c in peito)))
    pano = pano_vermelho(dados_mg_original, saia, esqueleto.ler(sk_k), log) if 'pano' in etapas else []
    if fisica:
        _trocar_cadeia(saia)
        tira, pts = tira_braco_fisica(esqueleto.ler(sk_k), obst, saia[0]['registro'], log)
        novo_sk = _cadeia_braco_esqueleto(novo_sk, pts)
        w.trocar_dados(i_sk, novo_sk)
        saia = saia + [tira]
    mg = MT.gravar_grupo(mg, 14, 0x1, saia + pano)
    mg = MT.gravar_grupo(mg, 18, 0x4, peito)
    # a pele do tronco atravessava o colete nas costas (teste 19): esconde a pele coberta por ele
    # (pele do tronco + faixa de pano da cintura do Kratos; as faixas dos pulsos/pés ficam longe do colete)
    # pescoço fica (o colarinho é estreito: esconder ali deixava buracos transparentes, teste 24)
    mg, n = MT.esconder_cobertos(mg, lambda m: m['grupo'] == 21 and m['material'] in (8, 11), peito, dist=0.06,
                                 y_max=1.97)
    log('  pele sob o colete do Dominus escondida (%d triângulos)' % n)
    w.trocar_dados(i_mg, mg)
    WE.atualizar_matx(w, log)
    return w.bytes()
