import io
import streamlit as st
from PIL import Image
from rembg import remove

st.set_page_config(
    page_title="Background Remover",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at 15% 0%, rgba(99,102,241,0.10), transparent 30%),
                 radial-gradient(circle at 90% 15%, rgba(14,165,233,0.08), transparent 28%),
                 #090b10;
}
.block-container {
    max-width: 1180px;
    padding-top: 42px;
    padding-bottom: 60px;
}
.header {
    text-align: center;
    margin-bottom: 38px;
}
.badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.09);
    color: #9ca5b5;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
}
.title {
    margin: 0;
    font-size: clamp(38px, 5vw, 58px);
    line-height: 1;
    font-weight: 800;
    letter-spacing: -0.045em;
    background: linear-gradient(135deg, #ffffff 0%, #d7dce6 50%, #858e9f 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
    margin-top: 16px;
    color: #858e9e;
    font-size: 15px;
    line-height: 1.6;
}
.upload-title {
    text-align: center;
    color: #e8ebf1;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 10px;
}
.upload-description {
    text-align: center;
    color: #6f7889;
    font-size: 12px;
    margin-top: 8px;
    margin-bottom: 15px;
}
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.025);
    border: 1px dashed rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 10px;
    transition: background 0.2s ease, border-color 0.2s ease;
}
[data-testid="stFileUploader"]:hover {
    background: rgba(255,255,255,0.04);
    border-color: rgba(255,255,255,0.30);
}
.card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.085);
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.025);
}
.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.card-title {
    color: #eef1f6;
    font-size: 14px;
    font-weight: 700;
}
.card-label {
    color: #737d8e;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
}
.preview-area {
    border-radius: 14px;
    overflow: hidden;
    background-color: #e5e7eb;
    background-image: linear-gradient(45deg, #cfd3da 25%, transparent 25%),
                      linear-gradient(-45deg, #cfd3da 25%, transparent 25%),
                      linear-gradient(45deg, transparent 75%, #cfd3da 75%),
                      linear-gradient(-45deg, transparent 75%, #cfd3da 75%);
    background-size: 24px 24px;
    background-position: 0 0, 0 12px, 12px -12px, -12px 0;
}
.success-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 14px;
    color: #8b95a6;
    font-size: 12px;
}
.success-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 12px rgba(74,222,128,0.55);
}
.info-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.055);
}
.info-row:last-child {
    border-bottom: none;
}
.info-label {
    color: #737d8e;
    font-size: 12px;
}
.info-value {
    color: #e7ebf2;
    font-size: 12px;
    font-weight: 600;
    max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.download-content {
    text-align: center;
    padding: 24px 10px 20px;
}
.download-icon {
    font-size: 34px;
    margin-bottom: 10px;
}
.download-title {
    color: #edf0f5;
    font-size: 15px;
    font-weight: 700;
}
.download-description {
    color: #747e8f;
    font-size: 12px;
    margin-top: 6px;
    margin-bottom: 20px;
}
.empty-state {
    text-align: center;
    padding: 65px 20px 45px;
}
.empty-icon {
    font-size: 58px;
    margin-bottom: 15px;
}
.empty-title {
    color: #e6eaf1;
    font-size: 18px;
    font-weight: 700;
}
.empty-description {
    color: #737d8e;
    font-size: 13px;
    margin-top: 7px;
}
.divider {
    width: 100%;
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 30px 0;
}
.stDownloadButton > button, .stButton > button {
    border-radius: 12px !important;
    min-height: 45px !important;
    font-weight: 600 !important;
}
.footer {
    text-align: center;
    color: #4f5868;
    font-size: 11px;
    margin-top: 48px;
}
</style>
""", unsafe_allow_html=True)

def abrir_imagem(arquivo):
    return Image.open(arquivo).convert("RGBA")

def remover_fundo(imagem):
    resultado = remove(imagem)
    if isinstance(resultado, Image.Image):
        return resultado.convert("RGBA")
    return Image.open(io.BytesIO(resultado)).convert("RGBA")

def imagem_para_png(imagem):
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return buffer.getvalue()

def formatar_tamanho(tamanho_bytes):
    if tamanho_bytes < 1024:
        return f"{tamanho_bytes} B"
    if tamanho_bytes < 1024 * 1024:
        return f"{tamanho_bytes / 1024:.1f} KB"
    return f"{tamanho_bytes / (1024 * 1024):.1f} MB"

st.markdown("""
<div class="header">
    <div class="badge">✂️ &nbsp; AI IMAGE TOOL</div>
    <h1 class="title">Background Remover</h1>
    <div class="subtitle">
        Remova o fundo de qualquer imagem automaticamente.<br>
        Resultado em PNG com transparência real.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="upload-title">Envie sua imagem</div>
<div class="upload-description">JPG, JPEG, PNG ou WEBP</div>
""", unsafe_allow_html=True)

arquivo = st.file_uploader(
    "Selecione uma imagem",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=False,
    label_visibility="collapsed",
)

if "arquivo_id" not in st.session_state:
    st.session_state.arquivo_id = None
if "imagem_original" not in st.session_state:
    st.session_state.imagem_original = None
if "imagem_sem_fundo" not in st.session_state:
    st.session_state.imagem_sem_fundo = None

if arquivo is None:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🖼️</div>
        <div class="empty-title">Pronto para remover o fundo</div>
        <div class="empty-description">Escolha uma imagem acima para começar.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    arquivo_id = f"{arquivo.name}:{arquivo.size}"
    if st.session_state.arquivo_id != arquivo_id:
        try:
            imagem_original = abrir_imagem(arquivo)
            with st.spinner("Removendo o fundo..."):
                imagem_sem_fundo = remover_fundo(imagem_original)
            st.session_state.arquivo_id = arquivo_id
            st.session_state.imagem_original = imagem_original
            st.session_state.imagem_sem_fundo = imagem_sem_fundo
            st.success("Fundo removido com sucesso!")
        except Exception as erro:
            st.error("Erro ao remover o fundo da imagem.")
            st.exception(erro)
            st.stop()

    imagem_original = st.session_state.imagem_original
    imagem_sem_fundo = st.session_state.imagem_sem_fundo

    largura, altura = imagem_original.size
    png_bytes = imagem_para_png(imagem_sem_fundo)
    tamanho_original = formatar_tamanho(arquivo.size)
    tamanho_resultado = formatar_tamanho(len(png_bytes))

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col_original, col_resultado = st.columns(2, gap="large")

    with col_original:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span class="card-title">Imagem original</span>
                <span class="card-label">ORIGINAL</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.image(imagem_original, use_container_width=True)

    with col_resultado:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span class="card-title">Imagem sem fundo</span>
                <span class="card-label">TRANSPARENTE</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="preview-area">', unsafe_allow_html=True)
        st.image(imagem_sem_fundo, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="success-status">
            <span class="success-dot"></span>
            Fundo removido com sucesso
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col_info, col_download = st.columns(2, gap="large")

    with col_info:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">
                <span class="card-title">Informações</span>
            </div>
            <div class="info-row">
                <span class="info-label">Arquivo</span>
                <span class="info-value" title="{arquivo.name}">{arquivo.name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Dimensões</span>
                <span class="info-value">{largura} × {altura}px</span>
            </div>
            <div class="info-row">
                <span class="info-label">Tamanho original</span>
                <span class="info-value">{tamanho_original}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Formato de saída</span>
                <span class="info-value">PNG</span>
            </div>
            <div class="info-row">
                <span class="info-label">Transparência</span>
                <span class="info-value">Canal Alpha</span>
            </div>
            <div class="info-row">
                <span class="info-label">Tamanho final</span>
                <span class="info-value">{tamanho_resultado}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_download:
        st.markdown("""
        <div class="card">
            <div class="download-content">
                <div class="download-icon">↓</div>
                <div class="download-title">Sua imagem está pronta</div>
                <div class="download-description">Baixe o PNG mantendo o fundo transparente.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        nome_base = arquivo.name.rsplit(".", 1)[0] if "." in arquivo.name else arquivo.name
        nome_download = f"{nome_base}_sem_fundo.png"
        st.download_button(
            label="⬇️  Baixar imagem sem fundo",
            data=png_bytes,
            file_name=nome_download,
            mime="image/png",
            use_container_width=True,
        )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if st.button("↻  Remover imagem e começar novamente", use_container_width=True):
        st.session_state.arquivo_id = None
        st.session_state.imagem_original = None
        st.session_state.imagem_sem_fundo = None
        st.rerun()

st.markdown('<div class="footer">Background Remover · Powered by rembg</div>', unsafe_allow_html=True)