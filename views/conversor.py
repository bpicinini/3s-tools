import streamlit as st

from modules.ui import apply_base_style, render_info_panel, render_metric_cards, render_page_header, render_sidebar_brand


apply_base_style()
render_sidebar_brand(subtitle="Área reservada para as próximas automações de planilhas.")
render_page_header(
    "Conversor de Planilhas",
    "Espaço reservado para a próxima frente do portal: validar layouts, padronizar colunas e gerar saídas prontas para operação.",
    kicker="Roadmap",
)

render_metric_cards([
    {"label": "Status", "value": "Em desenvolvimento", "help": "A base visual e o espaço já estão preparados."},
    {"label": "Próximo passo", "value": "Layouts", "help": "Mapeamento de formatos de entrada e regras de validação."},
    {"label": "Entrega futura", "value": "Conversão guiada", "help": "Fluxo com validação, resumo e exportação do resultado."},
])

render_info_panel(
    "O que faz sentido entrar aqui",
    "Normalização de cabeçalhos, checagem de colunas obrigatórias, validação de tipos e exportação para modelos usados pela equipe.",
    chips=["Validação", "Padronização", "Exportação"],
)

st.info("Este módulo está em desenvolvimento e será liberado em uma próxima etapa.")
