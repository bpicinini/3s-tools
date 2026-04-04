import streamlit as st

from modules.tecwin.tecwin import desconectar_pendurados, desconectar_usuario, listar_usuarios_online, login
from modules.ui import apply_base_style, render_info_panel, render_metric_cards, render_page_header, render_sidebar_brand


apply_base_style()
render_sidebar_brand(subtitle="Gestão de sessões e recuperação rápida de slots.")
st.markdown("""
<style>
.user-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(244,248,252,0.97));
    border: 1px solid #d5dfeb;
    border-radius: 18px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.user-card.pendurado {
    background: linear-gradient(180deg, rgba(253,236,235,0.95), rgba(255,255,255,0.98));
    border-color: #f1c7c4;
}

.user-name  { font-weight: 700; color: #16324f; font-size: 0.97rem; }
.user-info  { font-size: 0.83rem; color: #5b6773; margin-top: 2px; }
.badge-ok   { background: #e6f4ea; color: #2d7a3a; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.badge-pend { background: #fde8e8; color: #c0392b; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

render_page_header(
    "Sessões TecWin",
    "Monitore usuários conectados, identifique sessões acima do limite e libere vagas do ambiente com mais segurança.",
    kicker="Acesso",
)


def conectar_tecwin(login_usuario, senha_usuario):
    session, portal_login_id = login(login_usuario, senha_usuario)
    st.session_state["session"] = session
    st.session_state["portal_login_id"] = portal_login_id
    return session, portal_login_id


def listar_com_relogin(login_usuario, senha_usuario):
    try:
        session = st.session_state["session"]
        portal_login_id = st.session_state.get("portal_login_id")
        return listar_usuarios_online(session, excluir_login_id=portal_login_id)
    except Exception:
        session, portal_login_id = conectar_tecwin(login_usuario, senha_usuario)
        return listar_usuarios_online(session, excluir_login_id=portal_login_id)


def executar_desconexao(login_usuario, senha_usuario, acao):
    try:
        return acao(st.session_state["session"])
    except Exception:
        session, _ = conectar_tecwin(login_usuario, senha_usuario)
        return acao(session)


try:
    TECWIN_LOGIN = st.secrets["TECWIN_LOGIN"]
    TECWIN_SENHA = st.secrets["TECWIN_SENHA"]
    LIMITE_MINUTOS = int(st.secrets.get("TECWIN_LIMITE_MINUTOS", 30))
    TOTAL_SLOTS = int(st.secrets.get("TECWIN_TOTAL_SLOTS", 8))
except Exception:
    st.error("Credenciais TecWin não configuradas. Fale com o administrador do portal.")
    st.stop()

if "session" not in st.session_state:
    with st.spinner("Conectando ao TecWin..."):
        try:
            conectar_tecwin(TECWIN_LOGIN, TECWIN_SENHA)
        except RuntimeError as exc:
            st.error(f"Erro ao conectar: {exc}")
            st.stop()
        except Exception as exc:
            st.error(f"Erro inesperado: {exc}")
            st.stop()

render_info_panel(
    "Operação do módulo",
    "A tela exclui a própria sessão do portal da listagem e prioriza o destaque de usuários acima do limite configurado.",
    chips=[f"Limite atual: {LIMITE_MINUTOS} min", f"Capacidade: {TOTAL_SLOTS} slots"],
)

controles_col, filtro_col = st.columns([1, 1])
with controles_col:
    atualizar = st.button("🔄 Atualizar lista", use_container_width=True)
with filtro_col:
    mostrar_so_pendurados = st.checkbox("Mostrar apenas pendurados", value=False)

if "usuarios" not in st.session_state or atualizar:
    with st.spinner("Buscando usuários online..."):
        try:
            st.session_state["usuarios"] = listar_com_relogin(TECWIN_LOGIN, TECWIN_SENHA)
        except Exception as exc:
            st.error(f"Erro ao buscar usuários: {exc}")
            st.stop()

usuarios = st.session_state.get("usuarios", [])
pendurados = [u for u in usuarios if u["minutos"] is not None and u["minutos"] >= LIMITE_MINUTOS]
slots_livres = max(0, TOTAL_SLOTS - len(usuarios))

render_metric_cards([
    {"label": "Usuários online", "value": len(usuarios), "help": "Sessões visíveis no momento."},
    {"label": f"Pendurados (>{LIMITE_MINUTOS} min)", "value": len(pendurados), "help": "Esses usuários aparecem com destaque.", "tone": "danger" if pendurados else ""},
    {"label": f"Slots livres (de {TOTAL_SLOTS})", "value": slots_livres, "help": "Capacidade estimada restante no ambiente."},
])

st.divider()

if not usuarios:
    st.info("Nenhum usuário online no momento.")
    st.stop()

usuarios_ordenados = sorted(
    usuarios,
    key=lambda usuario: (
        not (usuario["minutos"] is not None and usuario["minutos"] >= LIMITE_MINUTOS),
        -(usuario["minutos"] or 0),
        usuario["nome"].lower(),
    ),
)

if mostrar_so_pendurados:
    usuarios_ordenados = [u for u in usuarios_ordenados if u["minutos"] is not None and u["minutos"] >= LIMITE_MINUTOS]

st.markdown("#### Usuários conectados")

for usuario in usuarios_ordenados:
    pendurado = usuario["minutos"] is not None and usuario["minutos"] >= LIMITE_MINUTOS
    badge = '<span class="badge-pend">⚠ Pendurado</span>' if pendurado else '<span class="badge-ok">✓ Ativo</span>'
    minutos_txt = f"{usuario['minutos']} min" if usuario["minutos"] is not None else "—"
    card_class = "user-card pendurado" if pendurado else "user-card"

    col_info, col_btn = st.columns([5, 1])
    with col_info:
        st.markdown(
            f"""
            <div class="{card_class}">
                <div>
                    <div class="user-name">👤 {usuario['nome']}</div>
                    <div class="user-info">Login: {usuario['data_login_str']} &nbsp;|&nbsp; {minutos_txt} conectado &nbsp;|&nbsp; IP: {usuario['ip']} &nbsp;|&nbsp; Tipo: {usuario['tipo'] or 'Não informado'}</div>
                </div>
                <div>{badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_btn:
        if pendurado:
            if st.button("Desconectar", key=f"btn_{usuario['login_id']}", type="primary", use_container_width=True):
                with st.spinner(f"Desconectando {usuario['nome']}..."):
                    try:
                        sucesso = executar_desconexao(
                            TECWIN_LOGIN,
                            TECWIN_SENHA,
                            lambda sessao: desconectar_usuario(sessao, usuario["login_id"]),
                        )
                        if sucesso:
                            st.success(f"{usuario['nome']} desconectado.")
                        else:
                            st.warning(f"Não foi possível desconectar {usuario['nome']}.")
                        st.session_state.pop("usuarios", None)
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Erro: {exc}")
        else:
            st.button("Ativo", key=f"btn_{usuario['login_id']}", disabled=True, use_container_width=True)

st.divider()

if not pendurados:
    st.success("Nenhum usuário pendurado. Tudo certo!")
else:
    if st.button(f"⚡ Desconectar todos os pendurados ({len(pendurados)})", type="primary"):
        with st.spinner("Desconectando..."):
            try:
                portal_login_id = st.session_state.get("portal_login_id")
                desconectados = executar_desconexao(
                    TECWIN_LOGIN,
                    TECWIN_SENHA,
                    lambda sessao: desconectar_pendurados(sessao, minutos=LIMITE_MINUTOS, excluir_login_id=portal_login_id),
                )
                if desconectados:
                    nomes = ", ".join(d["nome"] for d in desconectados)
                    st.success(f"{len(desconectados)} usuário(s) desconectado(s): {nomes}")
                else:
                    st.warning("Nenhum usuário foi desconectado (talvez já tenham saído).")
                st.session_state.pop("usuarios", None)
                st.rerun()
            except Exception as exc:
                st.error(f"Erro ao desconectar: {exc}")
