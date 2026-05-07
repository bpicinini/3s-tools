import json
import os

import pandas as pd
import streamlit as st

from modules.duimp.duimp_totvs import converter_duimp_totvs
from modules.ui import apply_base_style, render_metric_cards, render_page_header, render_sidebar_brand
from modules.xml.excel_nfe import processar_excel
from modules.xml.xml_nfe import processar_xml


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "clientes.json")


def carregar_clientes():
    with open(CONFIG_PATH, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def inicializar_estado():
    st.session_state.setdefault("xml_processamento", None)


def processar_arquivo_nfe(arquivo, regras=None):
    dados = arquivo.read()
    nome = arquivo.name.lower()
    if nome.endswith(".xml"):
        corrigido, alteracoes = processar_xml(dados, regras=regras)
        mime = "application/xml"
        extensao = ".xml"
    elif nome.endswith(".xlsx"):
        corrigido, alteracoes = processar_excel(dados)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extensao = ".xlsx"
    else:
        raise ValueError("Formato não suportado.")

    nome_saida = arquivo.name.replace(extensao, f" CORRIGIDO{extensao}")
    return {
        "nome": arquivo.name,
        "saida": corrigido,
        "alteracoes": alteracoes,
        "mime": mime,
        "nome_saida": nome_saida,
    }


apply_base_style()
render_sidebar_brand()
render_page_header("Reparador de XML", "Processamento de XML e Excel.")
inicializar_estado()

try:
    clientes = carregar_clientes()
except FileNotFoundError:
    st.error("Arquivo de configuração de clientes não encontrado.")
    st.stop()
except json.JSONDecodeError:
    st.error("O arquivo de clientes está inválido. Revise o JSON de configuração.")
    st.stop()

col1, _ = st.columns([2, 3])
with col1:
    cliente = st.selectbox("Cliente", options=list(clientes.keys()))

cfg_cliente = clientes[cliente]
modo = cfg_cliente.get("modo", "nfe")

# ── Fluxo DUIMP → TOTVS ──────────────────────────────────────────────────────

if modo == "duimp_totvs":
    st.caption(cfg_cliente.get("descricao", ""))

    arquivo = st.file_uploader(
        "XML da DUIMP",
        type=["xml"],
        accept_multiple_files=False,
    )

    if not arquivo:
        st.info("Faça upload do XML de extrato da DUIMP para converter.")
        st.stop()

    render_metric_cards([
        {"label": "Arquivo", "value": arquivo.name},
        {"label": "Saída", "value": "TOTVS XML"},
    ])

    if st.button("Converter DUIMP → TOTVS", type="primary", use_container_width=True):
        try:
            saida = converter_duimp_totvs(arquivo.read())
            nome_saida = arquivo.name.replace(".xml", "_TOTVS.xml").replace(".XML", "_TOTVS.xml")
            st.session_state["xml_processamento"] = {
                "modo": "duimp_totvs",
                "saida": saida,
                "nome_saida": nome_saida,
                "erro": None,
            }
        except Exception as exc:
            st.session_state["xml_processamento"] = {
                "modo": "duimp_totvs",
                "erro": str(exc),
            }

    processamento = st.session_state.get("xml_processamento")
    if not processamento or processamento.get("modo") != "duimp_totvs":
        st.stop()

    st.divider()

    if processamento.get("erro"):
        st.error(f"Erro na conversão: {processamento['erro']}")
        st.stop()

    st.success(f"XML convertido: **{processamento['nome_saida']}**")
    st.download_button(
        label=f"Baixar {processamento['nome_saida']}",
        data=processamento["saida"],
        file_name=processamento["nome_saida"],
        mime="application/xml",
        type="primary",
        use_container_width=True,
    )
    with st.expander("Pré-visualizar XML gerado"):
        st.code(processamento["saida"].decode("utf-8"), language="xml")
    st.stop()

# ── Fluxo NFe: reparo de XML / Excel ─────────────────────────────────────────

arquivos = st.file_uploader(
    "Arquivos",
    type=["xml", "xlsx"],
    accept_multiple_files=True,
)

if not arquivos:
    st.info("Faça upload de um ou mais arquivos XML ou Excel para processar.")
    st.stop()

render_metric_cards([
    {"label": "Arquivos", "value": len(arquivos)},
    {"label": "Formato", "value": "XML / XLSX"},
    {"label": "Cliente", "value": cliente},
])

if st.button("Processar arquivos", type="primary", use_container_width=True):
    processamento = {
        "modo": "nfe",
        "total": len(arquivos),
        "sucesso": 0,
        "com_alteracao": 0,
        "resultados": [],
        "erros": [],
    }
    regras = cfg_cliente.get("regras", [])
    for arquivo in arquivos:
        try:
            resultado = processar_arquivo_nfe(arquivo, regras=regras)
        except Exception as exc:
            processamento["erros"].append({"nome": arquivo.name, "erro": str(exc)})
            continue

        processamento["resultados"].append(resultado)
        processamento["sucesso"] += 1
        if resultado["alteracoes"]:
            processamento["com_alteracao"] += 1

    st.session_state["xml_processamento"] = processamento

processamento = st.session_state.get("xml_processamento")
if not processamento or processamento.get("modo") != "nfe":
    st.stop()

st.divider()

render_metric_cards([
    {"label": "Processados", "value": processamento["sucesso"]},
    {"label": "Alterados", "value": processamento["com_alteracao"]},
    {"label": "Falhas", "value": len(processamento["erros"]), "tone": "danger" if processamento["erros"] else ""},
])

for resultado in processamento["resultados"]:
    st.subheader(f"📎 {resultado['nome']}")
    if not resultado["alteracoes"]:
        st.success("Nenhuma alteração necessária.")
        continue

    st.success(f"{len(resultado['alteracoes'])} item(ns) corrigido(s).")
    df = pd.DataFrame(resultado["alteracoes"])
    df.columns = ["Item", "Código", "Antes", "Depois"]
    with st.expander("Alterações", expanded=True):
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        label=f"Baixar {resultado['nome_saida']}",
        data=resultado["saida"],
        file_name=resultado["nome_saida"],
        mime=resultado["mime"],
        key=f"download_{resultado['nome']}",
    )

for erro in processamento["erros"]:
    st.error(f"{erro['nome']}: {erro['erro']}")
