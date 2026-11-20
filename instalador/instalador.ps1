# GoW III Costumes - instalador / installer
# Adiciona ou remove visuais (costumes) do God of War III Remastered.
# SpartanPort (PC): instala como mod na pasta "mods" do SpartanPort.
# PS4: gera o arquivo WAD para copiar para o console.
#
# Uso interativo: duplo clique em "Instalar.bat".
# Uso por linha de comando (opcional):
#   instalador.ps1 -Acao instalar -Costume dark_odyssey -Slot R_HERO00 [-SpartanDir X] [-GameDir X] [-ModsDir X]
#   instalador.ps1 -Acao remover  -Costume dark_odyssey [-ModsDir X]
#   instalador.ps1 -Acao ps4      -Costume dark_odyssey -Slot R_HERO00 [-GameDir X] [-Saida X]
param(
    [string]$Acao = '',
    [string]$Costume = '',
    [string]$Slot = '',
    [string]$SpartanDir = '',
    [string]$GameDir = '',
    [string]$ModsDir = '',
    [string]$Saida = '',
    [switch]$Sim
)

$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
$Utf8 = New-Object System.Text.UTF8Encoding($false)
$Marcador = 'gow3costume.json'

# ---------------------------------------------------------------- idioma
$Lang = 'en'
if ((Get-Culture).Name -like 'pt*' -or (Get-UICulture).Name -like 'pt*') { $Lang = 'pt' }

$Textos = @{
 pt = @{
  titulo = 'GoW III Costumes - Instalador de visuais'
  menu = "`n  [1] Instalar visual (SpartanPort)`n  [2] Remover visual (SpartanPort)`n  [3] Gerar arquivos para PS4`n  [0] Sair`n"
  opcao = 'Escolha uma opcao'
  escolha_costume = 'Escolha o visual'
  slots = "Em qual slot do Kratos o visual deve entrar?`n  R_HERO00 = Kratos padrao (aparece sempre, sem escolher traje)`n  R_HERO01..R_HERO08 = trajes extras do menu de trajes"
  slot_prompt = 'Slot (Enter = {0})'
  slot_invalido = 'Slot invalido. Use R_HERO00 a R_HERO08.'
  achar_spartan = 'Pasta do SpartanPort nao encontrada. Selecione a pasta onde esta o SpartanPort.exe.'
  achar_jogo = 'Pasta do jogo nao encontrada. Selecione a pasta do jogo (a que tem eboot.bin).'
  spartan = 'SpartanPort: {0}'
  jogo = 'Jogo: {0}'
  mods = 'Pasta de mods: {0}'
  sem_wad = 'Arquivo original nao encontrado: {0}'
  montando = 'Montando {0} a partir do seu jogo...'
  hash_dif = 'AVISO: a textura {0} do seu jogo e diferente da esperada (versao diferente do jogo?).'
  continuar = 'Continuar mesmo assim? (s/n)'
  cancelado = 'Cancelado.'
  ok_inst = 'Instalado! "{0}" foi adicionado como mod em:'
  ok_inst2 = 'Abra o SpartanPort, aba Mods, e confira se o mod esta ativado. Para remover, use a opcao [2] ou desative no launcher.'
  ja_inst = '"{0}" ja esta instalado (slot {1}). Sera reinstalado.'
  conflito = 'AVISO: o mod "{0}" tambem substitui {1}. No SpartanPort, o mod mais abaixo na lista vence.'
  nada_inst = 'Nenhum visual deste pacote esta instalado.'
  removido = 'Removido: {0}'
  ps4_ok = 'Arquivo para PS4 gerado em:'
  ps4_info = "Copie a pasta EXEC para o PS4 com um redirecionador de arquivos (ex.: plugin AFR do GoldHEN:`n  /data/GoldHEN/AFR/<ID do jogo>/EXEC/WAD/PS4_LE/). Veja LEIA-ME.txt."
  verif_ok = 'Verificacao: WAD gerado identico ao esperado.'
  verif_dif = 'AVISO: o WAD gerado difere do esperado (jogo de outra versao/regiao). Teste com cuidado.'
  enter = 'Pressione Enter para continuar'
  erro = 'ERRO: {0}'
  sem_dados = "Pasta de dados nao encontrada: {0}`nUse o instalador do pacote (zip) gerado pelo build, extraido em uma pasta - nao a pasta 'instalador' do codigo-fonte."
 }
 en = @{
  titulo = 'GoW III Costumes - Costume installer'
  menu = "`n  [1] Install costume (SpartanPort)`n  [2] Remove costume (SpartanPort)`n  [3] Build files for PS4`n  [0] Exit`n"
  opcao = 'Choose an option'
  escolha_costume = 'Choose the costume'
  slots = "Which Kratos slot should the costume use?`n  R_HERO00 = default Kratos (always shown, no costume selection needed)`n  R_HERO01..R_HERO08 = bonus costumes from the costume menu"
  slot_prompt = 'Slot (Enter = {0})'
  slot_invalido = 'Invalid slot. Use R_HERO00 to R_HERO08.'
  achar_spartan = 'SpartanPort folder not found. Select the folder that contains SpartanPort.exe.'
  achar_jogo = 'Game folder not found. Select the game folder (the one with eboot.bin).'
  spartan = 'SpartanPort: {0}'
  jogo = 'Game: {0}'
  mods = 'Mods folder: {0}'
  sem_wad = 'Original file not found: {0}'
  montando = 'Building {0} from your game files...'
  hash_dif = 'WARNING: texture {0} in your game differs from the expected one (different game version?).'
  continuar = 'Continue anyway? (y/n)'
  cancelado = 'Cancelled.'
  ok_inst = 'Installed! "{0}" was added as a mod in:'
  ok_inst2 = 'Open SpartanPort, Mods tab, and make sure the mod is enabled. To remove it, use option [2] or disable it in the launcher.'
  ja_inst = '"{0}" is already installed (slot {1}). It will be reinstalled.'
  conflito = 'WARNING: mod "{0}" also replaces {1}. In SpartanPort, the lower mod in the list wins.'
  nada_inst = 'No costume from this package is installed.'
  removido = 'Removed: {0}'
  ps4_ok = 'PS4 file built in:'
  ps4_info = "Copy the EXEC folder to the PS4 with a file redirector (e.g. GoldHEN AFR plugin:`n  /data/GoldHEN/AFR/<game ID>/EXEC/WAD/PS4_LE/). See README.txt."
  verif_ok = 'Check: built WAD matches the expected file.'
  verif_dif = 'WARNING: built WAD differs from the expected one (other game version/region). Test carefully.'
  enter = 'Press Enter to continue'
  erro = 'ERROR: {0}'
  sem_dados = "Data folder not found: {0}`nRun the installer from the extracted package (zip), not from the source 'instalador' folder."
 }
}
function S($k) { return $Textos[$Lang][$k] }
function Pausa { if (-not $Acao) { [void](Read-Host (S 'enter')) } }

# ---------------------------------------------------------------- pastas
function Escolher-Pasta($msg) {
    Write-Host $msg -ForegroundColor Yellow
    Add-Type -AssemblyName System.Windows.Forms
    $d = New-Object System.Windows.Forms.FolderBrowserDialog
    $d.Description = $msg
    if ($d.ShowDialog() -eq 'OK') { return $d.SelectedPath }
    throw (S 'cancelado')
}

function Achar-Spartan {
    if ($SpartanDir -and (Test-Path (Join-Path $SpartanDir 'SpartanPort.exe'))) { return $SpartanDir }
    $cand = @()
    $p = $Raiz
    for ($i = 0; $i -lt 4 -and $p; $i++) { $cand += $p; $p = Split-Path -Parent $p }
    foreach ($b in @('C:\Games', 'D:\Games', 'E:\Games', "$env:USERPROFILE\Games", "$env:USERPROFILE\Downloads")) {
        if (Test-Path $b) { $cand += (Get-ChildItem $b -Directory -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }) }
    }
    foreach ($c in $cand) { if (Test-Path (Join-Path $c 'SpartanPort.exe')) { return $c } }
    if ($Acao) { throw (S 'achar_spartan') }
    $sel = Escolher-Pasta (S 'achar_spartan')
    if (-not (Test-Path (Join-Path $sel 'SpartanPort.exe'))) { throw (S 'achar_spartan') }
    return $sel
}

function Ler-Settings($sp) {
    $f = Join-Path $sp 'settings.json'
    if (Test-Path $f) {
        try { return ([IO.File]::ReadAllText($f) | ConvertFrom-Json) } catch { }
    }
    return $null
}

function Achar-Jogo($cfg) {
    $c = @()
    if ($GameDir) { $c += $GameDir }
    if ($cfg -and $cfg.game_dir) { $c += $cfg.game_dir }
    foreach ($g in $c) { if (Test-Path (Join-Path $g 'EXEC\WAD\PS4_LE')) { return $g } }
    if ($Acao) { throw (S 'achar_jogo') }
    $sel = Escolher-Pasta (S 'achar_jogo')
    if (-not (Test-Path (Join-Path $sel 'EXEC\WAD\PS4_LE'))) { throw (S 'achar_jogo') }
    return $sel
}

function Achar-Mods($sp, $cfg) {
    if ($ModsDir) { return $ModsDir }
    if ($cfg -and $cfg.mods_dir) { return $cfg.mods_dir }
    return (Join-Path $sp 'mods')
}

# ---------------------------------------------------------------- costumes do pacote
function Listar-Costumes {
    $l = @()
    $dados = Join-Path $Raiz 'dados'
    if (-not (Test-Path $dados)) { throw ((S 'sem_dados') -f $dados) }
    Get-ChildItem $dados -Directory | ForEach-Object {
        $m = Join-Path $_.FullName 'manifest.json'
        if (Test-Path $m) {
            $j = [IO.File]::ReadAllText($m, $Utf8) | ConvertFrom-Json
            $j | Add-Member -NotePropertyName pasta -NotePropertyValue $_.FullName
            $l += $j
        }
    }
    return $l
}
function Nome($c) { return $c.nomes.$Lang }

function Escolher-Costume($lista) {
    if ($Costume) {
        $c = $lista | Where-Object { $_.id -eq $Costume }
        if (-not $c) { throw "costume '$Costume'?" }
        return $c
    }
    if ($lista.Count -eq 1) { return $lista[0] }
    Write-Host (S 'escolha_costume')
    for ($i = 0; $i -lt $lista.Count; $i++) { Write-Host ("  [{0}] {1}" -f ($i + 1), (Nome $lista[$i])) }
    $n = [int](Read-Host (S 'opcao'))
    return $lista[$n - 1]
}

function Escolher-Slot($c) {
    if ($Slot) { $s = $Slot.ToUpper() }
    else {
        Write-Host ""
        Write-Host (S 'slots')
        $s = (Read-Host ((S 'slot_prompt') -f $c.slot_padrao)).Trim().ToUpper()
        if (-not $s) { $s = $c.slot_padrao }
    }
    if ($s -match '^0?\d$') { $s = 'R_HERO0' + $s.Substring($s.Length - 1) }
    if ($s -notmatch '^R_HERO0[0-8]$') { throw (S 'slot_invalido') }
    return $s
}

# ---------------------------------------------------------------- WAD
function Sha256($bytes, $off, $len) {
    $h = [Security.Cryptography.SHA256]::Create()
    return ([BitConverter]::ToString($h.ComputeHash($bytes, $off, $len)) -replace '-', '').ToLower()
}

function Entradas-Wad($d) {
    # Cabeçalho de 0x40 bytes: u32 tag, u32 tamanho, char nome[0x38]; dados alinhados a 16.
    $r = @{}
    $off = 0
    while ($off + 0x40 -le $d.Length) {
        $tam = [BitConverter]::ToUInt32($d, $off + 4)
        $fim = [Array]::IndexOf($d, [byte]0, $off + 8)
        if ($fim -lt 0 -or $fim -gt $off + 0x40) { $fim = $off + 0x40 }
        $nome = [Text.Encoding]::ASCII.GetString($d, $off + 8, $fim - $off - 8)
        if ($nome -like '*.dds') { $r[$nome] = @{ dados = $off + 0x40; tam = [int]$tam } }
        $off = ($off + 0x40 + $tam + 15) -band (-bnot 15)
    }
    return $r
}

function Montar-Wad($c, $w, $jogo) {
    # $w = uma entrada de $c.wads: base (WAD original do jogo), destino, texturas, sha256_resultado
    $src = Join-Path $jogo ("EXEC\WAD\PS4_LE\" + $w.base)
    if (-not (Test-Path $src)) { throw ((S 'sem_wad') -f $src) }
    Write-Host ((S 'montando') -f $w.base)
    $d = [IO.File]::ReadAllBytes($src)
    $ent = Entradas-Wad $d
    $avisos = @()
    foreach ($tx in $w.texturas) {
        $e = $ent[$tx.nome]
        if (-not $e) { throw "textura $($tx.nome)?" }
        # procura o cabeçalho "DDS " no início da entrada
        $dds = -1
        for ($i = $e.dados; $i -lt $e.dados + 0x200; $i++) {
            if ($d[$i] -eq 0x44 -and $d[$i + 1] -eq 0x44 -and $d[$i + 2] -eq 0x53 -and $d[$i + 3] -eq 0x20) { $dds = $i; break }
        }
        if ($dds -lt 0) { throw "DDS $($tx.nome)?" }
        $ini = $dds + 128
        if ($ini + $tx.tamanho -gt $e.dados + $e.tam) { throw "tamanho $($tx.nome)" }
        if ((Sha256 $d $ini $tx.tamanho) -ne $tx.sha256_original) { $avisos += $tx.nome }
        $novo = [IO.File]::ReadAllBytes((Join-Path $c.pasta $tx.arquivo))
        [Array]::Copy($novo, 0, $d, $ini, $novo.Length)
    }
    if ($avisos.Count -gt 0) {
        foreach ($a in $avisos) { Write-Host ((S 'hash_dif') -f $a) -ForegroundColor Yellow }
        if (-not $Sim) {
            if ($Acao) { throw (S 'cancelado') }
            $r = Read-Host (S 'continuar')
            if ($r -notmatch '^[sSyY]') { throw (S 'cancelado') }
        }
    }
    if ((Sha256 $d 0 $d.Length) -eq $w.sha256_resultado) { Write-Host (S 'verif_ok') -ForegroundColor Green }
    else { Write-Host (S 'verif_dif') -ForegroundColor Yellow }
    return , $d
}

function Destino($w, $slot) {
    if ($w.destino -eq 'slot') { return "$slot.WAD" }
    return $w.destino
}

function Gravar-Wads($c, $slot, $jogo, $wdir) {
    # monta e grava todos os WADs do visual; devolve os nomes gravados
    New-Item -ItemType Directory -Force $wdir | Out-Null
    $nomes = @()
    foreach ($w in $c.wads) {
        $d = Montar-Wad $c $w $jogo
        $dest = Destino $w $slot
        [IO.File]::WriteAllBytes((Join-Path $wdir $dest), $d)
        $nomes += $dest
    }
    return $nomes
}

# ---------------------------------------------------------------- mods.json do SpartanPort
function Limpar-ModsJson($sp, $nomePasta) {
    $f = Join-Path $sp 'mods.json'
    if (-not (Test-Path $f)) { return }
    try {
        $j = [IO.File]::ReadAllText($f) | ConvertFrom-Json
        $j.order = @($j.order | Where-Object { $_ -ne $nomePasta })
        $j.disabled = @($j.disabled | Where-Object { $_ -ne $nomePasta })
        [IO.File]::WriteAllText($f, ($j | ConvertTo-Json -Depth 5), $Utf8)
    } catch { }
}

function Instalados($mods) {
    $l = @()
    if (Test-Path $mods) {
        Get-ChildItem $mods -Directory | ForEach-Object {
            $m = Join-Path $_.FullName $Marcador
            if (Test-Path $m) {
                $j = [IO.File]::ReadAllText($m, $Utf8) | ConvertFrom-Json
                $j | Add-Member -NotePropertyName pasta -NotePropertyValue $_.FullName
                $l += $j
            }
        }
    }
    return $l
}

# ---------------------------------------------------------------- ações
function Instalar {
    $sp = Achar-Spartan; $cfg = Ler-Settings $sp
    $jogo = Achar-Jogo $cfg; $mods = Achar-Mods $sp $cfg
    Write-Host ((S 'spartan') -f $sp); Write-Host ((S 'jogo') -f $jogo); Write-Host ((S 'mods') -f $mods)
    $c = Escolher-Costume (Listar-Costumes)
    $s = Escolher-Slot $c
    $nome = Nome $c
    # reinstalação: remove a instalação anterior deste visual
    foreach ($i in (Instalados $mods)) {
        if ($i.id -eq $c.id) {
            Write-Host ((S 'ja_inst') -f $nome, $i.slot) -ForegroundColor Yellow
            Remove-Item -Recurse -Force -LiteralPath $i.pasta
            Limpar-ModsJson $sp (Split-Path -Leaf $i.pasta)
        }
    }
    # aviso de conflito com outros mods que usam os mesmos arquivos
    if (Test-Path $mods) {
        Get-ChildItem $mods -Directory | ForEach-Object {
            $outro = $_
            foreach ($w in $c.wads) {
                $dest = Destino $w $s
                if (Test-Path (Join-Path $outro.FullName "EXEC\WAD\PS4_LE\$dest")) {
                    Write-Host ((S 'conflito') -f $outro.Name, $dest) -ForegroundColor Yellow
                }
            }
        }
    }
    $pasta = Join-Path $mods ("GoW3 Costumes - " + $nome)
    $wdir = Join-Path $pasta 'EXEC\WAD\PS4_LE'
    [void](Gravar-Wads $c $s $jogo $wdir)
    $mj = [ordered]@{ name = $nome; author = $c.autor; version = $c.versao; description = ($c.descricao.$Lang + " [$s]") }
    [IO.File]::WriteAllText((Join-Path $pasta 'mod.json'), ($mj | ConvertTo-Json), $Utf8)
    $pv = Join-Path $c.pasta 'preview.png'
    if (Test-Path $pv) { Copy-Item $pv (Join-Path $pasta 'preview.png') }
    $mk = [ordered]@{ id = $c.id; slot = $s; versao = $c.versao }
    [IO.File]::WriteAllText((Join-Path $pasta $Marcador), ($mk | ConvertTo-Json), $Utf8)
    Write-Host ""
    Write-Host ((S 'ok_inst') -f $nome) -ForegroundColor Green
    Write-Host "  $pasta"
    Write-Host (S 'ok_inst2')
}

function Remover {
    $mods = $ModsDir; $sp = $null
    if (-not $mods) { $sp = Achar-Spartan; $mods = Achar-Mods $sp (Ler-Settings $sp) }
    elseif ($SpartanDir) { $sp = $SpartanDir }
    $inst = @(Instalados $mods)
    if ($Costume) { $inst = @($inst | Where-Object { $_.id -eq $Costume }) }
    if ($inst.Count -eq 0) { Write-Host (S 'nada_inst'); return }
    $alvo = $inst
    if (-not $Costume -and $inst.Count -gt 1) {
        for ($i = 0; $i -lt $inst.Count; $i++) { Write-Host ("  [{0}] {1} ({2})" -f ($i + 1), (Split-Path -Leaf $inst[$i].pasta), $inst[$i].slot) }
        $n = [int](Read-Host (S 'opcao'))
        $alvo = @($inst[$n - 1])
    }
    foreach ($i in $alvo) {
        Remove-Item -Recurse -Force -LiteralPath $i.pasta
        if ($sp) { Limpar-ModsJson $sp (Split-Path -Leaf $i.pasta) }
        Write-Host ((S 'removido') -f (Split-Path -Leaf $i.pasta)) -ForegroundColor Green
    }
}

function Gerar-PS4 {
    $cfg = $null
    if (-not $GameDir) { try { $cfg = Ler-Settings (Achar-Spartan) } catch { } }
    $jogo = Achar-Jogo $cfg
    $c = Escolher-Costume (Listar-Costumes)
    $s = Escolher-Slot $c
    $out = $Saida
    if (-not $out) { $out = Join-Path $Raiz ("PS4 - " + (Nome $c)) }
    $wdir = Join-Path $out 'EXEC\WAD\PS4_LE'
    $nomes = Gravar-Wads $c $s $jogo $wdir
    Write-Host ""
    Write-Host (S 'ps4_ok') -ForegroundColor Green
    foreach ($n in $nomes) { Write-Host "  $wdir\$n" }
    Write-Host (S 'ps4_info')
}

# ---------------------------------------------------------------- principal
function Executar($a) {
    try {
        switch ($a) {
            'instalar' { Instalar }
            'remover' { Remover }
            'ps4' { Gerar-PS4 }
            default { throw "acao '$a'?" }
        }
        return $true
    } catch {
        Write-Host ((S 'erro') -f $_.Exception.Message) -ForegroundColor Red
        if ($env:GOW3_DEBUG) { Write-Host $_.ScriptStackTrace }
        return $false
    }
}

if ($Acao) {
    if (-not (Executar $Acao.ToLower())) { exit 1 }
    exit 0
}

while ($true) {
    Clear-Host
    Write-Host (S 'titulo') -ForegroundColor Cyan
    Write-Host ('=' * (S 'titulo').Length)
    try { $lista = Listar-Costumes }
    catch {
        Write-Host ((S 'erro') -f $_.Exception.Message) -ForegroundColor Red
        [void](Read-Host (S 'enter'))
        exit 1
    }
    foreach ($c in $lista) { Write-Host ("  * {0} v{1}" -f (Nome $c), $c.versao) }
    Write-Host (S 'menu')
    $o = Read-Host (S 'opcao')
    switch ($o) {
        '1' { [void](Executar 'instalar'); Pausa }
        '2' { [void](Executar 'remover'); Pausa }
        '3' { [void](Executar 'ps4'); Pausa }
        '0' { exit 0 }
    }
}
