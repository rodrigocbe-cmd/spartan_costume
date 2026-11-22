"""Gera o pacote de distribuição com todos os visuais (trajes em slots novos).

uso: python -I ferramentas/build.py [--teste] [id1 id2 ...]     (padrão: TRAJES, nessa ordem)

Para cada traje: monta seus WADs (texturas + pos_wad.py, ver trajes.py) e grava um DELTA
(delta.py: "copiar do arquivo original do usuário" + bytes novos) — o pacote não leva arquivos
do jogo. Para cada combinação de trajes instalados, grava os deltas dos arquivos compartilhados
(R_PERM, R_LANG_*, COSTUMEIMAGES). O instalador escolhe a combinação e aplica os deltas.
Saída: build/dist/GoW3 Costumes/ (instalador .exe) e dist/GoW3_Costumes_v<versão>.zip.
"""
import hashlib, itertools, json, os, shutil, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import delta, trajes

RAIZ = trajes.RAIZ
VERSAO = '1.1.0'
PASTA_DIST = 'GoW3 Costumes'
TESTE = False
TRAJES = ['dark_odyssey', 'general_kratos', 'general_kratos_armadura']   # ordem do pacote = ordem dos slots (9, 10, ...)
# (god_armor PAUSADO — deixava o jogo lento quando selecionado; testar com: build.py dark_odyssey god_armor)


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Pacote:
    def __init__(self, ddir):
        self.ddir = ddir
        self.cache_fontes = {}

    def fonte(self, rel):
        if rel not in self.cache_fontes:
            self.cache_fontes[rel] = trajes.ler_jogo(rel)
        return self.cache_fontes[rel]

    def item(self, fonte, destino, novo, **extra):
        orig = self.fonte(fonte)
        d = delta.criar(orig, novo)
        arq = sha(d)[:16] + '.gw3d'
        p = os.path.join(self.ddir, arq)
        if not os.path.exists(p):
            open(p, 'wb').write(d)
        return dict(fonte=fonte, destino=destino, delta=arq, sha256_fonte=sha(orig),
                    sha256_resultado=sha(novo), tamanho=len(novo), **extra)


CSC = r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'


def icone(destino):
    """Ícone do instalador: cabeça/tronco da imagem do menu da Odisseia Sombria."""
    from PIL import Image
    im = Image.open(os.path.join(RAIZ, 'costumes', 'dark_odyssey', 'menu', 'imagem_menu.png')).convert('RGBA')
    caixa = im.getbbox()
    x0, y0, x1, _ = caixa
    lado = x1 - x0
    q = im.crop((x0, y0, x1, y0 + lado))
    q.save(destino, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def compilar_instalador(dist, ddir):
    """Compila instalador/Instalador.cs (WinForms, .NET 4 do Windows) com os dados como recursos."""
    import subprocess
    exe = os.path.join(dist, f'GoW3 Costumes {VERSAO}.exe')
    ico = os.path.join(RAIZ, 'build', 'instalador.ico')
    icone(ico)
    args = [CSC, '/nologo', '/target:winexe', '/optimize+', '/codepage:65001', '/platform:anycpu',
            '/r:System.Web.Extensions.dll', '/r:System.Windows.Forms.dll', '/r:System.Drawing.dll',
            '/win32icon:' + ico, '/out:' + exe]
    for f in sorted(os.listdir(ddir)):
        args.append('/resource:%s,dados/%s' % (os.path.join(ddir, f), f))
    args.append(os.path.join(RAIZ, 'instalador', 'Instalador.cs'))
    r = subprocess.run(args, capture_output=True, text=True, encoding='cp850', errors='replace')
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit('falha ao compilar o instalador')
    print('Instalador:', exe)
    return exe


def main(ids):
    dist = os.path.join(RAIZ, 'build', 'dist', PASTA_DIST)
    if os.path.isdir(dist):
        shutil.rmtree(dist)
    ddir = os.path.join(dist, 'dados')
    os.makedirs(ddir)
    pk = Pacote(ddir)

    lista = []
    for cid in ids:
        m = trajes.meta(cid)
        arqs = []
        for fonte, dest, dados in trajes.arquivos_traje(cid):
            print(cid, fonte, '->', dest, flush=True)
            arqs.append(pk.item(fonte, dest, dados))
        prev = os.path.join(m['_dir'], 'preview.png')
        if os.path.exists(prev):
            shutil.copy(prev, os.path.join(ddir, 'preview_%s.png' % cid))
        lista.append(dict(id=cid, slot=m['slot'], patches=trajes.patches(cid), nomes=m['nomes'], descricao=m['descricao'], autor=m.get('autor', ''),
                          preview=('preview_%s.png' % cid) if os.path.exists(prev) else '', arquivos=arqs))

    comp = {}
    slots = trajes.com_slot(ids)
    for n in range(1, len(slots) + 1):
        for sub in itertools.combinations(slots, n):
            chave = '+'.join(sub)
            print('compartilhados:', chave, flush=True)
            comp[chave] = [pk.item(f, d, dados, opcional=op) for f, d, dados, op in trajes.compartilhados(list(sub))]

    manifest = dict(versao=VERSAO, primeiro_indice=trajes.PRIMEIRO_INDICE, trajes=lista, compartilhados=comp)
    json.dump(manifest, open(os.path.join(ddir, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    compilar_instalador(dist, ddir)
    shutil.rmtree(ddir)                                   # dados vão embutidos no .exe
    shutil.copy(os.path.join(RAIZ, 'instalador', 'LEIA-ME.txt'), dist)

    # release: dist/ (guarda o histórico; nunca apaga versões); teste (--teste): build/teste/
    destino = os.path.join(RAIZ, 'build', 'teste') if TESTE else os.path.join(RAIZ, 'dist')
    os.makedirs(destino, exist_ok=True)
    zp = os.path.join(destino, f'{PASTA_DIST} v{VERSAO}.zip'.replace(' ', '_'))
    if os.path.exists(zp):
        os.remove(zp)
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for r, _, fs in os.walk(dist):
            for f in fs:
                p = os.path.join(r, f)
                z.write(p, os.path.relpath(p, os.path.dirname(dist)))
    print('Pacote:', zp, f'({os.path.getsize(zp) / 1e6:.1f} MB)')


if __name__ == '__main__':
    TESTE = '--teste' in sys.argv
    main([a for a in sys.argv[1:] if not a.startswith('--')] or TRAJES)
