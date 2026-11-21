"""Delta binário "copiar do original + bytes novos" (o pacote não leva arquivos do jogo).

Um arquivo novo é descrito como uma sequência de operações sobre o arquivo ORIGINAL do usuário:
  copiar(origem, tamanho)  -> bytes do original
  literal(tamanho)         -> bytes novos (do bloco de literais do delta)
Funciona com inserções/remoções (mensagens, objetos novos, malha que cresce).

Formato (little-endian):
  'GW3D' u32 versão(1) u64 tamanho_saída u32 n_ops u32 0
  n_ops × (i64 origem [-1 = literal], u32 tamanho, u32 0)
  literais concatenados
"""
import struct

import numpy as np

MAGICO = b'GW3D'
B = 32            # tamanho mínimo de cópia / bloco do índice


def _run(O, N, q, p):
    """Quantos bytes iguais a partir de O[q], N[p]."""
    L, passo = 0, 4096
    while True:
        m = min(passo, len(O) - q - L, len(N) - p - L)
        if m <= 0:
            return L
        d = np.flatnonzero(O[q + L:q + L + m] != N[p + L:p + L + m])
        if len(d):
            return L + int(d[0])
        L += m
        passo = min(passo * 2, 1 << 22)


def _chaves(N, a, b):
    seg = N[a:b + 7].astype(np.uint64)
    k = np.zeros(b - a, np.uint64)
    for i in range(8):
        k |= seg[i:i + b - a] << np.uint64(8 * i)
    return k


def criar(orig, novo):
    O = np.frombuffer(orig, np.uint8)
    N = np.frombuffer(novo, np.uint8)
    nb = len(orig) // B
    kb = np.frombuffer(orig[:nb * B], '<u8').reshape(nb, B // 8)[:, 0] if nb else np.zeros(0, np.uint64)
    ks, primeiro = np.unique(kb, return_index=True)
    n = len(novo)

    def buscar(p, shift):
        """Próxima posição >= p onde começa uma cópia: (p2, q2) ou None."""
        a, W = p, 1 << 16
        while a < n - B:
            b = min(n - 8, a + W)
            melhor = None
            # 1) continuar com o mesmo deslocamento
            lo, hi = max(a, -shift), min(b, len(orig) - shift)
            if hi - lo > B:
                eq = (N[lo:hi] == O[lo + shift:hi + shift]).astype(np.int32)
                c = np.concatenate([[0], np.cumsum(eq)])
                r = np.flatnonzero(c[B:] - c[:-B] == B)
                if len(r):
                    melhor = (lo + int(r[0]), lo + int(r[0]) + shift)
            # 2) índice de blocos do original
            if len(ks) and b > a:
                k = _chaves(N, a, b)
                idx = np.clip(np.searchsorted(ks, k), 0, len(ks) - 1)
                cand = np.flatnonzero(ks[idx] == k)
                for i in cand[:2000]:
                    pi = a + int(i)
                    if melhor is not None and pi >= melhor[0]:
                        break
                    q = int(primeiro[idx[i]]) * B
                    if _run(O, N, q, pi) >= B:
                        melhor = (pi, q)
                        break
            if melhor is not None:
                return melhor
            a = b - B
            W *= 2
        return None

    ops, lits = [], []
    p, shift = 0, 0
    lit_ini = None

    def fecha_literal(fim):
        nonlocal lit_ini
        if lit_ini is not None and fim > lit_ini:
            ops.append((-1, fim - lit_ini)); lits.append(novo[lit_ini:fim])
        lit_ini = None

    while p < n:
        q = p + shift
        if 0 <= q < len(orig):
            L = _run(O, N, q, p)
            if L >= B:
                fecha_literal(p)
                if ops and ops[-1][0] >= 0 and ops[-1][0] + ops[-1][1] == q:
                    ops[-1] = (ops[-1][0], ops[-1][1] + L)
                else:
                    ops.append((q, L))
                p += L
                continue
        if lit_ini is None:
            lit_ini = p
        r = buscar(p, shift)
        if r is None:
            p = n
            break
        p2, q2 = r
        while p2 > lit_ini and q2 > 0 and orig[q2 - 1] == novo[p2 - 1]:   # estende para trás
            p2 -= 1; q2 -= 1
        if p2 == lit_ini:
            lit_ini = None
        p, shift = p2, q2 - p2
        if lit_ini is not None:
            fecha_literal(p)
    fecha_literal(n)

    out = [MAGICO, struct.pack('<IQII', 1, n, len(ops), 0)]
    out += [struct.pack('<qII', s, t, 0) for s, t in ops]
    out += lits
    d = b''.join(out)
    assert aplicar(orig, d) == novo
    return d


def aplicar(orig, d):
    assert d[:4] == MAGICO
    _, n, nops, _ = struct.unpack_from('<IQII', d, 4)
    pos = 24 + 16 * nops
    out = bytearray(n)
    o = 0
    for i in range(nops):
        s, t, _ = struct.unpack_from('<qII', d, 24 + 16 * i)
        if s < 0:
            out[o:o + t] = d[pos:pos + t]; pos += t
        else:
            out[o:o + t] = orig[s:s + t]
        o += t
    assert o == n
    return bytes(out)


def literais(d):
    _, n, nops, _ = struct.unpack_from('<IQII', d, 4)
    return len(d) - 24 - 16 * nops
