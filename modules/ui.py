import html

import streamlit as st


BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');

:root {
    --brand-900: #1f3550;
    --brand-700: #33567d;
    --brand-500: #5279a3;
    --accent-500: #d59d41;
    --surface-app: #f6f2eb;
    --surface-0: #ffffff;
    --surface-1: #f3eee6;
    --border-1: #e4ddd1;
    --border-2: #d8cfbf;
    --text-1: #1f2933;
    --text-2: #6e6254;
    --shadow-soft: 0 10px 24px rgba(31, 53, 80, 0.06);
}

html, body, [class*="css"] {
    font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
}

.stApp {
    background: var(--surface-app);
    color: var(--text-1);
}

.main .block-container {
    padding-top: 1.35rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: #fffdfa;
    border-right: 1px solid var(--border-1);
}

[data-testid="stSidebar"] * {
    color: var(--text-1);
}

[data-testid="stSidebarNav"] {
    padding-top: 0.35rem;
}

[data-testid="stSidebarNav"] a {
    border-radius: 10px;
    margin-bottom: 0.12rem;
}

[data-testid="stSidebarNav"] a:hover {
    background: #f5efe6;
}

[data-testid="stSidebarNav"] a[data-testid="stSidebarNavLink-currentPage"] {
    background: #f1ebe2;
    color: var(--brand-900);
    font-weight: 700;
}

.sidebar-brand {
    margin: 0 0 1rem 0;
    padding: 0.15rem 0.1rem 1rem 0.1rem;
    border-bottom: 1px solid var(--border-1);
}

.sidebar-brand-title {
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.02em;
    color: var(--brand-900);
}

.sidebar-brand-title span {
    color: var(--accent-500);
}

.sidebar-brand-subtitle {
    margin-top: 0.35rem;
    font-size: 0.8rem;
    color: var(--text-2);
}

.page-hero {
    padding: 1rem 1.2rem;
    border: 1px solid var(--border-1);
    border-radius: 16px;
    background: var(--surface-0);
    box-shadow: var(--shadow-soft);
    margin-bottom: 1rem;
}

.page-kicker {
    margin-bottom: 0.2rem;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-2);
}

.page-title {
    margin: 0;
    color: var(--brand-900);
    font-size: 1.45rem;
    line-height: 1.05;
    font-weight: 800;
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
}

.page-subtitle {
    margin: 0.22rem 0 0 0;
    color: var(--text-2);
    font-size: 0.9rem;
    line-height: 1.45;
}

.metric-card {
    background: var(--surface-0);
    border: 1px solid var(--border-1);
    border-radius: 14px;
    padding: 0.85rem 1rem;
    box-shadow: var(--shadow-soft);
    min-height: 84px;
}

.metric-card.metric-danger {
    background: #fffaf6;
}

.metric-label {
    color: var(--text-2);
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 700;
}

.metric-value {
    color: var(--brand-900);
    font-size: 1.55rem;
    line-height: 1.05;
    font-weight: 800;
    margin-top: 0.35rem;
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
}

.metric-help {
    color: var(--text-2);
    font-size: 0.8rem;
    margin-top: 0.35rem;
    line-height: 1.35;
}

.info-panel {
    background: var(--surface-0);
    border: 1px solid var(--border-1);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    box-shadow: var(--shadow-soft);
}

.info-panel h3 {
    margin: 0 0 0.3rem 0;
    color: var(--brand-900);
    font-size: 0.98rem;
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
}

.info-panel p {
    margin: 0;
    color: var(--text-2);
    line-height: 1.45;
}

.chip-row {
    display: flex;
    gap: 0.45rem;
    flex-wrap: wrap;
    margin-top: 0.6rem;
}

.info-chip {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 0.2rem 0.6rem;
    background: var(--surface-1);
    color: var(--brand-900);
    font-size: 0.76rem;
    font-weight: 700;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 12px;
    border: 1px solid var(--border-2);
    box-shadow: none;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--brand-500);
}

.stButton > button[kind="primary"],
.stDownloadButton > button {
    background: var(--brand-900);
    color: #ffffff;
}

[data-testid="stFileUploader"] {
    background: var(--surface-0);
    border: 1px dashed var(--border-2);
    border-radius: 14px;
    padding: 0.35rem;
}

[data-testid="stFileUploader"] section {
    border: none;
}

[data-testid="stExpander"] {
    background: var(--surface-0);
    border: 1px solid var(--border-1);
    border-radius: 14px;
}

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--border-1);
}

.streamlit-expanderHeader {
    font-weight: 700;
    color: var(--brand-900);
}

.stAlert {
    border-radius: 12px;
}
</style>
"""


def apply_base_style() -> None:
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def render_sidebar_brand(title: str = "3S Tools", subtitle: str | None = None) -> None:
    with st.sidebar:
        st.markdown("## 3S Tools")
        if subtitle:
            st.caption(subtitle)
        st.divider()


def render_page_header(title: str, subtitle: str | None = None, kicker: str | None = None) -> None:
    if kicker:
        st.caption(kicker)
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
    st.divider()


def render_metric_cards(metrics: list[dict]) -> None:
    columns = st.columns(len(metrics))
    for column, metric in zip(columns, metrics):
        with column:
            st.metric(str(metric["label"]), str(metric["value"]))
            help_text = metric.get("help")
            if help_text:
                st.caption(help_text)


def render_info_panel(title: str, body: str, chips: list[str] | None = None) -> None:
    texto = body
    if chips:
        texto = body + "\n\n" + " • ".join(chips)
    st.info(f"**{html.escape(title)}**\n\n{html.escape(texto)}")
