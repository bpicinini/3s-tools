import streamlit as st

st.set_page_config(
    page_title="3S Tools",
    page_icon="🛠️",
    layout="wide",
)

pg = st.navigation({
    "": [
        st.Page("pages/home.py", title="Home", icon="🏠"),
    ],
    "Ferramentas": [
        st.Page("pages/1_XML_NFe.py", title="XML NF-e", icon="📄"),
        st.Page("pages/2_TecWin_Sessoes.py", title="Sessões TecWin", icon="👥"),
        st.Page("pages/3_Conversor.py", title="Conversor", icon="📊"),
    ],
})
pg.run()
