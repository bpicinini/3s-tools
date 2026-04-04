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
        st.Page("pages/xml_nfe.py", title="XML NF-e", icon="📄"),
        st.Page("pages/tecwin_sessoes.py", title="Sessões TecWin", icon="👥"),
        st.Page("pages/conversor.py", title="Conversor", icon="📊"),
    ],
})
pg.run()
