import numpy as np

from .garantir_uint import garantir_uint8


def ajustar_brilho_contraste(imagem, alpha=1.0, beta=0.0):
    """
    Aplica g(x,y) = alpha * f(x,y) + beta, pixel a pixel.

    alpha : ganho de contraste (1.0 = neutro; >1 aumenta, <1 diminui)
    beta  : deslocamento de brilho (0 = neutro; soma/subtrai intensidade)
    """
    imagem_float = imagem.astype(np.float64)
    saida = alpha * imagem_float + beta
    return garantir_uint8(saida)
