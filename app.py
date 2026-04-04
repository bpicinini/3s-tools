import streamlit as st

st.set_page_config(
    page_title="3S Tools",
    page_icon="🛠️",
    layout="wide",
)

st.title("3S Tools")
st.caption("Portal de ferramentas operacionais — 3S Corporate")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("XML NF-e")
    st.write("Ajuste de espelho de nota fiscal. Reordena as descrições dos itens para o formato correto (referência na frente, NCM depois).")
    st.page_link("pages/1_XML_NFe.py", label="Abrir", icon="📄")

with col2:
    st.subheader("Sessões TecWin")
    st.write("Visualize quem está conectado no TecWin e desconecte usuários pendurados com um clique.")
    st.page_link("pages/2_TecWin_Sessoes.py", label="Abrir", icon="👥")

with col3:
    st.subheader("Conversor de Planilhas")
    st.write("Em breve.")
    st.page_link("pages/3_Conversor.py", label="Abrir", icon="📊")
