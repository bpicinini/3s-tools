import streamlit as st

st.markdown("""
<style>
.hero-title { font-size: 2rem; font-weight: 800; color: #1E3A5F; margin-bottom: 4px; }
.hero-sub   { font-size: 1rem; color: #666; margin-bottom: 32px; }

/* Card via botão */
div[data-testid="stButton"] button {
    background: #f8f9fb;
    border: 1px solid #e3e6ed;
    border-radius: 12px;
    padding: 28px 24px;
    width: 100%;
    height: 220px;
    text-align: left;
    white-space: normal;
    color: inherit;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
    line-height: 1.5;
}
div[data-testid="stButton"] button:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(30,58,95,0.15);
    border-color: #1E3A5F;
    background: #ffffff;
    color: inherit;
}
div[data-testid="stButton"] button:focus {
    box-shadow: 0 8px 24px rgba(30,58,95,0.15);
    border-color: #1E3A5F;
    color: inherit;
}
div[data-testid="stButton"] button p {
    margin: 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">🛠️ 3S Tools</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Portal de ferramentas operacionais — 3S Corporate</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    if st.button("📄\n\n**XML NF-e**\n\nAjuste de espelho de nota fiscal. Reordena as descrições dos itens para o formato correto — referência na frente, NCM depois.\n\n🟢 Disponível", key="btn_xml"):
        st.switch_page("views/xml_nfe.py")

with col2:
    if st.button("👥\n\n**Sessões TecWin**\n\nVisualize quem está conectado no TecWin e desconecte usuários pendurados com um clique. Limite de 30 minutos por sessão.\n\n🟢 Disponível", key="btn_tecwin"):
        st.switch_page("views/tecwin_sessoes.py")

with col3:
    st.button("📊\n\n**Conversor de Planilhas**\n\nConversão e padronização de planilhas para formatos utilizados na operação. Em desenvolvimento.\n\n⚪ Em breve", key="btn_conversor", disabled=True)
