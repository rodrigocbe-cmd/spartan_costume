"""Gera o pacote de distribuição de um visual (costume).

uso: python -I ferramentas/build.py dark_odyssey

Para cada WAD listado em costumes/<id>/costume.json ("wads"):
1. Codifica os PNGs de costumes/<id>/texturas/<texturas>/ (DXT + mipmaps) sobre o WAD original.
2. Grava o WAD completo em build/<id>/ (só para teste local; NÃO é distribuído).
3. Extrai só os pixels das texturas alteradas para o pacote (deduplicados por hash).
Depois monta build/dist/<pasta>/ com o instalador e compacta em build/<pasta>_v<versão>.zip.
O WAD do jogo é lido da cópia do próprio usuário na instalação.
"""
import hashlib, json, os, shutil, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reempacotar import rebuild
from extrair_texturas import textures
import importlib.util
import wad as wadmod

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VERSAO = '0.4.0'
PASTA_DIST = 'GoW3 Costumes'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def trechos(orig, novo, ddir):
    """Entradas cujos dados mudaram → trechos (nome, ocorrência, deslocamento, tamanho).
    Texturas: só os pixels (depois do cabeçalho DDS). Outras entradas: os dados inteiros."""
    out = []
    vistos = {}
    eo = wadmod.parse(orig)
    for e in eo:
        k = (e['name'], e['tag'])
        oc = vistos.get(k, 0); vistos[k] = oc + 1
        a = orig[e['data_off']:e['data_off'] + e['size']]
        b = novo[e['data_off']:e['data_off'] + e['size']]
        if a == b:
            continue
        ini = 0
        dds = a.find(b'DDS ', 0, 0x200) if e['tag'] == 0xd0001 else -1
        if dds >= 0:
            ini = dds + 128
        pa, pb = a[ini:], b[ini:]
        h = sha(pb)
        arq = h[:16] + '.bin'
        if not os.path.exists(os.path.join(ddir, arq)):
            open(os.path.join(ddir, arq), 'wb').write(pb)
        out.append(dict(nome=e['name'], tag=e['tag'], ocorrencia=oc, desloc=ini, tamanho=len(pb),
                        arquivo=arq, sha256_original=sha(pa), sha256_novo=h))
    return out


def main(cid):
    cdir = os.path.join(RAIZ, 'costumes', cid)
    meta = json.load(open(os.path.join(cdir, 'costume.json'), encoding='utf-8'))

    dist = os.path.join(RAIZ, 'build', 'dist', PASTA_DIST)
    if os.path.isdir(dist):
        shutil.rmtree(dist)
    ddir = os.path.join(dist, 'dados', cid)
    os.makedirs(ddir)

    pos = None
    hook = os.path.join(cdir, 'pos_wad.py')
    if os.path.exists(hook):
        spec = importlib.util.spec_from_file_location('pos_wad', hook)
        pos = importlib.util.module_from_spec(spec); spec.loader.exec_module(pos)
    wads = []
    for w in meta['wads']:
        base = os.path.join(RAIZ, 'original', 'wad', w['base'])
        assert os.path.exists(base), f'copie {w["base"]} do jogo para original/wad/'
        wad_out = os.path.join(RAIZ, 'build', cid, w['base'])
        print('Reempacotando', w['base'])
        rebuild(base, os.path.join(cdir, 'texturas', w['texturas']), wad_out, verbose=False)
        if pos is not None:
            dados = pos.processar(w['base'][:-4], open(wad_out, 'rb').read())
            open(wad_out, 'wb').write(dados)
        orig, novo = open(base, 'rb').read(), open(wad_out, 'rb').read()
        assert len(orig) == len(novo)
        tex = trechos(orig, novo, ddir)
        print(f'  {len(tex)} trechos alterados')
        wads.append(dict(base=w['base'], destino=w['destino'], sha256_resultado=sha(novo), trechos=tex))

    manifest = dict(id=cid, versao=VERSAO, nomes=meta['nomes'], descricao=meta['descricao'],
                    autor=meta.get('autor', ''), slot_padrao=meta['slot_padrao'], wads=wads)
    json.dump(manifest, open(os.path.join(ddir, 'manifest.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    prev = os.path.join(cdir, 'preview.png')
    if os.path.exists(prev):
        shutil.copy(prev, os.path.join(ddir, 'preview.png'))

    inst = os.path.join(RAIZ, 'instalador')
    for f in os.listdir(inst):
        shutil.copy(os.path.join(inst, f), dist)

    zp = os.path.join(RAIZ, 'build', f'{PASTA_DIST} v{VERSAO}.zip'.replace(' ', '_'))
    for velho in os.listdir(os.path.join(RAIZ, 'build')):
        if velho.endswith('.zip'):
            os.remove(os.path.join(RAIZ, 'build', velho))
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for r, _, fs in os.walk(dist):
            for f in fs:
                p = os.path.join(r, f)
                z.write(p, os.path.relpath(p, os.path.dirname(dist)))
    print('Pacote:', zp, f'({os.path.getsize(zp) / 1e6:.1f} MB)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'dark_odyssey')
