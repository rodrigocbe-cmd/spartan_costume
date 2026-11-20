"""Varre o código do eboot.elf (segmento RX) com capstone e grava um índice pickle:
instruções com imediatos e referências RIP-relativas. uso: python -I ferramentas/disasm_scan.py"""
import pickle, struct, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP
d = open('original/eboot/eboot.elf', 'rb').read()
OFF, VA, SZ = 0x4000, 0, 0x3bd43c
code = d[OFF:OFF + SZ]
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True; md.skipdata = True
imms, rips = {}, {}
n = 0
for ins in md.disasm(code, VA):
    n += 1
    if ins.id == 0:
        continue
    try:
        ops = ins.operands
    except Exception:
        continue
    for op in ops:
        if op.type == X86_OP_IMM:
            imms.setdefault(op.imm & 0xffffffffffffffff, []).append(ins.address)
        elif op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
            rips.setdefault(ins.address + ins.size + op.mem.disp, []).append(ins.address)
pickle.dump(dict(imms=imms, rips=rips), open('original/eboot/indice.pkl', 'wb'))
print('instruções', n)
