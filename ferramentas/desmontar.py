"""Desmonta um trecho do eboot.elf. uso: python -I ferramentas/dis.py <va_ini_hex> <n_bytes_hex>"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
d = open('original/eboot/eboot.elf', 'rb').read()
va = int(sys.argv[1], 16); n = int(sys.argv[2], 16)
md = Cs(CS_ARCH_X86, CS_MODE_64)
for i in md.disasm(d[0x4000 + va:0x4000 + va + n], va):
    extra = ''
    if 'rip' in i.op_str:
        import re
        m = re.search(r'rip ([+-]) 0x([0-9a-f]+)', i.op_str)
        if m:
            t = i.address + i.size + (int(m.group(2), 16) * (1 if m.group(1) == '+' else -1))
            s = d[0x4000 + t:0x4000 + t + 40].split(b'\0')[0]
            extra = f'   ; -> {t:#x} ' + (repr(s[:40]) if s and all(32 <= c < 127 for c in s) else '')
    print(f'{i.address:#08x}: {i.mnemonic:8s} {i.op_str}{extra}')
