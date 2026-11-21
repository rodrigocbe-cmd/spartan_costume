"""Encaixe das peças do modelo do Soulcalibur (God Armor 2P) no Kratos do GoW III (pose T)."""
import numpy as np

ESCALA_SC = 0.851            # altura do Kratos GoW III / altura do modelo SC


def rot_a_para_b(a, b):
    """Rotação mínima (matriz para uso p @ R) que leva o vetor a para b."""
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = float(a @ b)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = np.eye(3) + vx + vx @ vx * (1 / (1 + c))
    return R.T                 # convenção p @ R


def ombreira_direita(V, eixo_sc, pivo_sc, pivo_gow, dir_gow=np.array([1.0, 0, 0]), escala_extra=1.0, desloc=np.zeros(3)):
    R = rot_a_para_b(eixo_sc, dir_gow)
    s = ESCALA_SC * escala_extra
    return ((V - pivo_sc) * s) @ R + pivo_gow + desloc
