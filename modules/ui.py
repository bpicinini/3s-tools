import html

import streamlit as st


BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');

:root {
    --brand-900: #16324f;
    --brand-700: #1f4f7a;
    --brand-500: #2f7cb5;
    --accent-500: #d6842a;
    --surface-0: #ffffff;
    --surface-1: #f5f8fc;
    --surface-2: #eaf1f8;
    --border-1: #d5dfeb;
    --text-1: #183247;
    --text-2: #5b6773;
    --shadow-soft: 0 16px 40px rgba(22, 50, 79, 0.08);
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(47, 124, 181, 0.12), transparent 28%),
        radial-gradient(circle at top right, rgba(214, 132, 42, 0.10), transparent 24%),
        linear-gradient(180deg, #f8fbff 0%, #f4f7fb 100%);
    font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
}

.main .block-container {
    padding-top: 2.2rem;
    padding-bottom: 2.5rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #16324f 0%, #1f4f7a 100%);
}

[data-testid="stSidebar"] * {
    color: #f6fbff;
}

[data-testid="stSidebarNav"] {
    padding-top: 0.3rem;
}

[data-testid="stSidebarNav"] a {
    border-radius: 14px;
    transition: background 0.2s ease, transform 0.2s ease;
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 255, 255, 0.10);
    transform: translateX(2px);
}

[data-testid="stSidebarNav"] a[data-testid="stSidebarNavLink-currentPage"] {
    background: rgba(255, 255, 255, 0.16);
    font-weight: 700;
}

.sidebar-brand {
    margin: 0.4rem 0 1rem 0;
    padding: 1rem 1rem 0.95rem 1rem;
    border-radius: 18px;
    background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(255,255,255,0.06));
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
}

.sidebar-brand-title {
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 0.01em;
}

.sidebar-brand-subtitle {
    margin-top: 0.28rem;
    font-size: 0.84rem;
    line-height: 1.45;
    color: rgba(246, 251, 255, 0.82);
}

.page-hero {
    position: relative;
    padding: 1.4rem 1.6rem;
    border-radius: 22px;
    border: 1px solid rgba(22, 50, 79, 0.08);
    background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(245, 248, 252, 0.96)),
        linear-gradient(90deg, rgba(47, 124, 181, 0.12), rgba(214, 132, 42, 0.08));
    box-shadow: var(--shadow-soft);
    margin-bottom: 1.25rem;
    overflow: hidden;
    animation: fadeUp 0.45s ease;
}

.page-hero::after {
    content: "";
    position: absolute;
    inset: auto 0 0 0;
    height: 4px;
    background: linear-gradient(90deg, var(--brand-500), var(--accent-500));
    opacity: 0.9;
}

.page-kicker {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    border-radius: 999px;
    padding: 0.32rem 0.7rem;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    background: rgba(22, 50, 79, 0.08);
    color: var(--brand-900);
    margin-bottom: 0.85rem;
}

.page-title {
    margin: 0;
    color: var(--text-1);
    font-size: 2rem;
    line-height: 1.1;
    font-weight: 800;
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
}

.page-subtitle {
    margin: 0.55rem 0 0 0;
    color: var(--text-2);
    font-size: 1rem;
    line-height: 1.55;
    max-width: 52rem;
}

.metric-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(240, 246, 252, 0.92));
    border: 1px solid var(--border-1);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    min-height: 106px;
    box-shadow: 0 10px 24px rgba(22, 50, 79, 0.06);
    animation: fadeUp 0.55s ease;
}

.metric-card.metric-danger {
    background: linear-gradient(180deg, rgba(253,236,235,0.95), rgba(255,255,255,0.98));
}

.metric-label {
    color: var(--text-2);
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 700;
}

.metric-value {
    color: var(--brand-900);
    font-size: 1.95rem;
    line-height: 1.05;
    font-weight: 800;
    margin-top: 0.45rem;
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
}

.metric-help {
    color: var(--text-2);
    font-size: 0.84rem;
    margin-top: 0.55rem;
    line-height: 1.4;
}

.info-panel {
    background: rgba(255,255,255,0.9);
    border: 1px solid var(--border-1);
    border-radius: 18px;
    padding: 1rem 1.15rem;
    box-shadow: 0 8px 22px rgba(22, 50, 79, 0.05);
    animation: fadeUp 0.65s ease;
}

.info-panel h3 {
    margin: 0 0 0.4rem 0;
    color: var(--brand-900);
    font-size: 1rem;
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
}

.info-panel p {
    margin: 0;
    color: var(--text-2);
    line-height: 1.55;
}

.chip-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
}

.info-chip {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 0.34rem 0.7rem;
    background: var(--surface-2);
    color: var(--brand-900);
    font-size: 0.82rem;
    font-weight: 700;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 14px;
    border: 1px solid var(--border-1);
    box-shadow: 0 10px 24px rgba(22, 50, 79, 0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(31, 79, 122, 0.45);
    box-shadow: 0 14px 26px rgba(22, 50, 79, 0.10);
}

.stDownloadButton > button {
    background: linear-gradient(180deg, #214d76, #16324f);
    color: #f8fbff;
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.8);
    border: 1px dashed rgba(31, 79, 122, 0.35);
    border-radius: 18px;
    padding: 0.5rem;
}

[data-testid="stFileUploader"] section {
    border: none;
}

.streamlit-expanderHeader {
    font-family: "Manrope", "IBM Plex Sans", sans-serif;
    font-weight: 700;
    color: var(--brand-900);
}

[data-testid="stExpander"] {
    background: rgba(255,255,255,0.75);
    border: 1px solid var(--border-1);
    border-radius: 18px;
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(22, 50, 79, 0.08);
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
"""


def apply_base_style() -> None:
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def render_sidebar_brand(title: str = "3S Tools", subtitle: str = "Portal operacional com foco em velocidade e clareza.") -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <section class="sidebar-brand">
                <div class="sidebar-brand-title">{html.escape(title)}</div>
                <div class="sidebar-brand-subtitle">{html.escape(subtitle)}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )


def render_page_header(title: str, subtitle: str, kicker: str | None = None) -> None:
    kicker_html = (
        f'<div class="page-kicker">{html.escape(kicker)}</div>'
        if kicker
        else ""
    )
    st.markdown(
        f"""
        <section class="page-hero">
            {kicker_html}
            <h1 class="page-title">{html.escape(title)}</h1>
            <p class="page-subtitle">{html.escape(subtitle)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: list[dict]) -> None:
    columns = st.columns(len(metrics))
    for column, metric in zip(columns, metrics):
        tone = metric.get("tone", "")
        tone_class = f" metric-{tone}" if tone else ""
        help_text = metric.get("help")
        help_html = f'<div class="metric-help">{html.escape(help_text)}</div>' if help_text else ""
        with column:
            st.markdown(
                f"""
                <div class="metric-card{tone_class}">
                    <div class="metric-label">{html.escape(str(metric["label"]))}</div>
                    <div class="metric-value">{html.escape(str(metric["value"]))}</div>
                    {help_html}
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_info_panel(title: str, body: str, chips: list[str] | None = None) -> None:
    chip_html = ""
    if chips:
        chip_html = '<div class="chip-row">' + "".join(
            f'<span class="info-chip">{html.escape(chip)}</span>' for chip in chips
        ) + "</div>"
    st.markdown(
        f"""
        <section class="info-panel">
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(body)}</p>
            {chip_html}
        </section>
        """,
        unsafe_allow_html=True,
    )
