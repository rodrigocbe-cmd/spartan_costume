"""Edição de WAD por blocos (inserir/copiar entradas entre WADs do jogo).

Um bloco = cabeçalho de 0x40 B + dados + alinhamento. Funções para:
  - copiar um MATERIAL de outro WAD (grupo GroupStart..próximo GroupStart: MAT, GroupEnd, ANM,
    shaders compilados tag 0x770001) + as TEXTURAS que ele cita e que faltam no destino;
  - acrescentar materiais à lista do modelo (referências tag 0x0001 antes da referência ao MG, um bloco
    por variante; nº de materiais no MDL +0x1c);
  - trocar dados de uma entrada (tamanho pode mudar).
As entradas DC_WAD são iguais em todos os R_HERO (não contam texturas/materiais).
"""
import re
import struct

from wad import parse, align, HDR


class Wad:
    def __init__(self, d):
        self.blocos = []
        for e in parse(d):
            fim = align(e['data_off'] + e['size'])
            self.blocos.append([dict(tag=e['tag'], name=e['name']), bytearray(d[e['off']:fim])])

    # --- consulta
    def idx(self, nome, tag=None, k=0):
        r = [i for i, (e, b) in enumerate(self.blocos) if e['name'] == nome and (tag is None or e['tag'] == tag)]
        return r[k]

    def tem(self, nome, tag=None):
        return any(e['name'] == nome and (tag is None or e['tag'] == tag) for e, b in self.blocos)

    def dados(self, i):
        e, b = self.blocos[i]
        n = struct.unpack_from('<I', b, 4)[0]
        return bytes(b[HDR:HDR + (0 if e['tag'] == 0 else n)])

    def trocar_dados(self, i, novo):
        e, b = self.blocos[i]
        h = bytearray(b[:HDR])
        struct.pack_into('<I', h, 4, len(novo))
        nb = h + novo
        nb += b'\x00' * (align(len(nb)) - len(nb))
        self.blocos[i][1] = bytearray(nb)

    def bytes(self):
        out = b''.join(bytes(b) for e, b in self.blocos)
        return out + b'\x00' * (align(len(out)) - len(out))

    def inserir(self, depois_de, blocos):
        self.blocos[depois_de + 1:depois_de + 1] = blocos

    # --- materiais
    def grupo_material(self, nome_mat):
        """Índices [ini, fim) do grupo do material: GroupStart antes do MAT até o GroupEnd com o nome
        dele (inclui ANM_templatens). Os shaders que vêm DEPOIS do GroupEnd são de outro programa."""
        i = self.idx('MAT_' + nome_mat if not nome_mat.startswith('MAT_') else nome_mat, 0x560001)
        nome = self.blocos[i][0]['name']
        ini = i - 1
        assert self.blocos[ini][0]['tag'] == 2, 'MAT sem GroupStart'
        fim = i + 1
        while not (self.blocos[fim][0]['tag'] == 3 and self.blocos[fim][0]['name'] == nome):
            fim += 1
        return ini, fim + 1

    def programa(self, prog):
        """Índices [ini, fim) das entradas do programa de shader `prog` (ex. '1A3D6F33'): '<prog>_*',
        'dbg_<prog>_*' e os marcadores DebugStart/DebugEnd entre eles."""
        ks = [k for k, (e, b) in enumerate(self.blocos) if e['tag'] == 0x770001
              and (e['name'].startswith(prog + '_') or e['name'].startswith('dbg_' + prog + '_'))]
        if not ks:
            return None
        ini, fim = min(ks), max(ks) + 1
        aberto = sum(1 for k in range(ini, fim) if self.blocos[k][0]['tag'] == 0x19) -             sum(1 for k in range(ini, fim) if self.blocos[k][0]['tag'] == 0x1a)
        while aberto > 0 and self.blocos[fim][0]['tag'] == 0x1a:
            fim += 1; aberto -= 1
        return ini, fim


PROG_MAT = 0x7c     # MAT +0x7c: u32 = programa de shader (entradas '<PROG>_<variante>' tag 0x770001)


def _textures_do_material(dados):
    return sorted({m.decode() for m in re.findall(rb'TX[0-9A-F]{8}\.[0-9A-F]{8}\.dds', dados)})


def copiar_material(dest, doador, nome_mat, log=print):
    """Copia o material `nome_mat` (ex.: 'templatens:skirt_m') do WAD doador para o destino:
    o grupo do MAT (GroupStart..GroupEnd), o PROGRAMA de shader que ele cita em +0x7c (se faltar no
    destino; vai antes do MAT, como no jogo) e as texturas que faltarem."""
    nome = 'MAT_' + nome_mat
    if dest.tem(nome, 0x560001):
        log('  material já existe:', nome_mat)
        return
    ini, fim = doador.grupo_material(nome)
    novos = [[dict(e), bytearray(b)] for e, b in doador.blocos[ini:fim]]
    i_mat = [k for k, (e, b) in enumerate(novos) if e['tag'] == 0x560001][0]
    dados_mat = bytes(novos[i_mat][1][HDR:])
    prog = '%08X' % struct.unpack_from('<I', dados_mat, PROG_MAT)[0]
    if dest.programa(prog) is None:
        r = doador.programa(prog)
        assert r, 'programa %s não está no doador' % prog
        novos = [[dict(e), bytearray(b)] for e, b in doador.blocos[r[0]:r[1]]] + novos
        log('  + programa de shader', prog, '(%d entradas)' % (r[1] - r[0]))
    # depois do último grupo de material do destino (antes do ANM_hero)
    i_anm = dest.idx('ANM_hero', 0x340001)
    dest.inserir(i_anm - 1, novos)
    for tx in _textures_do_material(dados_mat):
        if dest.tem(tx, 0xd0001):
            continue
        it = doador.idx(tx, 0xd0001)
        ultimo_tx = max(i for i, (e, b) in enumerate(dest.blocos) if e['tag'] == 0xd0001 and e['name'].startswith('TX'))
        dest.inserir(ultimo_tx, [[dict(doador.blocos[it][0]), bytearray(doador.blocos[it][1])]])
        log('  + textura', tx)
    log('  + material', nome_mat, '(programa %s)' % prog)


def lista_materiais(w, nome_mg):
    """(índice da referência ao MG, [índices das referências MAT antes dela])"""
    j = w.idx(nome_mg, 1)
    k = j - 1
    refs = []
    while w.blocos[k][0]['tag'] == 1 and w.blocos[k][0]['name'].startswith('MAT'):
        refs.insert(0, k)
        k -= 1
    return j, refs


def _ref(nome):
    b = bytearray(HDR)
    struct.pack_into('<II', b, 0, 1, 0)
    n = nome.encode('latin1')
    b[8:8 + len(n)] = n
    return [dict(tag=1, name=nome), b]


def acrescentar_materiais(w, nome_mg, nome_mdl, novos, variantes=None):
    """Acrescenta materiais ao FIM de cada bloco da lista do modelo. novos = [nome_base, ...]
    (ex.: 'templatens:skirt_m'); variantes = {nº do bloco: {nome_base: nome_variante}}.
    Devolve os índices de material atribuídos."""
    variantes = variantes or {}
    i_mdl = w.idx(nome_mdl, 0x520001)
    mdl = bytearray(w.dados(i_mdl))
    n = struct.unpack_from('<I', mdl, 0x1c)[0]
    j, refs = lista_materiais(w, nome_mg)
    nblocos = len(refs) // n
    assert nblocos * n == len(refs), (len(refs), n)
    for b in range(nblocos - 1, -1, -1):
        fim_bloco = refs[(b + 1) * n - 1]
        itens = [_ref('MAT_' + variantes.get(b, {}).get(m, m)) for m in novos]
        w.inserir(fim_bloco, itens)
    struct.pack_into('<I', mdl, 0x1c, n + len(novos))
    w.trocar_dados(i_mdl, bytes(mdl))
    return list(range(n, n + len(novos)))


def atualizar_matx(w, log=print):
    """MATX_<wad> (+0x10: u32 nº de programas de shader [prefixos distintos das entradas 0x770001 sem
    'dbg'], u32 nº de variantes [entradas - programas]). Confirmado nos 9 R_HERO. Sem isso, shaders
    copiados de outro WAD não são registrados e o jogo trava ao carregar o modelo."""
    sh = [e['name'] for e, b in w.blocos if e['tag'] == 0x770001 and not e['name'].startswith('dbg')]
    prog = len({x.split('_')[0] for x in sh})
    i = [k for k, (e, b) in enumerate(w.blocos) if e['name'].startswith('MATX_') and e['tag'] == 1][0]
    d = bytearray(w.dados(i))
    antes = struct.unpack_from('<II', d, 0x10)
    struct.pack_into('<II', d, 0x10, prog, len(sh) - prog)
    w.trocar_dados(i, bytes(d))
    log('  MATX: %s -> %s' % (antes, (prog, len(sh) - prog)))
