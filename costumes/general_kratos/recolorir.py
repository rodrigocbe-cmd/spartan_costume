"""General Kratos (e General Kratos (armadura)) – pele no tom do traje DEIMOS do jogo.

O "Deimos" do menu de trajes é o R_HERO07 (barbudo, rachaduras de lava; prints do usuário em
referencias/general_kratos/deimos_*.png). A pele dele está na própria textura de COR:
  Deimos  TX856D597B (corpo) pele mediana (109, 85, 71), TX3519F99F (rosto) (134, 101, 87), saturação ~0,35
  Kratos  TX27CF5CC1 (corpo) (156, 142, 132),            TX4A104642 (cabeça) (181, 170, 162), saturação ~0,13
e o 5º slot do material (versão "pálida" da pele) é arroxeado-quente no Deimos (TX887F374F, mediana
(107, 85, 109)) e azulado no Kratos (TX60366B5B (106, 105, 137), TXBEB53958 (132, 134, 156)).

Então: ganho por canal que leva a pele do Kratos à pele do Deimos (preserva todo o detalhe); tatuagem,
olhos, dentes, boca interna, barba e pano ficam idênticos. O 5º slot recebe o ganho que leva o azulado do
Kratos ao arroxeado do Deimos. (Testes 2/3 — trocar parâmetros do material pelos do Deimos de tatuagem azul
[R_HERO03] — não mudaram nada no jogo; descartados.)

General (armadura) = Dominus (R_HERO06): mesmas UVs e texturas de pele quase idênticas às do Kratos
(TX08FFABDA corpo, TX09BFCDF6 cabeça); o 5º slot dele já é branco (fica).

uso: python -I costumes/general_kratos/recolorir.py
"""
import importlib.util
import os
import shutil

import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
_spec = importlib.util.spec_from_file_location('recolorir_odisseia', os.path.join(RAIZ, 'costumes', 'dark_odyssey', 'recolorir.py'))
B = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B)

PELE_DEIMOS = {'corpo': np.array([109, 85, 71]) / 255.0, 'cabeca': np.array([134, 101, 87]) / 255.0}
QUINTO_DEIMOS = np.array([107, 85, 109]) / 255.0

ROSTO_EX = [(0.59, 0.57, 0.93, 0.73), (0.89, 0.59, 0.98, 0.64)]     # boca interna, tira vermelha
ROSTO_PANO = [(0.0, 0.56, 0.30, 1.0)]
CORPO_EX = [(0.64, 0.0, 1.0, 0.18)]                                 # dentes e gengiva
CICATRIZ = [(0.46, 0.575, 0.555, 0.67), (0.555, 0.605, 0.58, 0.635)]


def olho_ex(shape):
    return (B.mascara_olho_raio(shape, 0.155) > 0.5).astype(np.float32)


TRAJES = {
    # costume: (WAD, cor corpo, cor cabeça, [5º slot corpo, 5º slot cabeça] ou [])
    'general_kratos': ('R_HERO00', 'TX27CF5CC1.AD3FCC3E', 'TX4A104642.F3349159',
                       ['TX60366B5B.8595A315', 'TXBEB53958.0FB769D9']),
    'general_kratos_armadura': ('R_HERO06', 'TX08FFABDA.D13B2792', 'TX09BFCDF6.58027C50', []),
}


def manter_mascara(rgb, excluir, pano=(), sem_tatuagem=(), ex_mascara=None):
    """O que NÃO é pele (0..1): tatuagem, pano vermelho, e o que não parece pele nas caixas de exclusão."""
    h, s, v = B.hsv(rgb)
    L = B.lum(rgb)
    ex = B.caixa(rgb.shape, excluir)
    if ex_mascara is not None:
        ex = np.maximum(ex, ex_mascara(rgb.shape))
    pn = B.caixa(rgb.shape, pano)
    st = B.caixa(rgb.shape, sem_tatuagem)
    tat = B.mascara_tatuagem(rgb, np.maximum(np.maximum(ex, pn), st), 0.0015)
    pano_m = pn * B.suave(s, 0.25, 0.40)
    pele_like = (s < 0.16) & (L > 0.40) & (L < 0.93)
    return np.clip(tat + pano_m + ex * (~pele_like), 0, 1), tat, ex, pn


def pele_deimos(wad, nome, alvo, excluir, pano=(), sem_tatuagem=(), ex_mascara=None):
    rgb, a = B.carregar(nome, wad)
    manter, tat, ex, pn = manter_mascara(rgb, excluir, pano, sem_tatuagem, ex_mascara)
    h, s, v = B.hsv(rgb)
    L = B.lum(rgb)
    pele = (s < 0.45) & (L > 0.3) & (L < 0.85) & (manter < 0.1)
    ref = np.median(rgb[pele], 0)
    g = alvo / ref
    print('  %s %s pele %s -> %s (ganho %s)' % (wad, nome[:10], np.round(ref * 255), np.round(alvo * 255), np.round(g, 3)))
    out = np.clip(rgb * g, 0, 1)
    m = manter[..., None]
    return out * (1 - m) + rgb * m, a, manter


def main():
    for cid, (wad, corpo, cabeca, quintos) in TRAJES.items():
        B.SAIDA = os.path.join(RAIZ, 'costumes', cid, 'texturas')
        d = os.path.join(B.SAIDA, wad)
        if os.path.isdir(d):
            shutil.rmtree(d)
        print(cid)
        rosto, a, m_rosto = pele_deimos(wad, cabeca, PELE_DEIMOS['cabeca'], ROSTO_EX, ROSTO_PANO)
        B.salvar(cabeca, rosto, a, wad)
        corpo_rgb, a2, m_corpo = pele_deimos(wad, corpo, PELE_DEIMOS['corpo'], CORPO_EX,
                                             sem_tatuagem=CICATRIZ, ex_mascara=olho_ex)
        B.salvar(corpo, corpo_rgb, a2, wad)
        # 5º slot (versão "pálida"): azulado do Kratos -> arroxeado-quente do Deimos, fora do "manter"
        for q, m_alta in zip(quintos, (m_corpo, m_rosto)):
            qrgb, qal = B.carregar(q, wad)
            H, W = qrgb.shape[:2]
            m = np.asarray(Image.fromarray((m_alta * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
            ref = np.median(qrgb[m < 0.1], 0)
            g = QUINTO_DEIMOS / ref          # tom E brilho do Deimos (mais claro deixava a pele pálida)
            print('  %s %s 5º slot %s ganho %s' % (wad, q[:10], np.round(ref * 255), np.round(g, 3)))
            B.salvar(q, np.clip(qrgb * g, 0, 1) * (1 - m[..., None]) + qrgb * m[..., None], qal, wad)
        prev = os.path.join(RAIZ, 'costumes', cid, 'preview')
        if os.path.isdir(prev):
            shutil.rmtree(prev)
        os.makedirs(prev)
        for f in sorted(os.listdir(d)):
            o = Image.open(os.path.join(B.ORIG, wad, 'png', f)).convert('RGB')
            nv = Image.open(os.path.join(d, f)).convert('RGB')
            sc = 512 / max(o.size)
            o, nv = o.resize((int(o.width * sc), int(o.height * sc))), nv.resize((int(o.width * sc), int(o.height * sc)))
            p = Image.new('RGB', (o.width * 2 + 8, o.height), (255, 0, 255))
            p.paste(o, (0, 0)); p.paste(nv, (o.width + 8, 0))
            p.save(os.path.join(prev, f))


if __name__ == '__main__':
    main()
