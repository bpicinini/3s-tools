import json
import os
import streamlit as st
import pandas as pd
from modules.xml.xml_nfe import processar_xml
from modules.xml.excel_nfe import processar_excel

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "clientes.json")


def carregar_clientes():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


st.set_page_config(page_title="XML NF-e — 3S Tools", layout="wide")
st.title("Ajuste de Espelho de Nota Fiscal")

clientes = carregar_clientes()

cliente = st.selectbox("Cliente", options=list(clientes.keys()))
if cliente:
    st.caption(clientes[cliente]["descricao"])

st.divider()

arquivos = st.file_uploader(
    "Envie os arquivos do espelho (XML e/ou Excel)",
    type=["xml", "xlsx"],
    accept_multiple_files=True,
)

if not arquivos:
    st.info("Faça upload de um ou mais arquivos XML ou Excel para processar.")
    st.stop()

if st.button("Processar", type="primary"):
    for arquivo in arquivos:
        st.subheader(f"Arquivo: {arquivo.name}")
        dados = arquivo.read()

        if arquivo.name.lower().endswith(".xml"):
            xml_corrigido, alteracoes = processar_xml(dados)

            if not alteracoes:
                st.success("Nenhuma alteração necessária — descrições já estão no formato correto.")
            else:
                st.success(f"{len(alteracoes)} itens corrigidos.")
                df = pd.DataFrame(alteracoes)
                df.columns = ["Item", "Código", "Antes", "Depois"]
                with st.expander("Ver alterações (antes/depois)", expanded=True):
                    st.dataframe(df, use_container_width=True, hide_index=True)

                nome_saida = arquivo.name.replace(".xml", " CORRIGIDO.xml")
                st.download_button(
                    label=f"Baixar {nome_saida}",
                    data=xml_corrigido,
                    file_name=nome_saida,
                    mime="application/xml",
                )

        elif arquivo.name.lower().endswith(".xlsx"):
            excel_corrigido, alteracoes = processar_excel(dados)

            if not alteracoes:
                st.success("Nenhuma alteração necessária — descrições já estão no formato correto.")
            else:
                st.success(f"{len(alteracoes)} itens corrigidos.")
                df = pd.DataFrame(alteracoes)
                df.columns = ["Item", "Código", "Antes", "Depois"]
                with st.expander("Ver alterações (antes/depois)", expanded=True):
                    st.dataframe(df, use_container_width=True, hide_index=True)

                nome_saida = arquivo.name.replace(".xlsx", " CORRIGIDO.xlsx")
                st.download_button(
                    label=f"Baixar {nome_saida}",
                    data=excel_corrigido,
                    file_name=nome_saida,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
