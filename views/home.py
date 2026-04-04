import streamlit as st

st.markdown("""
<style>
.card-wrap {
    position: relative;
    border-radius: 12px;
}
.card-wrap a {
    position: absolute;
    inset: 0;
    z-index: 10;
    border-radius: 12px;
}
.card {
    background: #f8f9fb;
    border: 1px solid #e3e6ed;
    border-radius: 12px;
    padding: 28px 24px;
    height: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
    cursor: pointer;
}
.card-wrap:hover .card {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(30,58,95,0.15);
    border-color: #1E3A5F;
    background: #ffffff;
}
.card-icon  { font-size: 2.2rem; margin-bottom: 10px; }
.card-title { font-size: 1.15rem; font-weight: 700; color: #1E3A5F; margin-bottom: 6px; }
.card-desc  { font-size: 0.92rem; color: #555; line-height: 1.5; }
.card-badge {
    display: inline-block;
    margin-top: 14px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-active { background: #e6f4ea; color: #2d7a3a; }
.badge-soon   { background: #f0f0f0; color: #888; }
.hero-title { font-size: 2rem; font-weight: 800; color: #1E3A5F; margin-bottom: 4px; }
.hero-sub   { font-size: 1rem; color: #666; margin-bottom: 32px; }

/* Esconder o texto dos page_links mantendo o elemento clicável */
[data-testid="stPageLink"] {
    position: absolute;
    inset: 0;
    opacity: 0;
    z-index: 20;
}
[data-testid="stPageLink"] p { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">🛠️ 3S Tools</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Portal de ferramentas operacionais — 3S Corporate</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-icon">📄</div>
        <div class="card-title">XML NF-e</div>
        <div class="card-desc">Ajuste de espelho de nota fiscal. Reordena as descrições dos itens para o formato correto — referência na frente, NCM depois.</div>
        <span class="card-badge badge-active">✓ Disponível</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("views/xml_nfe.py", label=" ")

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-icon">👥</div>
        <div class="card-title">Sessões TecWin</div>
        <div class="card-desc">Visualize quem está conectado no TecWin e desconecte usuários pendurados com um clique. Limite de 30 minutos por sessão.</div>
        <span class="card-badge badge-active">✓ Disponível</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("views/tecwin_sessoes.py", label=" ")

with col3:
    st.markdown("""
    <div class="card">
        <div class="card-icon">📊</div>
        <div class="card-title">Conversor de Planilhas</div>
        <div class="card-desc">Conversão e padronização de planilhas para formatos utilizados na operação. Em desenvolvimento.</div>
        <span class="card-badge badge-soon">Em breve</span>
    </div>
    """, unsafe_allow_html=True)
