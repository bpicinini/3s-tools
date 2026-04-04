import streamlit as st

from modules.ui import apply_base_style, render_page_header, render_sidebar_brand


apply_base_style()
render_sidebar_brand()
render_page_header("Conversor", "Em desenvolvimento.")

st.info("Módulo em desenvolvimento.")
