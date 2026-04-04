import streamlit as st

from modules.ui import apply_base_style, render_page_header, render_sidebar_brand


apply_base_style()
render_sidebar_brand()

st.markdown("""
<style>
div[data-testid="stButton"] button {
    background: #ffffff;
    border: 1px solid #e4ddd1;
    border-radius: 16px;
    padding: 30px 28px;
    width: 100%;
    min-height: 290px;
    text-align: left;
    white-space: normal;
    color: #1f2933;
    cursor: pointer;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    line-height: 1.5;
    box-shadow: 0 10px 24px rgba(31, 53, 80, 0.06);
}

div[data-testid="stButton"] button:hover {
    box-shadow: 0 14px 28px rgba(31, 53, 80, 0.08);
    border-color: #5279a3;
    color: inherit;
}

div[data-testid="stButton"] button:focus {
    box-shadow: 0 14px 28px rgba(31, 53, 80, 0.08);
    border-color: #5279a3;
    color: inherit;
}

div[data-testid="stButton"] button p {
    margin: 0;
    font-size: 1.12rem;
    line-height: 1.65;
}

div[data-testid="stButton"] button strong {
    display: inline-block;
    font-size: 1.4rem;
    line-height: 1.2;
    margin: 0.2rem 0 0.35rem 0;
}
</style>
""", unsafe_allow_html=True)

render_page_header("Ferramentas", "Selecione um módulo.")

col1, col2, col3 = st.columns(3, gap="small")

with col1:
    if st.button(
        "👥\n\n**Acessos TECWIN**\n\nMonitoramento e desconexão\n\nDisponível",
        key="btn_tecwin",
        use_container_width=True,
    ):
        st.switch_page("views/tecwin_sessoes.py")

with col2:
    if st.button(
        "📄\n\n**Reparador de XML**\n\nXML e Excel\n\nDisponível",
        key="btn_xml",
        use_container_width=True,
    ):
        st.switch_page("views/xml_nfe.py")

with col3:
    st.button(
        "📊\n\n**Conversor**\n\nPadronização de planilhas\n\nEm breve",
        key="btn_conversor",
        disabled=True,
        use_container_width=True,
    )
