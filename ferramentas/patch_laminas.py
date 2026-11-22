"""Patch de código: lâminas douradas SÓ no traje da Odisseia Sombria.

O jogo carrega as armas pelo nome (ex.: "R_W_Explosive5") na mesma função que carrega todos os WADs
(eboot 0x1f4730 + base 0x400000). O patch desvia o início dessa função para um trecho novo, gravado em
preenchimentos de NOP entre funções (nunca executados), que faz:
    se [traje carregado] == INDICE e nome[4..7] == "Expl":  nome[4..11] = "GoldBlad"   (R_W_GoldBlade5)
    executa as 3 instruções deslocadas (push rbp; mov rbp,rsp; push r15) e volta.
O traje carregado (número do R_HeroNN) fica em 0x3c2b70 (gravado antes de carregar o R_HeroNN).
Os WADs R_W_GOLDBLADE0..5 são as lâminas douradas (cópias recoloridas de R_W_EXPLOSIVE0..5, mesmo nome
interno WAD_R_W_Explosive); os R_W_EXPLOSIVE originais ficam intactos para os outros trajes.

uso: python -I ferramentas/patch_laminas.py   -> grava os modelos em costumes/dark_odyssey/patches/
Os modelos têm {INDICE} (2 dígitos hex) para o instalador preencher com o slot da Odisseia Sombria.
"""
import os
import re
import struct

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ELF = os.path.join(RAIZ, 'original', 'eboot', 'eboot.elf')
BASE = 0x400000
OFF = 0x4000                 # deslocamento do segmento de código no ELF (va 0)
CODE_SZ = 0x3bd43c

HOOK = 0x1f4730              # função que carrega WADs por nome (rdi = nome)
VOLTA = 0x1f4736             # depois de push rbp; mov rbp,rsp; push r15
TRAJE_INSTR = 0x101bc0       # mov [rip+X], ecx  (X = 0x3c2b70, número do R_HeroNN carregado)
TRAJE = 0x3c2b70
P1, P2, P3, P4, SAI = 0x1073c1, 0x107411, 0x107461, 0x1074b1, 0x108c51   # preenchimentos de NOP


def carregar():
    d = open(ELF, 'rb').read()
    return d, d[OFF:OFF + CODE_SZ]


def rel32(de_fim, alvo):
    return struct.pack('<i', alvo - de_fim).hex()


def rel8(de_fim, alvo):
    v = alvo - de_fim
    assert -128 <= v < 128, v
    return struct.pack('<b', v).hex()


def assinatura(code, va, antes=12, depois=8, max_antes=48):
    """Pattern único (bytes exatos em volta de va) e o At correspondente."""
    for a in range(antes, max_antes + 1, 4):
        ini = va - a
        pat = code[ini:va + depois]
        if len([m for m in re.finditer(re.escape(pat), code)]) == 1:
            return ' '.join('%02x' % b for b in pat), a
    raise SystemExit('assinatura não única em %#x' % va)


def blocos(indice_hex):
    """Bytes de cada trecho (hex), já com os deslocamentos para esta versão do eboot."""
    p1 = '833d' + rel32(P1 + 7, TRAJE)[:8] + indice_hex   # cmp dword [rip+traje], imm8 (fim da instr. = P1+7)
    p1 += '0f85' + rel32(P1 + 13, SAI)                   # jne SAI
    p1 += 'eb' + rel8(P1 + 15, P2)                       # jmp P2
    p2 = '817f04' + b'Expl'.hex()                        # cmp dword [rdi+4], "Expl"
    p2 += '0f85' + rel32(P2 + 13, SAI)                   # jne SAI
    p2 += 'eb' + rel8(P2 + 15, P3)
    p3 = 'c74704' + b'Gold'.hex() + 'eb' + rel8(P3 + 9, P4)        # mov dword [rdi+4], "Gold"
    p4 = 'c74708' + b'Blad'.hex() + 'e9' + rel32(P4 + 12, SAI)     # mov dword [rdi+8], "Blad"
    sai = '554889e54157' + 'e9' + rel32(SAI + 11, VOLTA)            # instruções deslocadas + volta
    hook = 'e9' + rel32(HOOK + 5, P1) + '90'
    return dict(hook=hook, p1=p1, p2=p2, p3=p3, p4=p4, sai=sai)


def verificar(d, code):
    # o início da função e os preenchimentos são o que esperamos
    assert code[HOOK:HOOK + 6] == bytes.fromhex('554889e54157'), code[HOOK:HOOK + 8].hex()
    assert code[TRAJE_INSTR:TRAJE_INSTR + 2] == b'\x89\x0d'
    assert TRAJE_INSTR + 6 + struct.unpack_from('<i', code, TRAJE_INSTR + 2)[0] == TRAJE
    nop15 = bytes.fromhex('666666666666' + '2e0f1f840000000000')
    tam = {P1: 15, P2: 15, P3: 9, P4: 12, SAI: 11}
    for p, n in tam.items():
        assert code[p:p + 15] == nop15, ('preenchimento', hex(p), code[p:p + 15].hex())
        assert n <= 15
    verificar_saltos(code, list(tam))
    return True


def verificar_saltos(code, pads):
    """Nenhum salto/chamada do jogo (perto dos preenchimentos) cai dentro deles."""
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    for p in pads:
        ini = (p & ~0xf) - 0x400
        for i in md.disasm(code[ini:p + 0x500], ini):
            if i.mnemonic.startswith('j') or i.mnemonic == 'call':
                try:
                    t = int(i.op_str, 16)
                except ValueError:
                    continue
                assert not any(q <= t < q + 15 for q in pads), ('salto para dentro do preenchimento', hex(i.address))


def xml_spartan(d, code):
    """Modelo do patch para o SpartanPort (mods/<mod>/patches/*.xml), com assinaturas e alvos nomeados."""
    def bloco_rel(indice):
        return dict(
            hook='e9{rel:p1:0}90',
            p1='833d{rel:traje:1}' + indice + '0f85{rel:sai:0}eb' + rel8(P1 + 15, P2),
            p2='817f04' + b'Expl'.hex() + '0f85{rel:sai:0}eb' + rel8(P2 + 15, P3),
            p3='c74704' + b'Gold'.hex() + 'eb' + rel8(P3 + 9, P4),
            p4='c74708' + b'Blad'.hex() + 'e9{rel:sai:0}',
            sai='554889e54157e9{rel:volta:0}')
    b = bloco_rel('{INDICE}')
    linhas = []
    for nome, va in (('hook', HOOK), ('p1', P1), ('p2', P2), ('p3', P3), ('p4', P4), ('sai', SAI)):
        if nome == 'hook':
            pat, at = ' '.join('%02x' % x for x in code[HOOK:HOOK + 24]), 0
            assert len(list(re.finditer(re.escape(code[HOOK:HOOK + 24]), code))) == 1
        else:
            pat, at = assinatura(code, va, antes=16, depois=15)
        linhas.append('            <Line Type="bytes" Address="0x%08x" Value="%s" Pattern="%s" At="%d"/>'
                      % (va + BASE, b[nome], pat, at))
    n = 14
    while len(list(re.finditer(re.escape(code[VOLTA:VOLTA + n]), code))) != 1:   # só bytes DEPOIS do desvio
        n += 2
        assert n < 64
    pv = code[VOLTA:VOLTA + n]
    tpat, tat = assinatura(code, TRAJE_INSTR + 2, antes=12, depois=8)
    alvos = [
        '        <Target Name="p1" Address="0x%08x" Line="1"/>' % (P1 + BASE),
        '        <Target Name="sai" Address="0x%08x" Line="5"/>' % (SAI + BASE),
        '        <Target Name="volta" Address="0x%08x" Pattern="%s" At="0"/>'
        % (VOLTA + BASE, ' '.join('%02x' % x for x in pv)),
        '        <Target Name="traje" Address="0x%08x" Pattern="%s" At="%d" Ref="1" Tail="0"/>'
        % (TRAJE + BASE, tpat, tat),
    ]
    return ('<?xml version="1.0"?>\n'
            '<!-- GoW III Costumes: laminas douradas so no traje Odisseia Sombria (slot {INDICE} hex).\n'
            '     Gerado por ferramentas/patch_laminas.py. Desvia a funcao que carrega WADs: com esse traje,\n'
            '     "R_W_Explosive<n>" vira "R_W_GoldBlade<n>" (WADs dourados instalados pelo mod). -->\n'
            '<Patch>\n    <TitleID>\n        <ID>CUSA01623</ID>\n        <ID>CUSA01715</ID>\n    </TitleID>\n'
            '    <Metadata Title="God of War III Remastered" Name="GoW3 Costumes - Laminas douradas da Odisseia Sombria"'
            ' Note="Golden blades only with the Dark Odyssey costume." Author="GoW III Costumes" PatchVer="1.0"'
            ' AppVer="01.02" AppElf="eboot.bin" isEnabled="true">\n'
            '        <PatchList>\n' + '\n'.join(linhas) + '\n        </PatchList>\n'
            + '\n'.join(alvos) + '\n    </Metadata>\n</Patch>\n')


def xml_goldhen(blocos_hex):
    """Modelo para PS4 (GoldHEN, CUSA01623 v01.02): endereços fixos, deslocamentos já resolvidos."""
    ls = ['            <Line Type="bytes" Address="0x%08x" Value="%s"/>' % (va + BASE, blocos_hex[n])
          for n, va in (('p1', P1), ('p2', P2), ('p3', P3), ('p4', P4), ('sai', SAI), ('hook', HOOK))]
    return ('<?xml version="1.0" encoding="utf-8"?>\n<Patch>\n    <TitleID>\n        <ID>CUSA01623</ID>\n    </TitleID>\n'
            '    <Metadata Title="God of War III Remastered" Name="GoW3 Costumes - Golden blades (Dark Odyssey only)"'
            ' Note="Golden blades only with the Dark Odyssey costume (slot {INDICE} hex)." Author="GoW III Costumes"'
            ' PatchVer="1.0" AppVer="01.02" AppElf="eboot.bin">\n        <PatchList>\n'
            + '\n'.join(ls) + '\n        </PatchList>\n    </Metadata>\n</Patch>\n')


def main():
    d, code = carregar()
    verificar(d, code)
    b = blocos('{INDICE}')
    # tamanhos (com 2 hex do índice)
    for n, h in b.items():
        tam = len(h.replace('{INDICE}', '00')) // 2
        print(n, tam, 'bytes')
        assert tam <= 15
    dst = os.path.join(RAIZ, 'costumes', 'dark_odyssey', 'patches')
    os.makedirs(dst, exist_ok=True)
    open(os.path.join(dst, 'spartanport.xml'), 'w', encoding='utf-8').write(xml_spartan(d, code))
    open(os.path.join(dst, 'goldhen.xml'), 'w', encoding='utf-8').write(xml_goldhen(b))
    print('modelos em', dst)


if __name__ == '__main__':
    main()
