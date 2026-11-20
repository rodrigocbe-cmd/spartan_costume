# GoW III Costumes

Visuais (costumes) para **God of War III Remastered**. Foco principal: o port de PC
**SpartanPort**; tudo deve continuar instalável também no **PS4** (mesmo formato `PS4_LE`).

## Instruções do usuário (sempre seguir)

- Visuais devem ser **adicionados/removíveis** por um instalador; o jogo original nunca é alterado.
- Preferência: **não substituir visuais existentes**. Enquanto não houver slot novo
  (ver Roadmap), o instalador deixa o usuário escolher o slot (padrão: `R_HERO00`).
- **Idioma:** se o jogo/sistema estiver em português, os nomes dos visuais aparecem em
  português; em qualquer outro idioma, em inglês. **Outras traduções serão adicionadas
  no futuro** — manter todos os textos em tabelas por idioma (`nomes`/`descricao` em
  `costume.json`, tabela `$Textos` em `instalador/instalador.ps1`), nunca fixos no código.
- Pode reorganizar pastas e arquivos conforme o projeto precisar.
- Responder ao usuário em português.

## Visuais

### Odisseia Sombria / Dark Odyssey (em andamento — v0.3.0 instalada, aguardando teste)
- Base: Kratos padrão do GoW III (`R_HERO00.WAD`), **só recoloração** — malha, esqueleto,
  normal maps e animações intactos.
- **Regra de cores (pedido do usuário):** usar o modelo do GoW II
  (`referencias/dark_odyssey/gow2_modelo/`, texturas + OBJ) para saber ONDE vai cada cor,
  e as cores atuais do **GoW Ragnarok** (`referencias/dark_odyssey/ragnarok_*.webp`).
- Pele cinza-carvão (~`#2c2a24`), tatuagem dourada (~`#c48a3a`), **olhos brancos**.
- Roupas/armadura: saia preta com grega dourada; ombreira, braceletes, cinto, grevas/botas
  e asas de Hermes **dourados** (âmbar ~`#ba802e`); braçadeiras dos antebraços douradas
  (elos claros sobre fundo dourado escuro, como no modelo do GoW II).
- **Olhos todo brancos** (sem íris/pupila; brilho opcional, não feito). O olho usa 3 texturas:
  `innereye_m` → cor do corpo `TX27CF5CC1`; `outereye_m` → `TX60366B5B` (azulada) + normal
  `TX27586F46` (relevo da íris foi aplainado). Disco do olho na UV: centro (0.82, 0.30).
- Texturas azuladas `TX60366B5B` (corpo) e `TXBEB53958` (cabeça) = versão "pálida" da pele
  usada também por `chest_m`/`head_m`; são recoloridas mantendo a razão de brilho.
- **Lâminas do Exílio** (`R_W_EXPLOSIVE5`, a maior parte do jogo e o menu): cor `TXA4FBD109`
  (lâmina em gancho + cabo de dragão), brilho `TX8EE75C90` (runas vermelhas → laranja-dourado),
  especular `TX7F88879E`. Lâmina toda dourada (uniforme, como no Ragnarok), cabo preto,
  corrente dourada. A troca Atena → Exílio no início do jogo usa esses mesmos WADs
  (única outra cópia das texturas: `R_KRATOSFEAR10`, inimigo — não alterado).
- **Lâmina de Atena** (`R_W_EXPLOSIVE0..4`, início do jogo): `TX888F0896` (cabeça de dragão),
  toda dourada com cabo preto. As armas são globais: valem para todos os trajes.
- Script: `costumes/dark_odyssey/recolorir.py` (máscaras, caixas/polígonos UV e paleta).
- Pendente: texturas azuladas `TX60366B5B`/`TXBEB53958` (função desconhecida, não alteradas),
  preview com print real do jogo, conferir lâminas no jogo.

### Armadura do Deus da Guerra / God of War Armor (futuro)
- Inspirada na armadura do Kratos no **GoW II**.
- Referências: `referencias/god_armor/God of War Armor by _spartan_gamer.jpg` e
  `referencias/god_armor/god_armor_1_1/` (port direto da armadura do GoW II; substitui `R_HERO00.WAD`).

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
- Teste instalado: `mods/GoW3 Costumes - Teste slot novo` (com imagem).
- Pendente: instalador gerenciar um único mod com arquivos compartilhados
  (R_PERM/R_LANG/COSTUMEIMAGES) recalculados a partir dos originais.

## Estrutura

```
referencias/      imagens e mods de inspiração (por visual)
ferramentas/      wad.py, extrair_texturas.py, dds.py, reempacotar.py, build.py
original/         WADs e texturas extraídas do jogo (não versionado)
costumes/<id>/    costume.json (nomes/descrição por idioma), recolorir.py, texturas/ (geradas)
instalador/       instalador.ps1, Instalar.bat, LEIA-ME.txt (copiados para o pacote)
build/            WAD de teste e pacote de distribuição (não versionado)
```

## Fluxo

```
python -I ferramentas/extrair_texturas.py original/wad/R_HERO00.WAD original/R_HERO00
python -I ferramentas/extrair_texturas.py original/wad/R_W_EXPLOSIVE0.WAD original/R_W_EXPLOSIVE0
python -I costumes/dark_odyssey/recolorir.py
python -I ferramentas/build.py dark_odyssey      # -> build/GoW3_Costumes_v<versão>.zip
```

O pacote **não contém arquivos do jogo**: leva só os pixels das texturas alteradas
(`dados/<id>/*.bin` + `manifest.json` com SHA-256 do original e do resultado). O instalador
lê o `R_HERO00.WAD` do usuário, aplica as texturas, confere o hash e grava o mod
(SpartanPort) ou o arquivo para PS4. Teste sem prompts:
`instalador.ps1 -Acao instalar|remover|ps4 -Costume <id> -Slot R_HERO0x -ModsDir X -GameDir X`
(`$env:GOW3_DEBUG=1` mostra a pilha de erros).

## Roadmap / ideias

1. Testar a v0.3.0 (olhos, Lâminas do Exílio) e ajustar. Ombreira esquerda (`TXE90D274D`)
   aparece muito brilhante no jogo (especular) — talvez escurecer.
1b. `R_W_CESTUS0..` (Manoplas de Nemeia) traz cópias próprias das texturas do Kratos
   (cabeça/corpo com outros hashes) → com o Cesto o visual pode voltar ao original. Verificar.
2. Talvez tornar as lâminas opcionais no instalador (são globais).
3. Pesquisar **slot novo** (`R_HERO09`) sem substituir trajes: lista de trajes fixa no
   eboot (`R_HERO00..08`) → exige patch de código (patches XML do SpartanPort / GoldHEN no PS4),
   entrada no menu (`SHELL.WAD`), imagem (`COSTUMEIMAGES.WAD`) e textos (`R_LANG_*.WAD`).
4. Nomes dos visuais dentro do jogo (menu de trajes) em PT/EN, e depois outros idiomas.
5. Armadura do Deus da Guerra (ver acima).
6. Possível: ajustar mapas de brilho para o dourado parecer metal.
