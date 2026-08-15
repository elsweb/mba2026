import numpy as np


def garantir_uint8(imagem):
    """
    Satura (clipa) os valores no intervalo [0, 255] e converte para uint8.

    É a "porta de saída" de toda operação ponto a ponto ou filtro espacial
    desta aula: fazemos a matemática em float64 e só chamamos garantir_uint8()
    antes de exibir ou salvar o resultado.
    """
    return np.clip(imagem, 0, 255).astype(np.uint8)
