import streamlit as st

from modules.duimp.duimp_totvs import converter_duimp_totvs
from modules.ui import apply_base_style, render_metric_cards, render_page_header, render_sidebar_brand


CONVERSORES = {
    "DUIMP → TOTVS (Conexão Malhas)": {
        "descricao": "Converte o XML de extrato da DUIMP para o modelo XML exigido pelo sistema TOTVS.",
        "tipo_entrada": ["xml"],
        "funcao": converter_duimp_totvs,
        "sufixo_saida": "_TOTVS",
    },
}


def inicializar_estado():
    st.session_state.setdefault("conversor_resultado", None)
    st.session_state.setdefault("conversor_tipo", None)


apply_base_style()
render_sidebar_brand()
render_page_header("Conversor", "Transformação de XMLs entre formatos e sistemas.")
inicializar_estado()

col1, _ = st.columns([2, 3])
with col1:
    tipo = st.selectbox("Tipo de conversão", options=list(CONVERSORES.keys()))

cfg = CONVERSORES[tipo]
st.caption(cfg["descricao"])

arquivo = st.file_uploader(
    "XML de entrada",
    type=cfg["tipo_entrada"],
    accept_multiple_files=False,
)

if not arquivo:
    st.info("Faça upload do XML para iniciar a conversão.")
    st.stop()

render_metric_cards([
    {"label": "Arquivo", "value": arquivo.name},
    {"label": "Conversão", "value": tipo.split("→")[1].strip()},
])

if st.button("Converter", type="primary", use_container_width=True):
    try:
        dados = arquivo.read()
        saida = cfg["funcao"](dados)
        nome_base = arquivo.name.rsplit(".", 1)[0]
        nome_saida = f"{nome_base}{cfg['sufixo_saida']}.xml"
        st.session_state["conversor_resultado"] = {
            "nome_saida": nome_saida,
            "saida": saida,
            "erro": None,
        }
        st.session_state["conversor_tipo"] = tipo
    except Exception as exc:
        st.session_state["conversor_resultado"] = {
            "nome_saida": None,
            "saida": None,
            "erro": str(exc),
        }

resultado = st.session_state.get("conversor_resultado")
if not resultado:
    st.stop()

if resultado["erro"]:
    st.error(f"Erro na conversão: {resultado['erro']}")
    st.stop()

st.divider()
st.success(f"XML convertido com sucesso: **{resultado['nome_saida']}**")

st.download_button(
    label=f"Baixar {resultado['nome_saida']}",
    data=resultado["saida"],
    file_name=resultado["nome_saida"],
    mime="application/xml",
    type="primary",
    use_container_width=True,
)

with st.expander("Pré-visualizar XML gerado"):
    st.code(resultado["saida"].decode("utf-8"), language="xml")
