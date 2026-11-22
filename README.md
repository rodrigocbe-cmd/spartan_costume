# GoW III Costumes

Visuais (trajes) novos para o Kratos em **God of War III Remastered**, feitos para o port de PC
**SpartanPort** e também instaláveis no **PS4** (GoldHEN).

Cada visual entra como um **traje novo** no menu de trajes do jogo, depois dos trajes originais.
Nenhum traje do jogo é substituído e os arquivos originais nunca são alterados.

*English summary: new Kratos costumes for God of War III Remastered (SpartanPort PC port and PS4).
Each costume is added as a new entry in the in-game costume menu; no original costume or game file
is replaced. The package contains no game files.*

---

## O que já tem

### Odisseia Sombria (Dark Odyssey) — v1.0.0

O traje do GoW II, com as cores atuais do GoW Ragnarok, feito sobre o Kratos padrão do GoW III
(só recoloração: malha e animações originais).

- Pele cinza-carvão, tatuagem dourada e olhos todo brancos, como no Ragnarok.
- Armadura em preto e dourado, seguindo o desenho do GoW II: saia preta com grega dourada,
  ombreira, cinto, braçadeiras, grevas e botas de Hermes douradas.
- Lâminas de Atena e do Exílio douradas com cabo preto, com fogo, faíscas e rastros dos golpes
  dourados — **só com a Odisseia Sombria**: os outros trajes continuam com as lâminas originais
  (um patch que vem com o mod faz o jogo carregar as lâminas douradas só com esse traje).
- Bônus, como no GoW II: **ataque 2x, dano sofrido 2x, orbes vermelhas 4x**. Os troféus ficam
  desabilitados ao usar o traje, como nos trajes do próprio jogo.
- Nome e descrição no menu de trajes nos **16 idiomas do jogo**, seguindo as frases dos trajes
  oficiais.

### Instalador

- Um único `.exe` com janela; não precisa instalar nada além do jogo.
- Detecta a pasta do SpartanPort (ou deixa escolher com "Procurar..."), instala, atualiza ou remove
  os visuais com um clique.
- Instala como um mod do SpartanPort (`mods/GoW3 Costumes`), que pode ser desativado no launcher.
- Gera a pasta `EXEC` para copiar ao PS4 com um redirecionador de arquivos (ex.: plugin AFR do GoldHEN).
- Textos em português ou inglês, conforme o idioma do Windows.

## Como instalar

1. Baixe `GoW3_Costumes_v1.0.0.zip` e extraia em qualquer pasta.
2. Abra `GoW3 Costumes 1.0.0.exe`. Se o Windows mostrar "O Windows protegeu o computador", clique em
   "Mais informações" > "Executar assim mesmo" (o programa não é assinado).
3. Confira a pasta do jogo (a pasta do SpartanPort, onde está o `SpartanPort.exe`), marque os visuais
   e clique em **Instalar / atualizar**.
4. No SpartanPort, aba Mods, confira se **GoW3 Costumes** está ativado.
5. No jogo: menu **Extras > Seleção de traje**.

Para remover: **Remover tudo** no instalador, ou desative o mod no launcher.
Para PS4: **Gerar arquivos para PS4...** e copie a pasta `EXEC` gerada para
`/data/GoldHEN/AFR/<ID do jogo>/EXEC/`.

Instruções completas: `instalador/LEIA-ME.txt` (também vai dentro do zip).

### Requisitos

- Sua própria cópia de God of War III Remastered (CUSA01623).
- PC: SpartanPort. PS4: GoldHEN com um redirecionador de arquivos.

### Sem arquivos do jogo

O pacote **não contém arquivos do jogo**. Ele leva só as partes novas (texturas, malhas, textos) em
forma de *deltas*: instruções do tipo "copie este trecho do arquivo original" + os bytes novos.
O instalador lê os arquivos originais do seu jogo, monta os arquivos do mod e confere cada resultado
por SHA-256.

---

## O que vem por aí

### Armadura do Deus da Guerra (God of War Armor) — em desenvolvimento

Inspirada na armadura do Kratos no GoW II, com geometria própria:

- Ombreiras de carneiro, peitoral com grega, gola de malha, braçadeiras e grevas douradas e tiras
  de couro na cintura.
- Dourado um pouco gasto, com pátina leve.
- Bônus planejado: **ataque 2x, dano sofrido pela metade, todas as orbes 4x**.
- Situação: peças já aparecem e acompanham o corpo no jogo; faltam ajustes de encaixe, acabamento
  das texturas e a imagem do menu.

### Outros planos

- Imagem nova da Odisseia Sombria no menu de trajes (a atual é de uma versão anterior, com as
  lâminas escuras).
- Mais visuais no futuro, sempre como trajes novos.
- Mais traduções do instalador (hoje: português e inglês).

---

## Para desenvolvedores

```
costumes/<id>/    um visual: costume.json (nomes, descrição, bônus, textos do jogo por idioma),
                  scripts de textura/malha e texturas geradas
ferramentas/      leitura e escrita dos formatos do jogo (WAD, texturas, malhas, esqueleto,
                  textos, imagens do menu, partículas), deltas e o build do pacote
instalador/       Instalador.cs (instalador .exe) e LEIA-ME.txt
referencias/      imagens e modelos usados como referência
original/, build/ arquivos extraídos do jogo e saídas de build (não versionados)
```

Fluxo de build (Python 3 com Pillow, NumPy e SciPy; o instalador é compilado com o `csc.exe` do
.NET Framework que já vem no Windows):

```
python -I ferramentas/extrair_texturas.py original/wad/R_HERO00.WAD original/R_HERO00
python -I costumes/dark_odyssey/recolorir.py
python -I ferramentas/build.py        # -> dist/GoW3_Costumes_v<versão>.zip
```

Os detalhes técnicos descobertos (formato WAD, malhas, esqueleto, lista de trajes, bônus, imagens do
menu) estão anotados em `CLAUDE.md`.
