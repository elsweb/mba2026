import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from web.biblioteca.brilho import ajustar_brilho_contraste

caminho_imagem = "nootbooks/imgs/dog.jpg"
imagem_original = plt.imread(caminho_imagem)


alpha_input = st.slider(
    "Contraste",
    min_value=0.0,
    max_value=10.0,
    value=1.0,
    step=0.1,
    key="contraste",
)
beta_input = st.slider(
    "Brilho",
    min_value=0.0,
    max_value=10.0,
    value=0.0,
    key="brilho",
)

colA, colB = st.columns(2)

with colA:
    st.image(imagem_original, caption="Imagem Original")

with colB:
    st.image(
        ajustar_brilho_contraste(
            imagem_original,
            alpha=alpha_input,
            beta=beta_input,
        ),
        caption="Imagem Ajustada",
    )


def carregar_imagem_rgb(caminho):
    """Carrega uma imagem como float64 RGB no intervalo [0, 1]."""
    imagem = mpimg.imread(caminho)

    if imagem.ndim == 2:
        imagem = np.stack([imagem, imagem, imagem], axis=-1)
    elif imagem.shape[-1] == 4:
        imagem = imagem[..., :3]

    imagem = imagem.astype(np.float64)
    if imagem.max() > 1.0:
        imagem /= 255.0

    return np.clip(imagem, 0.0, 1.0)


def mostrar_pontos(imagem, pontos, titulo):
    """Exibe uma imagem com quatro pontos [x, y] e o polígono fechado."""
    _fig, ax = plt.subplots(figsize=(9, 6))
    ax.imshow(imagem)
    pontos_fechados = np.vstack([pontos, pontos[0]])
    ax.plot(pontos_fechados[:, 0], pontos_fechados[:, 1], color="crimson", linewidth=2)
    ax.scatter(
        pontos[:, 0], pontos[:, 1], color="yellow", edgecolors="black", s=80, zorder=3
    )
    for indice, (x, y) in enumerate(pontos):
        ax.text(
            x + 8,
            y - 8,
            str(indice),
            color="black",
            fontsize=11,
            bbox={"facecolor": "yellow", "edgecolor": "black", "pad": 2},
        )
    ax.set_title(titulo)
    ax.axis("off")
    plt.show()


def calcular_homografia_dlt(pts_origem, pts_destino):
    """Calcula H de origem para destino usando DLT e SVD."""
    pts_origem = np.asarray(pts_origem, dtype=np.float64)
    pts_destino = np.asarray(pts_destino, dtype=np.float64)

    if pts_origem.shape != (4, 2) or pts_destino.shape != (4, 2):
        raise ValueError("São necessários dois arrays com shape (4, 2).")
    if not np.all(np.isfinite(pts_origem)) or not np.all(np.isfinite(pts_destino)):
        raise ValueError("Os pontos devem conter apenas valores finitos.")

    matriz_a = []
    for (x, y), (u, v) in zip(pts_origem, pts_destino):
        # As duas linhas abaixo são as equações para U/W = u e V/W = v.
        matriz_a.append([-x, -y, -1, 0, 0, 0, x * u, y * u, u])
        matriz_a.append([0, 0, 0, -x, -y, -1, x * v, y * v, v])

    matriz_a = np.asarray(matriz_a, dtype=np.float64)
    _, valores_singulares, vh = np.linalg.svd(matriz_a)
    vetor_h = vh[-1]
    homografia = vetor_h.reshape(3, 3)

    if np.isclose(homografia[2, 2], 0.0):
        homografia /= np.linalg.norm(homografia)
    else:
        homografia /= homografia[2, 2]

    return homografia, matriz_a, valores_singulares


def aplicar_perspectiva_nearest(imagem, homografia, nova_altura, nova_largura):
    """Retifica uma imagem usando inverse warping e Nearest Neighbor."""
    imagem = np.asarray(imagem)
    if imagem.ndim not in (2, 3):
        raise ValueError("A imagem deve ter shape (H, W) ou (H, W, C).")
    if nova_altura <= 0 or nova_largura <= 0:
        raise ValueError("As dimensões de saída devem ser positivas.")

    era_cinza = imagem.ndim == 2
    imagem_3d = imagem[..., None] if era_cinza else imagem
    altura_origem, largura_origem, canais = imagem_3d.shape

    # Um ponto de saída pergunta de qual ponto da entrada deve receber sua cor.
    grade_x, grade_y = np.meshgrid(
        np.arange(nova_largura, dtype=np.float64),
        np.arange(nova_altura, dtype=np.float64),
    )
    pontos_saida = np.vstack(
        [
            grade_x.ravel(),
            grade_y.ravel(),
            np.ones(grade_x.size, dtype=np.float64),
        ]
    )

    homografia_inversa = np.linalg.inv(np.asarray(homografia, dtype=np.float64))
    pontos_origem_h = homografia_inversa @ pontos_saida
    w = pontos_origem_h[2]

    pontos_validos = np.abs(w) > 1e-12
    x_origem = np.full(w.shape, np.nan)
    y_origem = np.full(w.shape, np.nan)
    x_origem[pontos_validos] = pontos_origem_h[0, pontos_validos] / w[pontos_validos]
    y_origem[pontos_validos] = pontos_origem_h[1, pontos_validos] / w[pontos_validos]

    x_pixel = np.rint(x_origem).astype(np.int64)
    y_pixel = np.rint(y_origem).astype(np.int64)
    pontos_validos &= (
        (x_pixel >= 0)
        & (x_pixel < largura_origem)
        & (y_pixel >= 0)
        & (y_pixel < altura_origem)
    )

    saida = np.zeros((nova_altura, nova_largura, canais), dtype=imagem_3d.dtype)
    saida_y = grade_y.ravel()[pontos_validos].astype(np.int64)
    saida_x = grade_x.ravel()[pontos_validos].astype(np.int64)
    saida[saida_y, saida_x] = imagem_3d[
        y_pixel[pontos_validos], x_pixel[pontos_validos]
    ]

    return saida[..., 0] if era_cinza else saida


def pontos_para_homogeneos(pontos):
    """Converte um array (N, 2) de pontos [x, y] para (N, 3)."""
    pontos = np.asarray(pontos, dtype=np.float64)
    if pontos.ndim != 2 or pontos.shape[1] != 2:
        raise ValueError("Esperado um array com shape (N, 2).")
    return np.hstack([pontos, np.ones((pontos.shape[0], 1))])


def pontos_para_cartesianos(pontos_homogeneos):
    """Divide as duas primeiras coordenadas pela coordenada homogênea W."""
    pontos_homogeneos = np.asarray(pontos_homogeneos, dtype=np.float64)
    if pontos_homogeneos.ndim != 2 or pontos_homogeneos.shape[1] != 3:
        raise ValueError("Esperado um array com shape (N, 3).")
    w = pontos_homogeneos[:, 2]
    if np.any(np.isclose(w, 0.0)):
        raise ValueError("Não é possível de-homogeneizar W próximo de zero.")
    return pontos_homogeneos[:, :2] / w[:, None]


def aplicar_homografia(pontos, homografia):
    """Aplica qualquer matriz 3x3 (afim ou projetiva) a pontos (N, 2), retornando pontos cartesianos (N, 2)."""
    pontos_h = pontos_para_homogeneos(pontos)
    transformados_h = (homografia @ pontos_h.T).T
    return pontos_para_cartesianos(transformados_h)


caminho_imagem = "nootbooks/imgs/edge_warp.jpeg"
imagem_foto = carregar_imagem_rgb(caminho_imagem)
altura_foto, largura_foto = imagem_foto.shape[:2]


colA, colB = st.columns(2, border=True)
with colA:
    st.write("Canto Superior Esquerdo")

    sub_colA, sub_colB = st.columns(2)
    q_se_x = sub_colA.slider("Eixo X", 0, largura_foto, 605)
    q_se_y = sub_colB.slider("Eixo Y", 0, altura_foto, 227)

with colB:
    st.write("Canto Superior Direito")
    sub_colA, sub_colB = st.columns(2)
    q_sd_x = sub_colA.slider("Eixo X", 0, largura_foto, 1450)
    q_sd_y = sub_colB.slider("Eixo Y", 0, altura_foto, 599)

colA, colB = st.columns(2, border=True)
with colA:
    st.write("Canto Inferior Esquerdo")
    sub_colA, sub_colB = st.columns(2)
    q_ie_x = sub_colA.slider("Eixo X", 0, largura_foto, 149)
    q_ie_y = sub_colB.slider("Eixo Y", 0, altura_foto, 644)

with colB:
    st.write("Canto Inferior Direito")
    sub_colA, sub_colB = st.columns(2)
    q_id_x = sub_colA.slider("Eixo X", 0, largura_foto, 931)
    q_id_y = sub_colB.slider("Eixo Y", 0, altura_foto, 1270)


quinas_origem = np.array(
    [
        [q_se_x, q_se_y],
        [q_sd_x, q_sd_y],
        [q_id_x, q_id_y],
        [q_ie_x, q_ie_y],
    ],
    dtype=np.float64,
)

# Proporção de uma folha A4 em orientação paisagem (horizontal).
altura_saida = 400
largura_saida = round(altura_saida * 1.4142)
quinas_destino = np.array(
    [
        [0, 0],
        [largura_saida - 1, 0],
        [largura_saida - 1, altura_saida - 1],
        [0, altura_saida - 1],
    ],
    dtype=np.float64,
)

H_scanner, A_scanner, S_scanner = calcular_homografia_dlt(quinas_origem, quinas_destino)
imagem_retificada = aplicar_perspectiva_nearest(
    imagem_foto,
    H_scanner,
    nova_altura=altura_saida,
    nova_largura=largura_saida,
)

quinas_reprojetadas = aplicar_homografia(quinas_origem, H_scanner)
erro_scanner = np.max(np.linalg.norm(quinas_reprojetadas - quinas_destino, axis=1))

colA, colB = st.columns(2, border=True)
with colA:
    st.image(imagem_foto, caption="Imagem Original com Quinas Selecionadas")

with colB:
    st.image(imagem_retificada, caption="Imagem Retificada com Quinas Reprojetadas")
