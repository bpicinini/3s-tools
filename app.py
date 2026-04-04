import streamlit as st


st.set_page_config(
    page_title="3S Tools",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation({
    "": [
        st.Page("views/home.py", title="Home", icon="🏠"),
    ],
    "Ferramentas": [
        st.Page("views/xml_nfe.py", title="XML NF-e", icon="📄"),
        st.Page("views/tecwin_sessoes.py", title="Sessões TecWin", icon="👥"),
        st.Page("views/conversor.py", title="Conversor", icon="📊"),
    ],
})
pg.run()
