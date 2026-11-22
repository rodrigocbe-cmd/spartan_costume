# GoW III Costumes

Visuais (costumes) para **God of War III Remastered**. Foco principal: o port de PC
**SpartanPort**; tudo deve continuar instalável também no **PS4** (mesmo formato `PS4_LE`).

## Instruções do usuário (sempre seguir)

- Visuais devem ser **adicionados/removíveis** por um instalador; o jogo original nunca é alterado.
- Preferência: **não substituir visuais existentes** → cada visual entra num **slot novo** do menu
  de trajes (índices 9, 10, … atribuídos em sequência pelo instalador).
- **Idioma:** se o jogo/sistema estiver em português, os nomes dos visuais aparecem em
  português; em qualquer outro idioma, em inglês. **Outras traduções serão adicionadas
  no futuro** — manter todos os textos em tabelas por idioma (`nomes`/`descricao` em
  `costume.json`, classe `Txt` em `instalador/Instalador.cs`), nunca fixos no código.
  Textos DENTRO do jogo já estão nos 16 idiomas do jogo (`textos_jogo` por código do
  `R_LANG_<código>`: BR PT EN UK ES LA FR IT DE NL PL TR RU JA KO ZH; falta → vizinho
  [PT↔BR, UK→EN, LA↔ES] → EN). Frases seguem as dos trajes oficiais. A fonte do jogo só tem os
  caracteres usados no jogo: `trajes._linhas` recusa texto com caractere ausente no arquivo
  original (ex.: "ё" no RU, "갓" no KO) e cai para o próximo idioma.
  Descrição = 4 linhas (como Dominus/Deimos), cada uma ≤ a maior linha oficial do idioma
  (`_largura_max`); linhas maiores são quebradas (`_quebrar`) — melhor encurtar a frase.
- Pode reorganizar pastas e arquivos conforme o projeto precisar.
- Responder ao usuário em português.

## Visuais

### Odisseia Sombria / Dark Odyssey (lançada no pacote v1.0.0)
- Base: Kratos padrão do GoW III (`R_HERO00.WAD`), **só recoloração** — malha, esqueleto,
  normal maps e animações intactos.
- **Regra de cores (pedido do usuário):** usar o modelo do GoW II
  (`referencias/dark_odyssey/gow2_modelo/`, texturas + OBJ) para saber ONDE vai cada cor,
  e as cores atuais do **GoW Ragnarok** (`referencias/dark_odyssey/ragnarok_*.webp`).
- Pele cinza-carvão (~`#2c2a24`), tatuagem dourada (~`#c48a3a`), **olhos brancos**.
- Roupas/armadura: saia preta com grega dourada; ombreira, braceletes, cinto, grevas/botas
  e asas de Hermes **dourados** (âmbar ~`#ba802e`); braçadeiras dos antebraços douradas
  (elos claros sobre fundo dourado escuro, como no modelo do GoW II).
- **Olhos todo brancos** (sem íris/pupila; brilho opcional, não feito). O olho usa 4 texturas:
  `innereye_m` → cor `TX27CF5CC1` + mapa claro `TX3F8EBE10` (tinha a pupila preta);
  `outereye_m` → `TX60366B5B` (azulada) + normal `TX27586F46` (relevo aplainado). Disco do olho na UV: centro (0.82, 0.30).
- Texturas azuladas `TX60366B5B` (corpo) e `TXBEB53958` (cabeça) = versão "pálida" da pele
  usada também por `chest_m`/`head_m`; são recoloridas mantendo a razão de brilho.
- **Lâminas do Exílio** (`R_W_EXPLOSIVE5`, a maior parte do jogo e o menu): cor `TXA4FBD109`
  (lâmina em gancho + cabo de dragão), brilho `TX8EE75C90` (runas vermelhas → laranja-dourado),
  especular `TX7F88879E`. Lâmina toda dourada (uniforme, como no Ragnarok), cabo preto,
  corrente dourada. A troca Atena → Exílio no início do jogo usa esses mesmos WADs
  (única outra cópia das texturas: `R_KRATOSFEAR10`, inimigo — não alterado).
- **Lâmina de Atena** (`R_W_EXPLOSIVE0..4`, início do jogo): `TX888F0896` (cabeça de dragão),
  toda dourada com cabo preto.
- **Rastros dos golpes** (`TXR_swordtrail`, 128x64 DXT5 com alfa): um diferente em cada
  `R_W_EXPLOSIVE0..5` (nível) → recoloridos para dourado (saturado → âmbar, claro → dourado pálido).
  Por isso cada EXPLOSIVEk tem sua pasta em `texturas/`. Texturas `TXR_*` (sem .dds) agora são
  suportadas pelas ferramentas.
- **Fogo e faíscas das lâminas**: texturas de chamas (`TX22A00174`, `TXD8C83914`, `TX9E182643`,
  `TXA94E26B8`, brilho `TXBD708C9C`) recoloridas + **curvas de cor das partículas** (`PTS_*`, blocos de
  chaves (t,R,G,B,A) via tabela em +0x120) trocadas de vermelho/laranja para dourado por
  `ferramentas/particulas.py` (chamado em `costumes/dark_odyssey/pos_wad.py`).
  **As lâminas douradas fazem parte do conjunto da Odisseia e aparecem SÓ com ela (pedido do
  usuário; "depois vemos se aplicamos em outros").** Mecanismo (v1.1.0): os WADs dourados são
  instalados como `R_W_GOLDBLADE0..5.WAD` (mesmo nome interno `WAD_R_W_Explosive`; os
  `R_W_EXPLOSIVE` originais ficam intactos) + **patch de código** (`ferramentas/patch_laminas.py` →
  `costumes/dark_odyssey/patches/{spartanport,goldhen}.xml`, `{INDICE}` = slot em hex preenchido
  pelo instalador). O patch desvia o início da função que carrega WADs por nome (eboot va
  `0x1f4730`, +0x400000) para um trecho gravado em 5 preenchimentos de NOP (0x1073c1, 0x107411,
  0x107461, 0x1074b1, 0x108c51): se `[0x3c2b70]` (nº do R_HeroNN carregado) == slot e
  `nome[4..7]=="Expl"`, troca por "GoldBlad" ("R_W_Explosive5" → "R_W_GoldBlade5"). Nomes de arma
  vêm do R_PERM ("R_W_Explosive" + nível via `sprintf("%s%d")` em 0x102d68).
  SpartanPort: `mods/<mod>/patches/<id>.xml` (Pattern + Target/{rel:}; como o "Skip Intro" dele),
  vale com o mod ativado. PS4: `GoldHEN/<id>.xml` com endereços fixos (v01.02).
  (Itens sem slot continuam suportados: `"slot": false` no costume.json.)
- Especular do fleece (`TX2E5E7D75`) × 0,6: ombreira dourada estava estourada no jogo.
- Velo (TXE90D274D): as manchas de SANGUE ficam vermelhas (cor original onde o matiz é vermelho e a saturação
  > ~0,2); antes viravam manchas pretas no dourado (relato do usuário, 2026-11-22).
- Script: `costumes/dark_odyssey/recolorir.py` (máscaras, caixas/polígonos UV e paleta).
- Pendente: texturas azuladas `TX60366B5B`/`TXBEB53958` (função desconhecida, não alteradas),
  preview com print real do jogo, conferir lâminas no jogo.

### General Kratos (slot 10, no pacote depois da Odisseia; pedido de 2026-11-21)
- Kratos padrão (`R_HERO00`) com o **tom de pele do Deimos**; tatuagem vermelha, cicatrizes, lábios,
  olhos, dentes, roupas e lâminas IDÊNTICOS ao padrão.
- **O "Deimos" do menu = `R_HERO07`** (barbudo, rachaduras de lava; prints do usuário em
  `referencias/general_kratos/deimos_*.png`). A pele dele está na TEXTURA DE COR: TX856D597B (corpo)
  mediana (109,85,71), TX3519F99F (rosto) (134,101,87), saturação ~0,35 × Kratos (156,142,132)/(181,170,162)
  ~0,13; 5º slot do material (versão "pálida") TX887F374F arroxeado-quente (107,85,109) × Kratos azulado.
  `recolorir.py`: ganho por canal pele Kratos → Deimos (tatuagem/olho/dentes/boca/barba/pano mantidos) e
  5º slot → valor do Deimos. Histórico: teste 1 (bronzeado da arte do GoW II) "sutil, manchas cinzas";
  testes 2/3 (parâmetros do MAT copiados do `R_HERO03` [tatuagem azul, que NÃO é o Deimos]) sem efeito.
- **Teste 4 (tom do Deimos `R_HERO07`): aprovado ("cor interessante").** Pendente (pedido do usuário):
  puxar a pele um pouco mais para o **vermelho**, para parecer pele real (aumentar o ganho do canal R /
  alvo um pouco mais avermelhado em `PELE_DEIMOS`).
- **Mapeamento de arquivos = índice do texto** (*2000N* → `R_HERO0N`): 00 Kratos, 01 Kratos do Medo,
  02 Apolo, 03 Armadura de Morfeu (tatuagem/armadura azuis), 04 Fantasma do Caos, 05 Guerreiro
  Esquecido, 06 Dominus, 07 Deimos (DLC6 tem cópia idêntica), 08 Kratos cinza (variação, sem item).
- `costumes/general_kratos/imagem_menu.py` gera as imagens do menu a partir das imagens OFICIAIS do traje
  base (gocostume0 Kratos / gocostume6 Dominus: mesma pose/posição) com o MESMO ganho por canal da textura
  (Kratos (156,142,132) → Deimos (109,85,71), × 1,15) na pele; máscaras de `dark_odyssey/imagem_menu.py`.
- **General Kratos (armadura)** = `costumes/general_kratos_armadura` (slot 11): WAD do Dominus
  (`R_HERO06`; texturas de pele TX08FFABDA/TX09BFCDF6, mesmas UVs do Kratos) com a pele no tom do
  Deimos (mesmo `recolorir.py`; o 5º slot do Dominus já é branco). Mesmo bônus do General.
- Bônus (como no GoW II): **metade do dano causado, dobro do dano sofrido** → `[0.5, 2, 1, 1, 1, 1, 0]`.
  Textos: frase do Apolo ("causa metade dos danos") + "inimigos causam o dobro" da Odisseia.
  ZH: Kratos = 克雷多斯 (a fonte não tem 奎).
- Com/sem armadura no mesmo item do menu exigiria mexer no script do menu (`SMI_Shell`) → feito como
  2 itens (o usuário aprovou "General Kratos (armadura)").

### Atena (pesquisa, 2026-11-21)
- Só existe a Atena FANTASMA: `R_ATHENA00.WAD` (MG_d492a5f9_0; materiais `model_armorfinal1_lightingfeatures1`,
  `model_eyesfinal1opacity`, `model_left/rightskirtfinal1…opacity`; textura de cor TX69F18E99 2048² com pele e
  armadura NORMAIS — o aspecto de fantasma vem dos shaders/opacidade + texturas de nuvem/raio).
  `R_ATHENAFEAR` = estátua (textura de pedra). Materiais "athena" nas fases OLY225/275/325/350 = estátuas
  gigantes do cenário. Nenhum modelo da Atena "viva" como no GoW II.

### Deus da Guerra / God of War (armadura; PAUSADA em 2026-11-21 — deixava o jogo lento quando selecionada; fora do mod de teste)
- **Plano de montagem definido pelo usuário (2026-11-21), para quando retomar — juntar peças de trajes
  do próprio jogo:**
  - **Tanga inteira do "Fantasma do Caos"**, incluindo o cinto; a parte metálica fica **dourada no
    mesmo tom do dourado da armadura**.
  - **Pano vermelho** do Kratos padrão.
  - **Braçadeiras e luvas** do Kratos padrão.
  - **Tornozeleiras e calçados** do Kratos padrão.
  - **Peitoral e ombros inteiros do "Dominus"** (`R_HERO06`); o desenho do peito será modificado depois.
  - **Ombreiras já construídas** (carneiro do SC, grupos 9/6, posição aprovada no teste 11).
  - Fantasma do Caos = `R_HERO04` (MG_f402a4e_0), Dominus = `R_HERO06` (MG_382512b6_0).
  - **Viabilidade (2026-11-21):** todos os `R_HERO00..08` têm esqueleto de 254 juntas com os ossos do
    CORPO idênticos (nomes e pose; só rosto/asas de Hermes variam milímetros) → peças presas a ossos do
    corpo (peitoral, ombros, braçadeiras, luvas, botas, cinto) podem ser COPIADAS de um MG para outro
    com os pesos originais (índices de osso absolutos). **Conflito:** as juntas 165..219 (saia/pano)
    são reaproveitadas por cada traje com OUTROS nomes e posições (Kratos `JOfrontSkirt…/JObackSkirt…`,
    Dominus `kratos6JOfrontSkirt…`, Fantasma `joint07…`) → só um "rig de saia" por WAD. Tanga do
    Fantasma + pano vermelho do Kratos = duas peças de saia: uma precisa ser religada (pesos para os
    ossos de saia do outro, ou pélvis/coxas; ou converter vértices para a pose de ligação nova).
  - Falta descobrir: como o conjunto (set) da malha referencia o material (o MDL tem só 0x80 B; a
    lista de 16 materiais deve estar no MG ou na ordem das entradas MAT), para copiar MAT + texturas
    de outro traje para o WAD. **Lentidão** (relato do usuário): não existia só com as ombreiras; começou com o
    PEITORAL gerado (casca da pele, grupos 7/10/11/12 em espaço do modelo). Com peças do próprio jogo
    o usuário acredita que não ocorra.
- **v5 = MONTAGEM com peças do jogo (2026-11-21; teste 13 pendente; slot 12 no mod de teste)** —
  `costumes/god_armor/montagem.py` (chamado pelo `pos_wad.py`), sobre o R_HERO00:
  - tanga + cinto do Fantasma (material skirt_m: 14 partes, 3539 tri) → grupo 14 (cinto do Kratos sai);
    peitoral + ombros do Dominus (kratos06skirt_fancy_m + fancy_mred do grupo da pele: 4 partes, 1845 tri)
    → grupo 18; ombreiras de carneiro (`construir.so_ombreiras`); pano vermelho do Kratos escondido
    (índices zerados); braçadeiras/luvas/botas do Kratos intactas. Metal da tanga (TXA6C9CFBE, partes pouco
    saturadas) → dourado `OURO` das ombreiras. `texturas_armadura.py` agora só gera as texturas do fleece.
  - Ferramentas novas: `wad_edicao.py` (blocos; `copiar_material` = grupo GroupStart..próximo GroupStart
    com MAT/ANM/shaders + texturas que faltam; `acrescentar_materiais` = refs no fim de CADA bloco de
    variante + MDL +0x1c; Kratos: 16 blocos, bloco 9 = `_sw20`), `malha_transplante.py` (`extrair` peças com
    pesos de outro MG, rígidas viram peso 255; `abrir_espaco` antes da região de vértices; `gravar_grupo`;
    `esconder`), `malha.conjuntos` (registro do conjunto pela tabela +0x24 do grupo: material em R+0x26),
    `esqueleto.copiar_juntas` (nomes, locais @0x3ff0, poses inversas @0x7f80), `montar_heroi.py`.
  - Esqueleto: juntas 160..223 + os 2 `SCR_cloth` (frontskirtshape/backskirtshape: só parâmetros finais
    diferem) vêm do Fantasma. `ANM_hero` é idêntico em todos os R_HERO (saia = simulação de tecido).
  - **Teste 13: crash ao escolher o traje** (log do SpartanPort em `C:\Games\God of War III\user\last_run.log`:
    `Fault: read access to 8 at guest offset 0x1b9e09` = busca binária `0x1bd170` numa tabela global sem achar).
    Causa provável: **`MATX_R_Hero` (+0x10) = (nº de programas de shader = prefixos distintos das entradas
    0x770001 sem `dbg`, nº de variantes = entradas − programas)** — confirmado nos 9 R_HERO; a montagem
    copiava 5 programas novos sem atualizar → `wad_edicao.atualizar_matx` (23,104 → 28,128). Teste 14:
    slot 12 corrigido + slot 13 "Teste DG (só materiais)" (`costumes/_teste_dg_materiais`, temporário: só a
    etapa de materiais) para separar materiais × malha/esqueleto.
  - **Teste 14: os dois (DG e "só materiais") ainda travaram, mesmo ponto.** Causa real: **MAT +0x7c = u32 do
    PROGRAMA de shader** (entradas `<PROG>_<variante>` / `dbg_<PROG>_…` tag 0x770001). Os shaders que vêm logo
    depois do GroupEnd de um MAT são de OUTRO programa (do material seguinte; MATs ficam ordenados pelo
    programa e o programa aparece ANTES do 1º MAT que o usa). A cópia antiga levava os shaders errados → os 6
    materiais apontavam para programas inexistentes. `copiar_material` agora copia o grupo do MAT
    (GroupStart..GroupEnd) + o programa de +0x7c (se faltar, inserido antes). Conferência: todo MAT tem o
    programa e ele vem antes (vale nos originais e no montado). MATX → (29, 128). Teste 15 pendente.
  - **Teste 15: abriu!** (DG e "só materiais"; o item de diagnóstico foi removido). Problemas: tanga dourada e
    brilhante "como as botas", peitoral quase invisível (pele à mostra). Causa: **registro do conjunto
    R+0x08 (u16) = índice do MATERIAL, igual a R+0x24** (confirmado em 302 conjuntos de 5 R_HERO); o
    gravador mantinha o do doador (6/7 = hermesboots/bootwraps no Kratos). Corrigido em
    `malha_transplante.gravar_grupo`. (O gravador antigo `malha_escrita.substituir_grupo_ponderado_no_lugar`
    gravava 6 ali → as tiras de couro usavam o material hermesboots.) Flags R+0x2c: Kratos 0x7c2/0x7c3/0x7cb,
    Dominus/Fantasma 0x7e2/0x7e3 (mantidas do doador). Teste 16 pendente.
  - **Teste 16: "ficou ótimo"** no menu. Problemas: (a) a ombreira direita (grupo 9, osso do Velo
    `gldnFlcShould1` 0x61) some em "Novo jogo" — **o jogo esconde os ossos do Velo até o Kratos ganhá-lo** →
    agora no osso do braço `JORightUpperArm1Twist1` 0x60 (espaço do modelo), como a esquerda (0x82);
    (b) peças transplantadas PISCANDO no jogo (as ombreiras não): **cauda do conjunto** = registros por
    (submalha, osso): centro da caixa (modelo) + u8 osso + raio em float compactado (1 B expoente + 16 bits
    de mantissa, BE) ≈ 1,35–1,45 × meia-diagonal da caixa — eu gravava a meia-diagonal (esferas pequenas →
    descarte por visibilidade). Agora os registros ORIGINAIS do doador são copiados (0 estimados; estimativa
    = 1,5×). **R+0x3c = fim dos índices (sem alinhar), R+0x40 = cauda** (iguais quando os índices terminam
    alinhados). Teste 17 pendente.
  - **Pano vermelho (pedido de 2026-11-21, teste 18 pendente):** `montagem.pano_vermelho` — os 15 conjuntos
    skirt_cloth_m (material 15) do MG ORIGINAL do Kratos, puxados para 1,5 cm por dentro da tanga (sem chegar
    a < 6 mm da pele) onde ela cobre; o que fica totalmente acima de barra+5 cm (escondido e espremido entre
    corpo e tanga) é removido (1222 de 1760 tri) → sobra a parte pendurada abaixo da barra (y 0,82–1,14,
    painéis da frente e de trás). Pesos copiados dos vértices da tanga mais próximos
    (`malha_transplante.repesar`, 4 ossos) → segue os ossos de saia/simulação do Fantasma. Gravado no grupo 14
    junto com a tanga (material 15 do próprio Kratos). Originais da pele continuam escondidos.
  - **Teste 18: pano vermelho ficou por baixo da tanga, mas FPS muito baixo → usuário pediu para tirar.**
    `montar(etapas=...)` sem 'pano' por padrão (código mantido; causa da lentidão não isolada).
  - **Cota de malha de bronze nos braços e pernas (2026-11-21, teste 19 pendente)** — referência
    `referencias/god_armor/cota_de_malha_bracos_pernas.jpg` (arte do GoW II). Só TEXTURA (sem geometria):
    `costumes/god_armor/cota_malha.py` (chamado por `texturas_armadura.py`) rasteriza em UV os triângulos da
    pele: braços = chest_m (TX27CF5CC1) com |x| > 0,34 na pose T; pernas = head_m (parte de baixo de
    TX4A104642) com 0,12 < y < 1,30. Anéis (~1,5 cm; 16,6 px no braço, 8,9 px na perna) em cor, normal
    (TX27586F46/TX64D510EB, DXT5 x no alfa/y no verde), especular (TX4C116490/TX4395E116) e camada pálida
    (TX60366B5B/TXBEB53958). Antebraços/canelas ficam sob braçadeiras/grevas (grupos rígidos, sem pele).
  - **Teste 19:** malha parecia tecido (anéis pequenos), parte de trás do braço sem malha, pele atravessando o
    colete nas costas. → anéis de 3 cm (31,9 px braço / 17,8 px perna), mais contraste/relevo; LIMITE_BRACO
    0,24; **`malha_transplante.esconder_cobertos`**: esconde (índices degenerados) os triângulos da pele
    (chest_m + faixa de pano da cintura cloth_m) cujos vértices têm a reta da normal (±6 cm) cruzando um
    triângulo do colete (Möller–Trumbore) — nas bordas a reta não cruza, então não abre buraco. Teste de
    vizinhança por vértice falhava: o colete passa rente (≈4 mm) ou por dentro da pele nas costas baixas.
    2242 triângulos escondidos. Teste 20: "mais parecido" → malha em **AÇO NEGRO** (tom do colete do Dominus,
    TXFC6E37EC escuro ~(33,28,27)..(60,56,57)) em vez de bronze. Teste 21: "melhorou bastante" → **malha no
    PESCOÇO** (pedido: faixa de baixo até um pouco abaixo do meio, ~1/4 do pescoço): triângulos com
    1,98 < y < `LIMITE_PESCOCO` 2,11, |x| < 0,13, z > −0,12 (sem queixo/rosto), nas duas texturas (base no
    chest_m/corpo, laterais sob a barba no head_m/cabeça). Pescoço visível ~2,05..2,20; colarinho do colete
    sobe a 2,09 (frente) / 2,16 (costas). Anéis com período POR REGIÃO (densidade de texels própria: pescoço
    na cabeça 66,8 px, no corpo 33,6; braço 31,9; perna 17,8). Teste 22 pendente.
  - **Tanga sem o painel de trás + faixas de couro (pedido de 2026-11-21, teste 23 pendente):** peças da
    tanga (ordem de `extrair` no R_HERO04, material skirt_m): 0/1 cinto (rígido), 4/5/7/8/9 avental da frente,
    6/10 laterais, **2/3/11/12/13 painel de trás (cobria a bunda) → removidos** (`PECAS_TRAS`).
    `montagem.faixas_couro`: 16 faixas de 6 cm, ±65°..180° (lados e costas), y 1,46 (sob o cinto) → 1,12
    (~10 cm mais curtas que o avental, que vai a ~1,0), seguindo a superfície do painel removido + 8 mm,
    face dupla, UV = uma faixa com rebite da textura da tanga (eixo (240,575)→(185,870) px, ±16 px), pesos
    copiados da tanga original (`repesar`, inclui o painel removido → seguem a simulação de tecido).
    Atenção: o pano vermelho (também gerado + repesado) deixou o FPS baixo — conferir o FPS com as faixas.
    **Teste 23:** atrás piscando + alto das faixas entrando na coxa. As peças originais também têm face dupla
    e o raio original das caudas desses ossos de tecido ≈ 1× meia-diagonal (minha estimativa 1,5× basta) →
    causa provável: pesos MÉDIOS (k=6) misturando cadeias de simulação diferentes + cinto rígido. Agora as
    faixas também substituem as laterais (peças 6/10, `PECAS_LADO`) e copiam os pesos do vértice MAIS
    PRÓXIMO das peças removidas (`repesar(k=1)`). Teste 24: partes do pescoço perto do colete
    TRANSPARENTES (o esconder pegava pele sob o colarinho estreito) → `esconder_cobertos(y_max=1.97)`; axila
    cor de pele → malha também no TRONCO todo abaixo do pescoço (chest_m, y < 1,98: só aparece nas cavas
    e entre colete e cinto). Teste 25: ombreiras "mais finas, da finura do velo" → `construir.achatar_ombreira`
    (eixo de menor extensão por PCA: SC 0,241 m × velo grupo 9 0,144 → `ESPESSURA_OMBREIRA` 0,6, lado do ombro
    parado). Com isso aparecem embaixo as bordas dos ombros do colete do Dominus. Teste 26: "desceu, não está
    na altura certa" → âncora no lado de FORA (topo parado, a face de baixo sobe; folga mín. 1,1 cm do corpo).
    Teste 27: pintar as ombreiras "com as cores corretas", vermelho/preto no tom do peitoral →
    `texturas_armadura.regioes_ombreira`: da textura do SC (64²) com cor/brilho suavizados (σ 2 px): vermelho =
    r/g > 1,38 e L < 115 (fundo vinho atrás do carneiro), preto = L < 48; resto = metal dourado (`OURO`).
    Tons do colete do Dominus: `VERMELHO` (82,25,16), `PRETO` (40,35,34), sombreados pelo relevo. Teste 28: nuca
    sem malha → `LIMITE_PESCOCO_COSTAS` 2,21 para z > 0 (o colarinho de trás sobe a ~2,16); **2ª ombreira**: no SC,
    sob o carneiro (mat_15), há 2 componentes do mat_12 (armadura do tronco) no ombro: placa curva por cima/atrás
    do ombro (64 tri) + faixas penduradas no alto do braço (15 tri) → `construir.pecas_ombro_sc` (mesma
    transformação do carneiro, centrada nele; `achatar_ombreira(ref=carneiro)`), nos grupos 9/6 (340 tri ≤ 402);
    textura do mat_12 do SC (09df94e0…, 128²) recolorida pela mesma regra → quadrante sup. dir. do atlas
    TXE90D274D (era do peitoral antigo). Teste 29: (a) nuca do lado ainda sem malha (atrás da orelha) → limite
    do pescoço com transição suave em z: 2,11 (z ≤ −0,10) → 2,21 (z ≥ −0,02); (b) faixas penduradas em VERMELHO
    do peitoral: a faixa da textura da tanga também é usada pelo avental da frente → `montagem._faixa_vermelha`
    copia a faixa (deitada, couro em `VERMELHO_PEITO`, rebites dourados) para a área livre do canto inferior
    esquerdo de TXA6C9CFBE (x 40..340, y 920..952) e as faixas usam a cópia; (c) grevas/tornozeleiras
    (TXE3FF895B, cobre avermelhado) → dourado das ombreiras com 25% do cobre original ("meio dourado", arte
    do GoW II), tira de couro de cima original (`texturas_armadura.grevas`). Teste 30: tiras de couro no alto do
    braço, sob a ombreira (o usuário escolheu esse lugar) → `construir.tiras_braco`: 9 tiras de 5 cm em arco de
    ±125° em volta do eixo ombro(0x42)→cotovelo(0x43) a partir do topo (lado de baixo, que encosta no tronco
    com o braço caído, sem tiras), x 0,36 (sob a ombreira) → 0,52, raio 0,10 → 0,11, face dupla, nos grupos
    rígidos das ombreiras (g9 376/402 tri); UV = célula B do atlas (couro + rebite), agora no vermelho do
    peitoral (`couro_tira`). Teste 31: "tiras legais; faltou física e a ponta como as do cinto; as do cinto
    ainda não estão vermelhas" → (a) as "do cinto" eram as faixas DIAGONAIS do avental da frente (canto esq. de
    TXA6C9CFBE, x < 375, y 430..890: `AREA_FAIXAS_FRENTE`) → couro em vermelho do peitoral, metal dourado;
    (b) tiras do braço com o MESMO desenho das do cinto (ponta + rebite): `texturas_armadura.tira_fantasma`
    copia a faixa da tanga para a célula B do atlas, em pé (x 0,30..0,70 da célula); (c) física: o esqueleto não
    tem ossos simulados no braço (só a saia tem `SCR_cloth`) → precisaria criar juntas + script de tecido; não
    feito. Teste 32: pontas em FLECHA (vértice central extra na ponta, `TIRAS_BRACO['ponta']` 3,5 cm), tiras POR
    CIMA do braço/colete (raio por tira e linha = maior distância ao eixo da pele + peitoral do Dominus naquele
    ângulo ±(meia largura+6°) e ±3 cm ao longo do braço, + `FOLGA_TIRA` 1,5 cm, máx. `RAIO_MAX_TIRA` 0,135 sob a
    ombreira; a montagem passa os obstáculos para `so_ombreiras`); g9 394/402 tri. Armadura dos braços e das
    pernas DOURADA: `texturas_armadura.armadura_dourada` (TX3DEC657A: placas + cinto → dourado envelhecido das
    grevas; elos das correntes = s < 0,33, matiz 0,072..0,2, L > 0,25 → cor original). Teste 33: (a) faixas na
    frente da coxa ESQUERDA (x < 0; a tanga do Fantasma só tem faixas sobre a direita, peças 8/9) →
    `montagem.FAIXAS_COXA_ESQ` (4 faixas, −58°..−15°, y 1,46 → 1,03, por cima do avental peça 4 + 1,2 cm, pesos
    k=1 das peças 4/7); `_faixas` = gerador comum. (b) MANOPLAS: mão = dedos/polegar (chest_m-0/-1, região
    própria de TX27CF5CC1, as 2 mãos na mesma região espelhada) + faixas de pano do dorso/punho (cloth_m com
    x > 0,9, ilha da mão em TX5512508B; normal TX587A1BF5, especular TX0393CBA3) → `cota_malha.manoplas`
    rasteriza em UV a posição/normal 3D da mão direita: placas douradas de 2,2 cm ao longo de x (rampa + fresta,
    relevo no normal map), palma (normal y < −0,45) couro escuro, punho (faixas, x < 1,0) vermelho do peitoral.
    (c) chifre da ombreira: sulcos entre os gomos (L − blur(L) < −0,09 dentro do círculo `CHIFRE` (0,45; 0,54;
    r 0,27) da textura do SC) em vermelho. Teste 34: o CINTURÃO (anel das peças 0/1 da tanga: lados e costas; a
    frente é o avental) deve parecer complemento do peitoral → painel central com arabescos (cápsula
    `PAINEL_CINTO` x 45..978, y 318 ± 76 px em TXA6C9CFBE, 6 px para dentro) no `PRETO_PEITO` (40,35,34) com o
    relevo original; borda e nervura douradas (`_dourar_metal`). Teste 35: (a) malha da nuca alta demais →
    `LIMITE_PESCOCO_COSTAS` 2,175 (colarinho: frente 2,02 [decote em V] → costas 2,16); (b) **RENOMEADO
    "Armadura de Deus" / "God Armor"** (como no GoW II) nos 16 idiomas + descrição atualizada; (c) correntes
    douradas → máscara dos elos por proporção de canais (bege ~(148,130,107): r/g 1,14 ± 0,09, g/b 1,21 ±
    0,14, abertura+fechamento) — a antiga (saturação) deixava as bordas dos elos douradas; (d) manoplas com
    placas de 4 cm (`PLACA_M`; 2,2 cm era detalhado demais). Teste 36: malha do pescoço mais baixa
    (`LIMITE_PESCOCO` 2,07, costas 2,168) + **PANO VERMELHO NOVO** (referência `referencias/god_armor/geral.jpg`:
    painel da frente com grega + pano de trás inteiro até o joelho; o original do Kratos é rasgado) →
    `costumes/god_armor/pano_cfg.py` (blocos na textura TX5512508B, na área da saia original escondida:
    frente (420,30)-(820,590) com a grega bege-dourada na borda de fora, trás (860,30)-(1440,590) liso com barra;
    trama = detalhe fino da amostra do pano das canelas), `texturas_armadura.pano_textura` (+ normal plano e
    especular baixo nos blocos), `montagem.pano_novo`/`_pano` (grade: frente −40°..15° na posição do painel
    original, por cima do avental/faixas +1,5 cm; trás 95°..265° por baixo das faixas +3 mm; y 1,45 → 0,85;
    face dupla; pesos k=1 das peças da tanga). Material **8 (cloth_m)** e registro de peça da tanga — a tentativa
    anterior (material 15 skirt_cloth_m) deixou o FPS baixo. Teste 37 pendente (conferir FPS).
    **Teste 37 → pano na posição errada; refeito (2026-11-22) na posição/inclinação do pano ORIGINAL do Kratos**
    (material 15 do R_HERO00 medido): começa na frente um pouco à esquerda do centro, borda inclinada para a
    direita ao descer (-55° no cinto → -22° na barra), barra mais baixa na frente (0,85) subindo ao dar a volta
    pela direita/costas (~1,0–1,05) até o quadril esquerdo (1,28; abertura -100°..-55°). `pano_cfg.BARRA`
    (ângulo, y), `FRENTE`/`TRAS` com `ang_topo`/`ang_base` e folga por ângulo; ângulo contínuo -90°..270°. Pano de trás agora POR CIMA das faixas de couro (ref inclui as faixas, folga 8–10 mm).
  - **SCR_cloth (decifrado 2026-11-22)** — entrada tag 0xd0001 no grupo do `gohero` (2 por R_HERO:
    `frontskirtshape`, `backskirtshape`): +0x48 nome; +0x80 i32: 1ª raiz, nº de cadeias, juntas por cadeia (6),
    -1, nº de cadeias, nº de ESFERAS; +0x98 6 floats (parâmetros: frente 0,.96,1,0,1,1; trás 0,.99,1.5,0,.8,.8);
    +0xb0 raízes (i32 × nº cadeias; cadeia = raiz..raiz+5); depois esferas de colisão de 24 B
    `x,y,z (local do osso), raio, i32 osso, i32 id` (pélvis, costas, coxas, JOclothCrotch). Fantasma: frente
    3 cadeias 165/171/177, trás 6 cadeias 184..214; as juntas de uma cadeia são IRMÃS (todas filhas de
    frontSkirtShape 164 / backSkirtShape 183), eixo Y da junta contra o sentido da cadeia. Nenhuma cadeia
    livre na montagem (só as pontas 170/176/182/189 e 160..164, 183, 220..223 sem pesos).
  - **Física nas tiras do braço — TESTE 38 (1 tira, braço direito)**: `montagem.CADEIA_BRACO` — a cadeia
    165..170 (frente-esquerda) é religada ao osso 0x60 (hierarquia: sai da lista de filhos de 164, entra como
    1ºs filhos de 0x60; matrizes local/inversa novas ao longo da tira do topo do braço, índice 4); pesos da
    tanga/pano nessa cadeia → cadeia do centro 171..176 (`_trocar_cadeia`); a tira sai do grupo rígido 9
    (`so_ombreiras(sem_tira_dir=4)`) e vai para o grupo 14 com pesos nas juntas (2 mais próximas);
    `ESFERAS_BRACO` (3 esferas no osso 0x60) acrescentadas ao SCR da frente. Etapa 'fisica_braco'. Riscos:
    animação com trilhas dessas juntas, simulação presa à cintura, travamento. Se funcionar: liberar mais
    cadeias (ex. reduzir as 6 de trás) para 2–3 cadeias por braço.
  - **Meta (pedido de 2026-11-22): igualar TUDO ao Soulcalibur + GoW II, usando peças em alta definição nativas
    do GoW III.** Lista do que falta/diverge (análise de 2026-11-22): (1) grevas altas com joelheira (placa com
    furos) e faixa de corrente/grega no joelho; (2) sandálias de couro vermelho com dedos de fora; (3) crista
    dourada atrás das ombreiras; (4) 2ª fileira de tiras sob as ombreiras; (5) couro vermelho no alto das
    braçadeiras; (6) faixa grega na borda de baixo do peitoral [feito no peitoral]; (7) pátina esverdeada;
    (8) placa de costas com desenho; (9) PEITORAL com o desenho do GoW II [feito]; (10) cota de malha
    marrom-avermelhada nas referências (usuário escolheu aço negro); (11) na arte o painel do pano fica na coxa
    DIREITA (o nosso segue o GoW III, à esquerda, pedido do usuário); (12) tiras de couro largas da cintura
    (pteruges) em vez do avental do Fantasma; (13) ombreiras de leão/carneiro do GoW II; (14) manoplas com
    volume; (15) gola de malha alta.
  - **Peitoral GoW II (teste 39 pendente)** — `costumes/god_armor/peitoral_gow2.py`: mapeia cada texel do colete
    do Dominus (TXFC6E37EC, ilha única: frente abaixo do buraco do pescoço, costas acima e invertidas) para a
    posição 3D e desenha em VISTA DE FRENTE (tela em metros): couraça roxa (`BASE` (62,46,62)), músculos do
    relevo do próprio colete, gola dourada (borda do buraco do pescoço, `GOLA_PX`), crescentes no alto dos
    peitorais = CÃO de perfil virado para o centro [2ª versão: desenho DECALCADO do peitoral.jpg em polígonos (`DEC_*`, px da referência → modelo por `_dec`: esterno x=600, escala x 0,0008 m/px, alturas por `DEC_ALTURAS`), cão/pata do lado direito espelhados, parte de baixo assimétrica; relevo da frente suavizado σ3 para tirar os entalhes do Dominus] (cabeça com focinho, orelha, olho vazado e boca aberta no alto; corpo = crescente; garras sob os peitorais = patas), flor-de-lis no esterno, garras sob os peitorais, faixa em zigue-zague
    no lado ESQUERDO (x < 0, como na arte), filete + grega na cintura. Dourado antigo do Dominus removido na
    frente (cor e relevo do normal [TX9DC6B004: x no alfa, y no verde; sinal calibrado pelo dourado antigo]);
    costas mantêm o desenho do Dominus em roxo; vermelho (fancy_mred) → roxo escuro. Especular TX08D5DF6D.
    Saída em `texturas_montagem/`; `montagem._peitoral_gow2` troca as texturas no WAD (`_trocar_textura`).
    Rodar `python -I costumes/god_armor/peitoral_gow2.py` antes do instalar_teste.
  - **Peitoral = desenho do ORIGINAL (3ª versão, 2026-11-22; pedido "extraia o desenho do original")**: o port do
    GoW II (`referencias/god_armor/port_gow2_god_armor_1_1/.../R_HERO00.WAD`) tem a couraça original
    (material chest_m = 11; cor TXA950000B 2048×1024; texturas extraídas em `original/port_gow2/png`): FRENTE =
    dois cães em "S" (cabeça no alto virada para o centro, patas, cauda descendo), flor-de-lis, leques nas
    laterais, abdômen esculpido; COSTAS = cabeça de carneiro com chifres e nervuras. `peitoral_gow2.desenho_port`
    transfere em 3D: texel→posição na couraça do port (`mapa_port`) e no colete do Dominus; correspondência por
    (ângulo em volta do tronco × `CIL_R`, altura) com a altura esticada (port 2,06→1,44 ↔ nosso 2,06→1,60:
    `PORT_Y_*`, `NOSSO_Y_BASE`); dourado = máscara de cor do port, tom = luminância do port (escultura). Base
    PRETA (40,35,34) como no original. Nossa gola, filete e grega por cima. **Relevo e textura do colete do Dominus ficam INTEIROS por baixo** (teste: "ficou liso como a pele" quando o relevo era suavizado) — só o dourado do miolo da frente (garras) vira preto; bordas (< `BORDA_DOMINUS_PX` da borda da ilha) e faixas ficam. (O decalque do peitoral.jpg e o
    cão desenhado ficaram no código como `desenho_decalque`/`DEC_*`, só a faixa de baixo é usada.)
    Prévia: `costumes/god_armor/preview/peitoral_vs_original.png`. Antes de lançar: o desenho vem de textura
    de terceiros/Sony — o delta do pacote levaria a textura gerada como literal.
  - **Peitoral — versão atual (4ª, 2026-11-22): "use TUDO da armadura do GoW III e troque só o desenho do peito"**:
    `peitoral_gow2.main` mantém o colete do Dominus inteiro (cores, bordas/gola/faixa douradas, vermelho dos
    ombros, costas, relevo, especular); só no MIOLO da frente (`PEITO_Y0..Y1`, a mais de `BORDA_DOMINUS_PX` da
    borda da ilha) o desenho antigo (garras + contorno) é apagado (cor/normal/especular preenchidos pela
    vizinhança, sem puxar dourado) e os cães + flor-de-lis do port são pintados no dourado do próprio Dominus.
    Sem carneiro nas costas, sem gola/grega nossas (versões anteriores descartadas). Prévia:
    `costumes/god_armor/preview/peitoral_atual.png`.
  - **Teste 1 da física do braço: o pano da frente ficou "reto para cima"** → a cadeia 165 é o 1º campo do
    cabeçalho do SCR_cloth da frente (provável âncora da simulação); religá-la ao braço levou a simulação da
    saia junto. Agora a cadeia do braço é a 177..182 (`CADEIA_BRACO`, pesos dela → 171..176).
  - **Pacote:** o WAD montado tem bytes de R_HERO04/06 → o delta atual (só copia do arquivo de origem)
    os gravaria como literais (= distribuir arquivos do jogo). Antes de lançar: delta com várias fontes
    (copiar trechos de R_HERO04/06 do jogo do usuário).
- **Nome no jogo: "Armadura de Deus" / "God Armor"** (pedido de 2026-11-22, como no GoW II; antes "Deus da
  Guerra" / "God of War" e "Armadura do Deus da Guerra"). Nos outros idiomas: Dios de la Guerra, Dieu de la guerre, Dio della Guerra,
  Kriegsgott, Oorlogsgod, Bóg Wojny, Savaş Tanrısı, Бог войны, 軍神, 전쟁의 신, 戰神.
- Ombreiras: o osso delas segue o braço; a pose T tem o braço na horizontal, mas no jogo (de pé) ele
  fica ~70° caído → girar em volta de X na pose T só TORCE a peça em volta do braço. Para inclinar o
  topo para trás na pose de pé, girar em volta de `EIXO_TRAS_OMBREIRA` = (cos70, sin70, 0) na pose T
  (positivo = topo p/ trás). Atual: torção `INCLINACAO_OMBREIRA = -25°` + `INCLINACAO_TRAS_OMBREIRA = 30°`
  (teste 9 do usuário: ainda inclinada p/ frente com só a torção). + `ABERTURA_OMBREIRA = 15°` em volta do
  vertical da pose de pé (`EIXO_VERTICAL_OMBREIRA` = (-sin70, cos70, 0)); positivo = face p/ trás (teste 10). Posição: `DESLOC_OMBREIRA` z = +0,015
  (teste 11: estavam à frente do corpo com z = -0,04; z na pose T = z na pose de pé). Sem animações decodificadas, a
  pose de pé é aproximada — ajustar pelo jogo.
- Inspirada na armadura do Kratos no **GoW II**. Decisões do usuário (2026-11-20):
  **geometria própria** (não usar o port de terceiros), cores **meio-termo** (dourado um pouco
  mais escuro/gasto, pátina leve), bônus **ataque 2x, dano ½, orbes 4x** → `[2, 0.5, 4, 4, 4, 4, 0]`.
  Slot planejado: índice 10 (`R_HERO10.WAD`, mensagem `*20009*`, registro 10 do R_PERM, `gocostume10`
  — `costumeimages.hash_modelo` ainda só aceita índice ≤ 9).
- Referências (`referencias/god_armor/`): `arte_spartan_gamer.jpg`; `soulcalibur_bd/` (PSP, OBJ+PNG:
  `kratos_2p_god_armor` = God Armor, `kratos_1p`, `armas`); `port_gow2_god_armor_1_1/` (port de
  terceiros — só referência; tem malha MG maior + 197 texturas 2048 + efeitos).
- Fases: (1) decodificar malha MG; (2) regravar idêntico; (3) armadura a partir do modelo do
  Soulcalibur, ajustada ao Kratos e com pesos transferidos da pele; (4) texturas + slot/bônus/imagem.
- **Malha MG** (tag 0x520001; Kratos = `MG_b826bd6e_0`; cópia `original/MG_kratos.bin`). Leitor:
  `ferramentas/malha.py` (exporta OBJ), esqueleto: `ferramentas/esqueleto.py`.
  - Cabeçalho: `u16 0x0d, u16 1, u32 INÍCIO DA REGIÃO DE VÉRTICES (0x41290), u16 nº grupos (22),
    u16 nº registros (2364), …`; tabela de grupos (u32 absolutos) em +0x18; registros de 20 B
    (`ffff0000`+4 floats, função desconhecida) logo após a tabela; descritores + índices; região de
    vértices até o fim.
  - Grupo rígido (ex. 9): +0x08 osso; +0x20 tamanho do resto; +0x50 `material<<16|1`; ponteiros
    relativos p/ cauda; paleta u16; streams 12 B (`s32 offset relativo à entrada, u8, uso, tipo, u8,
    u32 bytes`: uso1 posição float3, uso4/uso5 s16×4 (normal/tangente, w=±1), uso8 pesos u8×4,
    uso0x0a ossos u16×4, uso0x0f UV float2 em stream próprio); submalhas: 16 B
    (`nv, ntri<<8|flags, rel→índices, paleta(n<<16|início)`), índices u16; cauda 32 B (esfera).
  - Vértice rígido = 28 B; com pesos = 40 B. **UV: textura = (u, v−1)** (repetição; PNG y p/ baixo).
  - Material do grupo = índice na lista de 16 materiais do `MDL_b826bd6e` (0 barba, 1 dentes,
    2 olho ext., 3 olho int., 4 fleece, 5 armor, 6 hermesboots, 7 bootwraps, 8 cloth, 9 bootl,
    10 head, 11 chest, 12 eyegasket, 13 chest-0, 14 chest-1, 15 skirt).
  - Espaço: grupos rígidos = local do osso; grupo 21 (`hero`) = corpo com pesos em espaço do modelo;
    grupos 0/5/20 (cabeça/mandíbula/língua) também em espaço do modelo.
  - **Esqueleto** (entrada sem nome após `gohero`): 254 juntas; hierarquia 8 B em +0x14 (flags,
    filho, irmão, pai); nomes 56 B; matrizes locais 4×4 (v·M, translação na 4ª linha) começando
    16 B após o offset da tabela. Osso do grupo = índice da junta (ex. 0x21 lowOuterEyeRight).
  - Grupos rígidos reaproveitáveis p/ armadura: 6 gldnFlcWristGuard, 7 gldnFlcForeaerm,
    8 ArmArmorRight, 9 gldnFlcShould1, 10 gldnFlcBicep1, 11 gldnFlcClav, 12 gldnFlcClav01,
    13 ArmArmorLeft, 14 Belt, 16/18/19 canelas/ShinArmor.
  - **Plano de escrita (seguro):** em vez de inserir grupos, reaproveitar um grupo rígido: gravar o
    bloco novo (descritor+índices) e seus vértices no FIM do MG e trocar só a entrada da tabela
    (absoluta). Nenhum outro ponteiro muda. Tamanho da entrada MG no WAD é atualizado.
  - Gravador: `ferramentas/malha_escrita.py` (`substituir_grupo` = no fim [NÃO desenha];
    `substituir_grupo_no_lugar` = correto).
  - **Regras validadas no jogo (testes 1–4, slot 10 "Teste Armadura"):**
    - Redirecionar a tabela para um descritor gravado APÓS o início da região de vértices = a peça
      some (não é desenhada). → Use `substituir_grupo_no_lugar`: descritor no lugar do bloco antigo
      do grupo (tem de caber: 0xb4 + 6·ntri + 32 ≤ tamanho antigo); vértices podem ir para o FIM do MG.
    - Ossos auxiliares (sem pesos de pele: `gldnFlc…`, `ArmArmor…`, `Belt`, `ShinArmor`) → vértices em
      espaço LOCAL do osso. Ossos do corpo (`JO…` usados pela pele) → vértices em espaço do MODELO
      (pose de ligação, T). Ex.: ombreira espelhada no osso 0x82 em espaço do modelo = correta.
    - Espelho: inverter ordem dos triângulos e o w da tangente.
    - Orçamento (tri máx. no lugar): g6 459, g7 209, g8 679, g9 402, g10 144, g11 289, g12 286,
      g13 679, g14 919, g16 1045, g18 741, g19 1862.
  - Vértices: `uso4` = tangente, `uso5` = bitangente (s16×4, w=32767); **normal externa = uso4 × uso5**.
    **Triângulos em ordem HORÁRIA** (produto vetorial p/ dentro). Peças com ordem invertida aparecem
    "por dentro" e somem de alguns ângulos (backface culling) — visto no teste 6.
    Último byte de cada entrada de stream = stride em dwords (7=28 B, 0x0a=40 B, 2=8 B, 5=20 B).
    Pele usa UV em stream de 20 B (usos 0x16 e 0x0f intercalados). Leitor exige esse byte ≠ 0.
  - Visualização sem o jogo: `ferramentas/render.py` (z-buffer + Lambert; `render.kratos()`).
  - Construção da armadura: `costumes/god_armor/construir.py` + `encaixe.py` (ombreiras SC mat_15
    giradas pelo eixo do braço do SC → +X e posicionadas pelo centro da ombreira do Velo; grupo 9
    (osso 0x61, local) e grupo 6 (osso 0x82, modelo, espelhada); Velo restante (7,10,11,12) oculto).
    Textura das ombreiras = `TXE90D274D` (material fleece) gerada do SC ampliado + metal procedural.
  - **v1 completa** (`costumes/god_armor/instalar_teste.py` monta o mod de teste com slots 9 e 10):
    ombreiras SC (grupos 9/6) + peitoral = casca da pele do tronco (grupo 21, região |x|<0.29,
    1.48<y<2.00, sem pescoço) deslocada 3,5 cm, simplificada por grade e dividida em 4 partes:
    peito esq./dir. (grupos 11/12, osso JOBack3 0x4) e abdome esq./dir. (grupos 7/10, osso JOBack2 0x3),
    todas em espaço do modelo. UV cilíndrica na metade direita do atlas `TXE90D274D`.
    Texturas (`texturas_armadura.py`, tom meio-termo): atlas (ombreira + peitoral com grega),
    braçadeiras/cinto dourados, correntes aço escuro, botas/grevas douradas, saia vermelha com grega
    dourada; pele e tatuagem originais. Bônus registro 10 = [2, 0.5, 4, 4, 4, 4, 0]; mensagem 20009;
    imagem do menu provisória = do Kratos padrão (`costumes/god_armor/menu/imagem_menu.png` se existir).
  - **v2** (mesmo script): + gola de malha (pele da base do pescoço, deslocada 1,2 cm, simplificada,
    metades junto das placas do peito nos grupos 11/12 — placas limitadas a 205 tri), + tiras de couro
    (pteruges, 13 tiras geradas na frente/lados da cintura, grupo 18 [antes ShinArmor] no osso da pelve,
    dupla face), braçadeiras (grupos 8/13) e grevas (placa de metal dos grupos 16/19) remodeladas
    EDITANDO AS POSIÇÕES NO LUGAR (alargamento radial; abertura no cotovelo; joelheira = topo esticado).
    Atlas: célula B (couro, u .25–.5 / v .5–.75), célula C (malha, u 0–.25 / v .75–1).
    Pendente: imagem própria (print do menu de trajes com a versão atual).
  - **Grupos COM PESOS (vértice 40 B) — gravador `malha_escrita.substituir_grupo_ponderado_no_lugar`:**
    grupo = cabeçalho (+0x10 nº de conjuntos, +0x24 tabela de rel→registro de cada conjunto); registro
    R: `0x17,1,6|1<<16,float,1,0,0x20,0`, R+0x20 `6 | nsub<<16`, R+0x24 `1 | material<<16`,
    R+0x28 `soma paletas | nº ossos distintos<<16`, R+0x2c `0x7c3 | 4<<16` (rígido = 0x7c2), R+0x30/34/38
    rel→paleta(u16 crescente)/streams(6: pos, uso4, uso5, UV tipo 0x12, pesos u8×4 @+0x1c, ossos u16×4
    @+0x20)/submalhas; R+0x3c/40 rel→cauda = 1 registro 16 B por (submalha, osso): centro da caixa
    (modelo) dos vértices do osso + u8 osso + 3 bytes (1º = expoente do raio; resto não decifrado).
    Ossos dos vértices = juntas absolutas; sem uso = peso 0/osso 0; pesos somam 255. A saia original
    (material 15) = vários conjuntos de 1 submalha com ≤ 16 ossos; ossos da saia `JOfrontSkirt1..18`,
    `JObackSkirt1..36` (0xa5..0xdb, animados). **Tiras de couro (grupo 18) agora com pesos copiados da
    saia** (`construir.pesos_da_saia`, 2 ossos/vértice, 4 conjuntos): rígidas na pelve, a coxa as
    atravessava ao correr (simulado: 4–36 cm). Teste 12 no jogo pendente.
  - **v4 (só renderizado):** peitoral = casca da pele SOLDADA (vértices duplicados nas costuras das
    submalhas faziam buracos), afastada 4,5 cm, simplificada UMA vez, suavizada (Laplaciano, borda
    fixa) e só então dividida nas 4 partes por limite de triângulos (bordas compartilhadas, sem
    frestas). Render: `render.kratos(b, sk, grupos_modelo=(6,7,10,11,12,18,16,19))`.
  - **v3 (teste 8: peitoral "rachado"/estourado, braçadeiras escuras):** o material fleece usa também
    normal `TXE8CC240F`, especular `TX2E5E7D75`, oclusão `TX5F3FCC5C` (512², relevo da ombreira
    original) → agora gerados do atlas (`mapas_fleece`). Vértices não compartilhados davam normais por
    face (facetas) → `normais_suaves` (solda por posição, só faces com dot > 0.5). Braçadeiras dos
    antebraços = região das correntes de `TX3DEC657A` → douradas.
  - Fonte da geometria: `soulcalibur_bd/kratos_2p_god_armor` (OBJ, altura 2,64; partes por material:
    mat_15 ombreiras de carneiro, mat_12 peitoral/tronco, mat_17 cota, mat_16 saia, mat_14 tiras,
    mat_13 grevas). Escala ~0,92 p/ o GoW III; peças precisam de alinhamento por osso.
  - Ferramentas de engenharia reversa: `ferramentas/desmontar.py`, `disasm_scan.py`.

## Caminhos

- SpartanPort: `C:\Games\God of War III` (`settings.json` → `game_dir`, `mods_dir`).
- Dump do jogo: `C:\Users\rodri\Downloads\ShadPS4 Output\CUSA01623`
  (WADs em `EXEC\WAD\PS4_LE\`; DLC em `EXEC\DLC\DLCn\WAD\PS4_LE\`).

## Formato técnico (descoberto)

- **WAD**: sequência de entradas; cabeçalho de 0x40 bytes = `u32 tag, u32 tamanho, char nome[0x38]`;
  dados alinhados a 16 bytes. Todos os `R_HERO0x.WAD` têm o nome interno `WAD_R_Hero`
  (por isso um visual pode ir para qualquer slot).
- **Texturas**: entradas tag `0xd0001` com nome `TX????????.????????.dds`; dentro há um
  preâmbulo (0x4C bytes) + **DDS padrão** (DXT1/DXT5, layout linear, mipmaps completos).
  Substituição no lugar (mesmo tamanho) → WAD final com o mesmo tamanho do original.
- Texturas do Kratos padrão (R_HERO00): rosto `TX4A104642`, corpo `TX27CF5CC1`,
  saia `TX5512508B`/`TX4D95EEC1`, botas de Hermes `TXE3FF895B`, ombreira/metal `TXE90D274D`,
  cinto/braceletes/correntes `TX3DEC657A`. Laranjas = normal maps; cinzas = brilho/AO.
- Slots: `R_HERO00` = Kratos padrão; `R_HERO01..08` = trajes extras (02 parece Apolo;
  05 armadura com pelos; 07 = DLC6; 08 = variação do padrão sem botas/ombreira).
  Menu "Seleção de traje" (PT): Kratos, Kratos do Medo, Apolo, Armadura de Morfeu,
  Fantasma do Caos, Guerreiro Esquecido, Dominus, ... (lista continua). Mapeamento exato
  slot → traje ainda não confirmado. O mod em R_HERO00 também aparece no menu Tesouros.
- Um visual pode alterar vários WADs: `costume.json` → `wads` (`base`, pasta `texturas`,
  `destino` = `slot` ou nome fixo). Texturas ficam em `costumes/<id>/texturas/<WAD>/`.
- **SpartanPort mods**: pasta em `mods/` espelhando o jogo a partir de `EXEC/`, com
  `mod.json` (`name`, `author`, `version`, `description`, `url`) e `preview.png`.
  Ordem/ativação em `mods.json` (`order`, `disabled`); o mod mais abaixo vence.
  Mods podem trazer patches XML em `patches/`. Doc: github.com/FelipePrado0/SpartanPort `docs/MODS.md`.
- Textos do jogo: `EXEC/WAD/PS4_LE/R_LANG_*.WAD` (há mais de um português: `R_LANG_PT`, `R_LANG_BR`).
- DLC6 adiciona um traje com `R_HERO07.WAD` + `COSTUMEIMAGES.WAD` + `R_LANG_EN.WAD`.

## Slot novo de traje (descoberto — em teste)

Lista de trajes é **dados**, não código:
- **Textos** (`R_LANG_*.WAD` → `MSGS_TXT`, UTF-8/CRLF; também `EXEC/DLC/DLC6/WAD/PS4_LE/R_LANG_EN.WAD`):
  mensagem `*2000N*[DLCk]` = linhas `índice` / `TRUE|FALSE` (desbloqueado) / nome / `heroImageNN` /
  descrição (1+ linhas). Índice → `R_Hero%02d.WAD` e linha da tabela de bônus. Oficiais: 20000..20007
  (índices 0..7; Deimos usa imagem heroImage10). 1ª linha do MSGS_TXT = capacidades
  `<ids> <linhas>` (aumentar ao inserir). Ferramenta: `ferramentas/lang.py`.
- Odisseia: exclusão do olho na textura do corpo é um **disco** (raio 0.155), não caixa — a caixa
  deixava vermelha a ponta de uma faixa da tatuagem das costas.
- **Bônus** (`R_PERM.WAD`, offset `0x26813f8`, 16 registros de 7 floats, stride 0x1c):
  `[ataque, dano sofrido, orbe?, orbe?, orbe?, orbe vermelho, 0]` (verde/azul/amarelo nos 3 do meio).
  Registros 9..15 livres/neutros. Código que aplica: eboot `0x50e40` (traje do jogador em `0x420564`).
- Menu (`SHELL.WAD` → script `SMI_Shell`) reserva 64 trajes (`costume0..63`).
- Odisseia Sombria (GoW II): ataque 2x, dano sofrido 2x, orbes vermelhos 4x → registro 9 =
  `[2, 2, 1, 1, 1, 4, 0]`, mensagem `*20008*`, `R_HERO09.WAD`.
- **Imagem do menu**: o menu mostra o objeto `gocostumeK` do `COSTUMEIMAGES.WAD` (K = índice do
  traje; o `heroImageNN` do texto não é usado). Cada imagem = textura 256x512 DXT5 sem mips →
  `MAT_ubershaderN` → `MG_/MDL_e075da3X` → `gocostumeK` (+ objeto com "costumeK", `SCP_costumeK`)
  → ref na lista de UI; `DC_WAD` 0x9000c conta objetos. `ferramentas/costumeimages.py` clona o
  grupo do traje 7 para um índice novo. Aplicar no base e no `DLC/DLC6` (só shaders diferem).
- Imagem da Odisseia (2026-11-22): `costumes/dark_odyssey/imagem_menu.py` repinta a imagem OFICIAL do Kratos
  padrão (pose/posição corretas) por partes: `POLIGONOS_KRATOS` (ombreira, cinto, saia, braçadeiras, lâminas,
  botas, em pixels) + pele/tatuagem pela cor (`mascaras_kratos`, reaproveitada pelo General); cores da paleta
  de recolorir.py com a luminância relativa à pele. Antes: recorte do print do menu (`referencias/dark_odyssey/print_menu_v0.2.png`)
  com GrabCut — `costumes/dark_odyssey/recortar_print.py` (precisa opencv-python-headless,
  rodar sem `-I`). O print é da v0.2 (lâminas escuras); refazer com um print da versão atual.
- Teste rápido: `costumes/god_armor/instalar_teste.py` grava `mods/GoW3 Costumes - Teste slot novo`
  (mesma geração do build, sem deltas). Não deixar ativo junto com o mod do instalador.
- Geração: `ferramentas/trajes.py` (`arquivos_traje`, `compartilhados(ids)`); dados de jogo do traje
  em `costume.json` (`bonus`, `textos_jogo` por idioma = nome + linhas da descrição, `imagem_menu`).

## Estrutura

```
referencias/      imagens e mods de inspiração (por visual)
ferramentas/      wad.py, extrair_texturas.py, dds.py, reempacotar.py, build.py
original/         WADs e texturas extraídas do jogo (não versionado)
costumes/<id>/    costume.json (nomes/descrição por idioma), recolorir.py, texturas/ (geradas)
instalador/       Instalador.cs (instalador .exe, compilado pelo build), LEIA-ME.txt
build/            WAD de teste e pacote de distribuição (não versionado)
```

## Fluxo

```
python -I ferramentas/extrair_texturas.py original/wad/R_HERO00.WAD original/R_HERO00
python -I costumes/dark_odyssey/recolorir.py
python -I costumes/god_armor/texturas_armadura.py
python -I ferramentas/build.py            # trajes de build.TRAJES -> dist/GoW3_Costumes_v<versão>.zip
```

O pacote **não contém arquivos do jogo**. Cada arquivo de saída é um **delta** (`ferramentas/delta.py`,
`dados/<hash>.gw3d`: operações "copiar trecho do arquivo original do usuário" + literais com os
bytes novos; aceita inserções, ex. malha maior, mensagens, objetos novos). `dados/manifest.json`:
`trajes` (ordem = ordem dos slots; `arquivos` com `fonte`, `destino` ['slot' = R_HERO<índice>],
`delta`, SHA-256 da fonte e do resultado) e `compartilhados[<ids unidos por +>]` (R_PERM, R_LANG_*,
COSTUMEIMAGES, os de DLC6 `opcional`) — um conjunto por combinação de trajes (2^n−1).
O instalador mantém UM mod `mods/GoW3 Costumes` (marcador `gow3costume.json` com `ids`); instalar/
remover recalcula tudo a partir dos originais; remove pastas do instalador antigo. Ajustes
não-textura do traje: `costumes/<id>/pos_wad.py` (god_armor troca a malha).
**Instalador = `.exe` de verdade** (o usuário não deve rodar scripts: o Windows bloqueia .ps1):
`instalador/Instalador.cs` (WinForms, C# 5, .NET 4 que já vem no Windows) compilado pelo
`build.py` com o `csc.exe` do Windows; `dados/` (manifest + deltas + previews) vão EMBUTIDOS como
recursos `dados/<arquivo>`; ícone = recorte da imagem do menu da Odisseia. Pacote = zip com
`GoW3 Costumes <versão>.exe` + `LEIA-ME.txt`. Janela: pasta do jogo (SpartanPort, detectada e com
"Procurar..."), lista de visuais com caixas (marcados = conjunto desejado), "Instalar / atualizar",
"Remover tudo", "Gerar arquivos para PS4...". Teste sem janela:
`"GoW3 Costumes X.exe" --acao instalar|remover|ps4 --ids <id>[,id]|todos [--spartan X] [--jogo X] [--mods X] [--saida X] [--sim]`.

## Roadmap / ideias

0. **v1.0.0 (2026-11-20)**: pacote só com `dark_odyssey` (lâminas incluídas);
   `god_armor` fora (em desenvolvimento) — `build.TRAJES`. O instalador SEMPRE pede a pasta do
   jogo (pasta do SpartanPort, sugerindo a detectada; `game_dir`/mods vêm do settings.json dele);
   no PS4 pede a pasta com os arquivos do jogo. Mod de teste removido do SpartanPort (jogo limpo).
1. Testar no jogo: Odisseia (especular da ombreira reduzido), Armadura v4, pacote v1.0.0.
1b. `R_W_CESTUS0..4` (Manoplas de Nemeia) têm materiais `head_sw0..2`/`chest_sw0..2` com texturas
   de pele próprias, mas com OUTRO layout de UV (outro modelo do Kratos); materiais iguais aparecem
   em WADs de fases (GAZ500, GAZ600, OLY800, ICA200, HDS025, R_POS*) → provavelmente Kratos de cenas
   específicas, não o do jogador. Não alterado; conferir no jogo se o visual muda com as Manoplas.
2. ~~Lâminas opcionais~~ descartado: lâminas fazem parte da Odisseia.
3. Pesquisar **slot novo** (`R_HERO09`) sem substituir trajes: lista de trajes fixa no
   eboot (`R_HERO00..08`) → exige patch de código (patches XML do SpartanPort / GoldHEN no PS4),
   entrada no menu (`SHELL.WAD`), imagem (`COSTUMEIMAGES.WAD`) e textos (`R_LANG_*.WAD`).
4. Nomes dos visuais dentro do jogo (menu de trajes) em PT/EN, e depois outros idiomas.
5. Armadura do Deus da Guerra (ver acima).
6. Possível: ajustar mapas de brilho para o dourado parecer metal.
