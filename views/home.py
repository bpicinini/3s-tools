import streamlit as st

from modules.ui import apply_base_style, render_info_panel, render_metric_cards, render_page_header, render_sidebar_brand


apply_base_style()
render_sidebar_brand(subtitle="Atalhos internos para rotinas fiscais e operacionais.")

st.markdown("""
<style>
div[data-testid="stButton"] button {
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(242,247,252,0.98));
    border: 1px solid #d5dfeb;
    border-radius: 20px;
    padding: 28px 24px;
    width: 100%;
    min-height: 250px;
    text-align: left;
    white-space: normal;
    color: #183247;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
    line-height: 1.5;
    box-shadow: 0 12px 30px rgba(22, 50, 79, 0.08);
}

div[data-testid="stButton"] button:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 34px rgba(22, 50, 79, 0.14);
    border-color: #1f4f7a;
    background: #ffffff;
    color: inherit;
}

div[data-testid="stButton"] button:focus {
    box-shadow: 0 16px 34px rgba(22, 50, 79, 0.14);
    border-color: #1f4f7a;
    color: inherit;
}

div[data-testid="stButton"] button p {
    margin: 0;
}

.home-caption {
    color: #5b6773;
    margin: 0.4rem 0 1rem 0;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

render_page_header(
    "3S Tools",
    "Portal interno para tarefas operacionais de alto volume, com foco em agilidade, padronização e menos retrabalho manual.",
    kicker="Suite operacional",
)

render_metric_cards([
    {"label": "Módulos ativos", "value": "2", "help": "XML NF-e e TecWin já estão prontos para uso."},
    {"label": "Em evolução", "value": "1", "help": "Conversor de planilhas preparado para a próxima etapa."},
    {"label": "Objetivo", "value": "Menos cliques", "help": "Ferramentas pensadas para reduzir gargalos da operação."},
])

st.markdown(
    '<p class="home-caption">Escolha um módulo para começar. As telas abaixo já trazem atalhos para as rotinas mais frequentes da equipe.</p>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    if st.button(
        "📄\n\n**XML NF-e**\n\nProcessamento em lote de espelhos XML e Excel para reorganizar descrições dos itens com segurança.\n\n🟢 Disponível",
        key="btn_xml",
    ):
        st.switch_page("views/xml_nfe.py")

with col2:
    if st.button(
        "👥\n\n**Sessões TecWin**\n\nMonitore sessões online, identifique usuários pendurados e libere vagas do ambiente em poucos cliques.\n\n🟢 Disponível",
        key="btn_tecwin",
    ):
        st.switch_page("views/tecwin_sessoes.py")

with col3:
    st.button(
        "📊\n\n**Conversor de Planilhas**\n\nCamada futura para normalização de layouts, validação de colunas e exportações operacionais.\n\n⚪ Em breve",
        key="btn_conversor",
        disabled=True,
    )

st.divider()

render_info_panel(
    "Onde o portal já ajuda hoje",
    "O foco atual está em duas frentes críticas: corrigir arquivos fiscais sem intervenção manual linha a linha e limpar sessões do TecWin antes que elas virem bloqueio para o time.",
    chips=["Processamento em lote", "Visão operacional", "Ações de recuperação rápidas"],
)
