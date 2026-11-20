"""Odisseia Sombria (Dark Odyssey) – recoloração das texturas do Kratos do GoW III.

Pele cinza-carvão e tatuagem dourada (inspiradas no GoW Ragnarok), roupas/armadura em
preto e dourado (inspiradas no GoW II). Só altera cores; malha e mapas de normal ficam iguais.

uso: python -I costumes/dark_odyssey/recolorir.py
Lê:   original/<WAD>/png/*.png   (gerado por ferramentas/extrair_texturas.py)
Gera: costumes/dark_odyssey/texturas/<WAD>/*.png  e  previews em costumes/dark_odyssey/preview/
(WADs: R_HERO00 = Kratos; R_W_EXPLOSIVE0 = Lâminas do Exílio, aplicadas também em 1..4 pelo build)
"""
import os
import numpy as np
from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ORIG = os.path.join(RAIZ, 'original')
SAIDA = os.path.join(os.path.dirname(__file__), 'texturas')
PREV = os.path.join(os.path.dirname(__file__), 'preview')

# ---- Paleta (amostrada de referencias/dark_odyssey/ragnarok_dark_odyssey_rosto_laminas.webp)
PELE = np.array([44, 42, 36]) / 255.0       # cinza-carvão quente (ref: #282823 .. #28261f)
TATUAGEM = np.array([196, 138, 58]) / 255.0 # dourado (ref: tatuagem #885b2c, lâminas #a26517)
OURO = np.array([186, 128, 46]) / 255.0     # metal dourado âmbar (ref: lâminas/medalhão Ragnarok)
OLHO = np.array([238, 238, 232]) / 255.0    # olhos brancos (Ragnarok)
PRETO = np.array([30, 29, 27]) / 255.0      # couro/tecido preto

# Texturas de cor (diffuse) – identificadas pela folha de contato
TEX_ROSTO = 'TX4A104642.F3349159'   # cabeça, rosto, braço, pés (tatuagem)
TEX_CORPO = 'TX27CF5CC1.AD3FCC3E'   # tronco, braços, olho, dentes (tatuagem)
TEX_SAIA = ['TX5512508B.F9EA0D02', 'TX4D95EEC1.E6645096']   # saia vermelha
TEX_COURO = ['TXE3FF895B.EF07B012']                          # botas / proteções de couro
TEX_METAL = ['TXE90D274D.FDB1BC40']                          # ombreira / braceletes (bronze)
TEX_CINTO = ['TX3DEC657A.5633D663']                          # cinto, correntes, faixas
TEX_NORMAL_CORPO = 'TX27586F46.42C0C6FA'   # normal map do corpo (DXT5: x no alfa, y no verde)
NORMAL_PLANA = np.array([255, 126, 0, 127]) / 255.0   # valor "plano" medido na pele em volta do olho
TEX_AZUL_CORPO = 'TX60366B5B.8595A315'     # versão azulada do corpo (chest_m, outereye_m)
TEX_AZUL_ROSTO = 'TXBEB53958.0FB769D9'     # versão azulada da cabeça (head_m, eyegasket_m)
WAD_EXILIO = 'R_W_EXPLOSIVE5'              # Lâminas do Exílio (a maior parte do jogo e o menu)
TEX_EXILIO = 'TXA4FBD109.99B55E5A'         # cor: lâmina em gancho + cabo de dragão
TEX_EXILIO_BRILHO = 'TX8EE75C90.9E8E5EDC'  # brilho (runas vermelhas) -> laranja-dourado
WAD_LAMINAS = 'R_W_EXPLOSIVE0'             # Lâmina de Atena (início do jogo; EXPLOSIVE0..4)
TEX_LAMINA = 'TX888F0896.11CF076F'   # Lâminas do Exílio (cor): lâmina + cabeça de dragão + cabo
# Polígono (UV) do cabo: cabeça de dragão, guarda, empunhadura e pomo. O resto é lâmina.
CABO = [(0.34, 0.21), (0.39, 0.17), (0.40, 0.06), (0.42, 0.0), (0.50, 0.0), (0.56, 0.08),
        (0.58, 0.20), (0.62, 0.30), (0.62, 0.45), (0.66, 0.52), (0.76, 0.56), (0.80, 0.62),
        (0.87, 0.72), (0.80, 0.76), (0.74, 0.88), (0.70, 0.84), (0.66, 0.79), (0.56, 0.76),
        (0.50, 0.74), (0.44, 0.77), (0.39, 0.75), (0.39, 0.62), (0.42, 0.52), (0.40, 0.46),
        (0.34, 0.43), (0.33, 0.31)]


def mascara_olho(shape):
    """Disco do globo ocular na UV do corpo: centro (0.82, 0.30), raio 0.145 da largura."""
    H, W = shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - 0.82 * W, yy - 0.30 * H)
    return 1 - suave(r, 0.135 * W, 0.145 * W)


def carregar(nome, wad='R_HERO00'):
    im = Image.open(os.path.join(ORIG, wad, 'png', nome + '.png')).convert('RGBA')
    a = np.asarray(im).astype(np.float32) / 255.0
    return a[..., :3], a[..., 3:]


def salvar(nome, rgb, alpha, wad='R_HERO00'):
    d = os.path.join(SAIDA, wad)
    os.makedirs(d, exist_ok=True)
    out = np.concatenate([np.clip(rgb, 0, 1), alpha], -1)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(d, nome + '.png'))


def hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    d = np.maximum(mx - mn, 1e-4)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    return h, sat, mx


def lum(rgb):
    return rgb @ np.array([0.299, 0.587, 0.114])


def caixa(shape, boxes):
    """Máscara 1.0 dentro das caixas (coordenadas UV normalizadas x0,y0,x1,y1)."""
    h, w = shape[:2]
    m = np.zeros((h, w), np.float32)
    for x0, y0, x1, y1 in boxes:
        m[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
    return m


def pecas(rgb, boxes, limiar=0.03, erosao=6, fg=None):
    """Máscara das ilhas da UV (peças inteiras) cujo CENTRO cai dentro das caixas.
    Peças que se encostam são separadas por erosão e depois re-expandidas
    (cada pixel volta para a peça mais próxima). Evita cortar uma peça ao meio."""
    from scipy import ndimage
    if fg is None:
        fg = lum(rgb) > limiar
    nucleo = ndimage.binary_erosion(fg, iterations=erosao)
    lab, n = ndimage.label(nucleo)
    _, (iy, ix) = ndimage.distance_transform_edt(lab == 0, return_indices=True)
    lab = np.where(fg, lab[iy, ix], 0)
    H, W = fg.shape
    manter = np.zeros(n + 1, bool)
    for k, c in enumerate(ndimage.center_of_mass(fg, lab, range(1, n + 1)), 1):
        cy, cx = c[0] / H, c[1] / W
        manter[k] = any(x0 <= cx <= x1 and y0 <= cy <= y1 for x0, y0, x1, y1 in boxes)
    m = ndimage.binary_dilation(manter[lab], iterations=2)   # cobre a borda da peça
    return ndimage.gaussian_filter(m.astype(np.float32), 1.0)


def suave(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def tingir(L, cor, ref, contraste=1.0):
    """Mantém o detalhe (luminância relativa) e aplica a cor-alvo."""
    k = (L / max(ref, 1e-3)) ** contraste
    return cor * k[..., None]


def mascara_tatuagem(rgb, ex, area_min_frac):
    """Tatuagem = regiões GRANDES de vermelho saturado (descarta lábios, orelhas, mamilos...)."""
    from scipy import ndimage
    h, s, v = hsv(rgb)
    L = lum(rgb)
    vermelho = ((h < 0.05) | (h > 0.95)) & (s > 0.28) & (L < 0.55)
    vermelho &= ex < 0.5
    # fecha buracos de sujeira dentro da tatuagem
    sol = ndimage.binary_closing(vermelho, iterations=4)
    sol = ndimage.binary_fill_holes(sol)
    lab, n = ndimage.label(sol)
    idx = range(1, n + 1)
    areas = ndimage.sum(sol, lab, idx)
    sat_media = ndimage.mean(s, lab, idx)
    min_area = area_min_frac * sol.size
    manter = np.zeros(n + 1, bool)
    # tatuagem real: região grande e bem saturada (lábios/orelhas/mamilos/cicatrizes têm s<=0.39)
    manter[1:] = (areas >= min_area) & (sat_media >= 0.41)
    sol = manter[lab]
    sol = ndimage.binary_opening(sol, iterations=2)
    m = ndimage.gaussian_filter(sol.astype(np.float32), 1.5)   # borda suave
    return np.clip(m, 0, 1)


def pele_e_tatuagem(nome, excluir, pano=(), sem_tatuagem=()):
    """excluir: caixas cujo conteúdo não-pele é preservado (olho, dentes, boca interna).
    pano: caixas onde vermelho saturado é pano (vira preto, não tatuagem)."""
    rgb, a = carregar(nome)
    h, s, v = hsv(rgb)
    L = lum(rgb)
    ex = caixa(rgb.shape, excluir)
    pn = caixa(rgb.shape, pano)
    st = caixa(rgb.shape, sem_tatuagem)   # ex.: cicatriz que encosta na tatuagem
    tat = mascara_tatuagem(rgb, np.maximum(np.maximum(ex, pn), st), 0.0015)
    pele_ref = np.median(L[(s < 0.12) & (L > 0.5)])
    tat_ref = np.median(L[tat > 0.9])
    nova_pele = tingir(L, PELE, pele_ref, 1.3)
    # tatuagem: detalhe mais suave (desgaste leve, como no Ragnarok)
    Lt = 0.55 * L + 0.45 * tat_ref
    nova_tat = tingir(Lt, TATUAGEM, tat_ref, 1.0)
    out = nova_pele * (1 - tat[..., None]) + nova_tat * tat[..., None]
    # pano vermelho -> preto
    pano_m = pn * suave(s, 0.25, 0.40)
    out = out * (1 - pano_m[..., None]) + tingir(L, PRETO * 1.3, 0.3)[...] * pano_m[..., None]
    # caixas de exclusão: preserva tudo que não parece pele (dentes, olho, boca interna)
    pele_like = (s < 0.16) & (L > 0.40) & (L < 0.93)
    keep = ex * (~pele_like)
    out = out * (1 - keep[..., None]) + rgb * keep[..., None]
    return out, a, tat


def main():
    # Rosto: pano vermelho (canto inferior esquerdo), lábios, olho/boca escuros
    rosto_ex = [(0.59, 0.57, 0.93, 0.73),   # boca interna (marrom)
                (0.89, 0.59, 0.98, 0.64)]   # tira vermelha pequena
    rosto_pano = [(0.0, 0.56, 0.30, 1.0)]   # pano vermelho
    out, a, tat = pele_e_tatuagem(TEX_ROSTO, rosto_ex, rosto_pano)
    salvar(TEX_ROSTO, out, a)
    corpo_ex = [(0.64, 0.0, 1.0, 0.18),     # dentes e gengiva
                (0.66, 0.22, 1.0, 0.40)]    # globo ocular
    corpo_cicatriz = [(0.46, 0.575, 0.555, 0.67),    # cicatriz da barriga
                      (0.555, 0.605, 0.58, 0.635)]  # ponte entre cicatriz e tatuagem
    out2, a2, _ = pele_e_tatuagem(TEX_CORPO, corpo_ex, sem_tatuagem=corpo_cicatriz)
    # Olhos todo brancos, sem íris/pupila (Ragnarok; no GoW II o olho também é branco).
    # O globo ocular é um disco na UV (centro 0.82, 0.30). Ele é desenhado em 3 texturas:
    # cor do corpo (innereye_m), cor azulada (outereye_m) e mapa de normal (relevo da íris).
    olho = mascara_olho(out2.shape)
    out2 = out2 * (1 - olho[..., None]) + OLHO * olho[..., None]
    salvar(TEX_CORPO, out2, a2)
    nrgb, nal = carregar(TEX_NORMAL_CORPO)
    o = mascara_olho(nrgb.shape)[..., None]
    nrgb = nrgb * (1 - o) + NORMAL_PLANA[:3] * o           # sem relevo de íris
    nal = nal * (1 - o) + NORMAL_PLANA[3] * o
    salvar(TEX_NORMAL_CORPO, nrgb, nal)

    # Texturas azuladas (pele "pálida", mesma UV em meia resolução): acompanham a
    # recoloração mantendo a relação de brilho com as originais.
    for azul, principal, nova in ((TEX_AZUL_CORPO, TEX_CORPO, out2), (TEX_AZUL_ROSTO, TEX_ROSTO, out)):
        brgb, bal = carregar(azul)
        H, W = brgb.shape[:2]
        orig_p = np.asarray(Image.open(os.path.join(ORIG, 'R_HERO00', 'png', principal + '.png'))
                            .convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
        nova_p = np.asarray(Image.fromarray((np.clip(nova, 0, 1) * 255).astype(np.uint8))
                            .resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
        razao = np.clip(lum(brgb) / np.maximum(lum(orig_p), 0.02), 0.5, 2.0)
        res = nova_p * razao[..., None]
        if azul == TEX_AZUL_CORPO:
            o = mascara_olho(res.shape)[..., None]
            res = res * (1 - o) + OLHO * o
        salvar(azul, res, bal)

    # Saia vermelha -> preta; detalhes claros (grega) -> dourado
    for n in TEX_SAIA:
        rgb, al = carregar(n)
        h, s, v = hsv(rgb)
        L = lum(rgb)
        claro = suave(L, 0.35, 0.55) * (1 - suave(s, 0.5, 0.8))
        base = tingir(L, PRETO, np.median(L), 1.0)
        ouro = tingir(L, OURO, 0.6, 0.8)
        salvar(n, base * (1 - claro[..., None]) + ouro * claro[..., None], al)

    # Botas de Hermes / grevas: armadura das pernas dourada (pedido do usuário),
    # só a tira de couro de cima fica preta
    for n in TEX_COURO:
        rgb, al = carregar(n)
        L = lum(rgb)
        tira = pecas(rgb, [(0.0, 0.0, 0.65, 0.18)], erosao=10)
        ref = np.median(L[L > 0.05])
        out = tingir(L, OURO, ref, 1.0) * (1 - tira[..., None])
        out += tingir(L, PRETO * 1.4, ref, 1.0) * tira[..., None]
        salvar(n, out, al)

    # Metal bronze -> dourado
    for n in TEX_METAL:
        rgb, al = carregar(n)
        L = lum(rgb)
        salvar(n, tingir(L, OURO, np.median(L[L > 0.2]), 1.0), al)

    # Cinto/braçadeiras/correntes (mapa do GoW II): tudo dourado. Nas braçadeiras dos
    # antebraços (peça das correntes), elos claros sobre fundo dourado mais escuro.
    for n in TEX_CINTO:
        rgb, al = carregar(n)
        L = lum(rgb)
        correntes = pecas(rgb, [(0.33, 0.0, 1.0, 0.52)])
        resto = np.clip(1 - correntes, 0, 1)
        ref = np.median(L[L > 0.1])
        h, s, v = hsv(rgb)
        elos = (1 - suave(s, 0.12, 0.25)) * correntes          # elos: cinza (pouca saturação)
        fundo = tingir(L, OURO * 0.6, ref, 1.3)                # fundo da braçadeira: dourado escuro
        elo = tingir(L, OURO * 1.15, ref, 1.0)                 # elos: dourado claro
        out = (fundo * (1 - elos[..., None]) + elo * elos[..., None]) * correntes[..., None]
        out += tingir(L, OURO, ref, 1.2) * resto[..., None]
        salvar(n, out, al)

    # Lâminas do Exílio (Ragnarok): lâmina dourada (teia mais escura), cabo preto;
    # corrente da empunhadura e olho do dragão viram detalhes dourados
    from PIL import ImageDraw
    from scipy import ndimage
    rgb, al = carregar(TEX_LAMINA, WAD_LAMINAS)
    H, W = rgb.shape[:2]
    h, s, v = hsv(rgb)
    L = lum(rgb)
    mimg = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mimg).polygon([(x * W, y * H) for x, y in CABO], fill=255)
    cabo = ndimage.gaussian_filter(np.asarray(mimg).astype(np.float32) / 255, 2.0)
    detalhe = cabo * suave(s, 0.35, 0.55) * ((h > 0.04) & (h < 0.15))   # corrente/olho laranja
    ref_cabo = np.median(L[cabo > 0.5])
    Lb = 0.3 * L + 0.7 * 0.55                         # lâmina toda dourada (Ragnarok): pouco contraste
    lamina = tingir(Lb, OURO * 1.1, 0.55, 1.0)
    cabo_preto = tingir(L, PRETO * 1.3, ref_cabo, 1.2)
    out = lamina * (1 - cabo[..., None]) + cabo_preto * cabo[..., None]
    out = out * (1 - detalhe[..., None]) + tingir(L, OURO, 0.5, 1.0) * detalhe[..., None]
    salvar(TEX_LAMINA, out, al, WAD_LAMINAS)

    # Lâminas do Exílio (Ragnarok): lâmina (fio de osso, centro e face com runas) dourada,
    # cabo de dragão e pomo pretos com a corrente dourada; runas em brilho laranja-dourado.
    rgb, al = carregar(TEX_EXILIO, WAD_EXILIO)
    H, W = rgb.shape[:2]
    fundo_cor = np.median(rgb[int(0.92 * H):, :int(0.03 * W)].reshape(-1, 3), 0)  # laranja liso
    fg = np.abs(rgb - fundo_cor).sum(-1) > 0.18
    cabo = pecas(rgb, [(0.45, 0.30, 0.86, 1.0), (0.26, 0.74, 0.40, 1.0)], erosao=4, fg=fg)
    pedra = caixa(rgb.shape, [(0.86, 0.0, 1.0, 0.58)])            # bloco de pedra: não mexe
    h, s, v = hsv(rgb)
    L = lum(rgb)
    Lb = 0.3 * L + 0.7 * 0.55                                     # lâmina toda dourada (Ragnarok)
    lamina = tingir(Lb, OURO * 1.1, 0.55, 1.0)
    ref_cabo = np.median(L[cabo > 0.5])
    cabo_preto = tingir(L, PRETO * 1.3, ref_cabo, 1.2)
    out = lamina * (1 - cabo[..., None]) + cabo_preto * cabo[..., None]
    corrente = cabo * suave(L, ref_cabo * 1.05, ref_cabo * 1.5)    # elos mais claros no cabo
    out = out * (1 - corrente[..., None]) + tingir(L, OURO, 0.45, 1.0) * corrente[..., None]
    out = out * (1 - pedra[..., None]) + rgb * pedra[..., None]
    salvar(TEX_EXILIO, out, al, WAD_EXILIO)
    # brilho: vermelho -> laranja-dourado (mesma intensidade)
    grgb, gal = carregar(TEX_EXILIO_BRILHO, WAD_EXILIO)
    h, s, v = hsv(grgb)
    verm = ((h < 0.06) | (h > 0.94)) * suave(s, 0.3, 0.6)
    fogo = np.array([1.0, 0.62, 0.15]) * v[..., None]
    salvar(TEX_EXILIO_BRILHO, grgb * (1 - verm[..., None]) + fogo * verm[..., None], gal, WAD_EXILIO)

    # Previews lado a lado (original | novo)
    os.makedirs(PREV, exist_ok=True)
    arqs = [(w, f) for w in sorted(os.listdir(SAIDA)) for f in sorted(os.listdir(os.path.join(SAIDA, w)))]
    for w_, f in arqs:
        o = Image.open(os.path.join(ORIG, w_, 'png', f)).convert('RGB')
        nv = Image.open(os.path.join(SAIDA, w_, f)).convert('RGB')
        w, h = o.size
        sc = 512 / max(w, h)
        o, nv = o.resize((int(w * sc), int(h * sc))), nv.resize((int(w * sc), int(h * sc)))
        p = Image.new('RGB', (o.width * 2 + 8, o.height), (255, 0, 255))
        p.paste(o, (0, 0)); p.paste(nv, (o.width + 8, 0))
        p.save(os.path.join(PREV, w_ + '_' + f))
    print('texturas geradas em', SAIDA)


if __name__ == '__main__':
    main()
