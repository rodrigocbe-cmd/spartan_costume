"""Pano vermelho novo da Armadura de Deus (pedido de 2026-11-22; referência referencias/god_armor/geral.jpg):
painel da FRENTE com a grega + pano de TRÁS inteiro, do cinto até o joelho. Material 8 (cloth_m, o das faixas
de pano das mãos/pés) com a textura TX5512508B: os blocos abaixo ficam na área da saia original do Kratos
(escondida), repintada por texturas_armadura.pano_textura(); a geometria é gerada por montagem.pano_novo().
Tentativa anterior (pano original rasgado, material 15 skirt_cloth_m) deixou o FPS baixo (teste 18)."""

TEX = 'TX5512508B.F9EA0D02'          # 2048 x 1024
TEX_TAM = (2048, 1024)
# blocos na textura (px): x0, y0, x1, y1 (topo do pano em y0)
BLOCO_FRENTE = (420, 30, 820, 590)
BLOCO_TRAS = (860, 30, 1440, 590)
# amostra de pano vermelho liso do próprio Kratos (faixa das canelas) para a trama
AMOSTRA_PANO = (270, 630, 850, 930)

# geometria = a do pano ORIGINAL do Kratos (material 15 do R_HERO00, medido em 2026-11-22): ângulos em graus
# (0 = frente, + = lado direito do Kratos, contínuo até 270° = quadril esquerdo pelas costas), alturas em m.
# Começa na frente um pouco à esquerda do centro com a borda inclinada para a direita ao descer (-55° no cinto
# -> -22° na barra); a barra é mais baixa na frente e vai subindo ao dar a volta pela direita e pelas costas até
# o quadril esquerdo (abertura de ~-100° a -55°, como no original).
Y_TOPO = 1.45
BARRA = [(-60, 1.10), (-40, 0.92), (-22, 0.85), (0, 0.85), (15, 0.90), (35, 0.97), (60, 1.00), (90, 0.97),
         (120, 0.99), (150, 1.02), (180, 1.04), (210, 1.05), (225, 1.07), (240, 1.13), (262, 1.28)]
FRENTE = dict(ang_topo=(-55.0, 35.0), ang_base=(-22.0, 35.0), folga=[(-60, 0.015), (20, 0.015), (35, 0.008)], colunas=10, linhas=9)
TRAS = dict(ang_topo=(35.0, 262.0), ang_base=(35.0, 255.0), folga=[(35, 0.010), (60, 0.008)], colunas=20, linhas=9)
# folga = [(ângulo, distância acima da superfície de referência)]: a frente passa por cima do avental/faixas,
# o resto por cima das faixas de couro (pedido do usuário, 2026-11-22)
MATERIAL = 8                          # cloth_m
