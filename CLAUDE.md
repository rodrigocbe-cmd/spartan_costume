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
  **As lâminas douradas fazem parte do conjunto da Odisseia (decisão do usuário): instalam junto,
  não são item separado.** No jogo as armas são globais (ficam douradas em qualquer traje).
  (Itens sem slot continuam suportados: `"slot": false` no costume.json.)
- Especular do fleece (`TX2E5E7D75`) × 0,6: ombreira dourada estava estourada no jogo.
- Script: `costumes/dark_odyssey/recolorir.py` (máscaras, caixas/polígonos UV e paleta).
- Pendente: texturas azuladas `TX60366B5B`/`TXBEB53958` (função desconhecida, não alteradas),
  preview com print real do jogo, conferir lâminas no jogo.

### Armadura do Deus da Guerra / God of War Armor (v1 completa instalada no slot 10 — aguardando teste)
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
- Imagem da Odisseia: recorte do print do menu (`referencias/dark_odyssey/print_menu_v0.2.png`)
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
python -I ferramentas/build.py            # trajes de build.TRAJES -> GoW3_Costumes_v<versão>.zip (raiz do projeto)
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
