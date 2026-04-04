import json
import os

import pandas as pd
import streamlit as st

from modules.ui import apply_base_style, render_info_panel, render_metric_cards, render_page_header, render_sidebar_brand
from modules.xml.excel_nfe import processar_excel
from modules.xml.xml_nfe import processar_xml


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "clientes.json")


def carregar_clientes():
    with open(CONFIG_PATH, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def inicializar_estado():
    st.session_state.setdefault("xml_processamento", None)


def processar_arquivo(arquivo):
    dados = arquivo.read()
    nome = arquivo.name.lower()
    if nome.endswith(".xml"):
        corrigido, alteracoes = processar_xml(dados)
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
render_sidebar_brand(subtitle="Tratamento fiscal em lote com foco em consistência.")
render_page_header(
    "XML NF-e",
    "Processe espelhos XML e Excel em lote, com reorganização de descrições e rastreabilidade das alterações por item.",
    kicker="Fiscal",
)
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
if cliente:
    st.caption(clientes[cliente]["descricao"])

render_info_panel(
    "Como funciona",
    "O processamento mantém o código do produto na frente da descrição e preserva o excedente no campo complementar quando necessário.",
    chips=["XML", "Excel", "Processamento em lote"],
)

arquivos = st.file_uploader(
    "Envie os arquivos do espelho (XML e/ou Excel)",
    type=["xml", "xlsx"],
    accept_multiple_files=True,
)

if not arquivos:
    render_metric_cards([
        {"label": "Arquivos carregados", "value": "0", "help": "Envie um ou mais arquivos para começar."},
        {"label": "Formatos aceitos", "value": "XML / XLSX", "help": "Os dois formatos podem ser processados juntos."},
        {"label": "Cliente ativo", "value": cliente, "help": "As regras exibidas seguem o cliente selecionado."},
    ])
    st.info("Faça upload de um ou mais arquivos XML ou Excel para processar.")
    st.stop()

render_metric_cards([
    {"label": "Arquivos carregados", "value": len(arquivos), "help": "Todos serão processados na mesma execução."},
    {"label": "Formatos aceitos", "value": "XML / XLSX", "help": "Os dois formatos podem ser enviados juntos."},
    {"label": "Cliente ativo", "value": cliente, "help": "A descrição da regra atual aparece logo acima."},
])

if st.button("Processar arquivos", type="primary", use_container_width=True):
    processamento = {
        "total": len(arquivos),
        "sucesso": 0,
        "com_alteracao": 0,
        "sem_alteracao": 0,
        "resultados": [],
        "erros": [],
    }
    for arquivo in arquivos:
        try:
            resultado = processar_arquivo(arquivo)
        except Exception as exc:
            processamento["erros"].append({"nome": arquivo.name, "erro": str(exc)})
            continue

        processamento["resultados"].append(resultado)
        processamento["sucesso"] += 1
        if resultado["alteracoes"]:
            processamento["com_alteracao"] += 1
        else:
            processamento["sem_alteracao"] += 1

    st.session_state["xml_processamento"] = processamento

processamento = st.session_state.get("xml_processamento")
if not processamento:
    st.stop()

st.divider()

render_metric_cards([
    {"label": "Processados", "value": processamento["sucesso"], "help": f"De {processamento['total']} arquivo(s) enviados."},
    {"label": "Com alteração", "value": processamento["com_alteracao"], "help": "Arquivos com itens reordenados automaticamente."},
    {"label": "Falhas", "value": len(processamento["erros"]), "help": "Arquivos que exigem revisão manual.", "tone": "danger" if processamento["erros"] else ""},
])

for resultado in processamento["resultados"]:
    st.subheader(f"📎 {resultado['nome']}")
    if not resultado["alteracoes"]:
        st.success("Nenhuma alteração necessária. A descrição já estava no formato correto.")
        continue

    st.success(f"{len(resultado['alteracoes'])} item(ns) corrigido(s).")
    df = pd.DataFrame(resultado["alteracoes"])
    df.columns = ["Item", "Código", "Antes", "Depois"]
    with st.expander("Ver alterações (antes/depois)", expanded=True):
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        label=f"⬇️ Baixar {resultado['nome_saida']}",
        data=resultado["saida"],
        file_name=resultado["nome_saida"],
        mime=resultado["mime"],
        key=f"download_{resultado['nome']}",
    )

for erro in processamento["erros"]:
    st.error(f"{erro['nome']}: {erro['erro']}")
