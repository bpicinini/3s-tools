import streamlit as st
import pandas as pd
from modules.tecwin.tecwin import login, listar_usuarios_online, desconectar_usuario, desconectar_pendurados

st.markdown("""
<style>
.page-title { font-size: 1.6rem; font-weight: 800; color: #1E3A5F; margin-bottom: 2px; }
.page-sub   { font-size: 0.95rem; color: #666; margin-bottom: 20px; }
.user-card {
    background: #f8f9fb;
    border: 1px solid #e3e6ed;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.user-card.pendurado {
    background: #fff5f5;
    border-color: #f5c6c6;
}
.user-name  { font-weight: 700; color: #1E3A5F; font-size: 0.97rem; }
.user-info  { font-size: 0.83rem; color: #777; margin-top: 2px; }
.badge-ok   { background: #e6f4ea; color: #2d7a3a; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.badge-pend { background: #fde8e8; color: #c0392b; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.metric-card {
    background: #f0f4fa;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
}
.metric-val  { font-size: 2rem; font-weight: 800; color: #1E3A5F; }
.metric-label { font-size: 0.82rem; color: #666; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">👥 Sessões TecWin</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Monitore e gerencie os usuários conectados ao sistema</div>', unsafe_allow_html=True)

# Credenciais
try:
    TECWIN_LOGIN = st.secrets["TECWIN_LOGIN"]
    TECWIN_SENHA = st.secrets["TECWIN_SENHA"]
    LIMITE_MINUTOS = int(st.secrets.get("TECWIN_LIMITE_MINUTOS", 30))
except Exception:
    st.error("Credenciais TecWin não configuradas. Fale com o administrador do portal.")
    st.stop()

limite = LIMITE_MINUTOS

# Login: só cria nova sessão se não existir uma ativa
if "session" not in st.session_state:
    with st.spinner("Conectando ao TecWin..."):
        try:
            session, portal_login_id = login(TECWIN_LOGIN, TECWIN_SENHA)
            st.session_state["session"] = session
            st.session_state["portal_login_id"] = portal_login_id
        except RuntimeError as e:
            st.error(f"Erro ao conectar: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
            st.stop()

# Buscar usuários
atualizar = st.button("🔄 Atualizar lista")

if "usuarios" not in st.session_state or atualizar:
    with st.spinner("Buscando usuários online..."):
        try:
            portal_login_id = st.session_state.get("portal_login_id")
            usuarios = listar_usuarios_online(st.session_state["session"], excluir_login_id=portal_login_id)
            st.session_state["usuarios"] = usuarios
        except Exception:
            try:
                session, portal_login_id = login(TECWIN_LOGIN, TECWIN_SENHA)
                st.session_state["session"] = session
                st.session_state["portal_login_id"] = portal_login_id
                usuarios = listar_usuarios_online(session, excluir_login_id=portal_login_id)
                st.session_state["usuarios"] = usuarios
            except Exception as e:
                st.error(f"Erro ao buscar usuários: {e}")
                st.stop()

usuarios = st.session_state.get("usuarios", [])
session = st.session_state["session"]

st.divider()

# Métricas
pendurados = [u for u in usuarios if u["minutos"] is not None and u["minutos"] >= limite]
total = len(usuarios)
qtd_pendurados = len(pendurados)
slots_livres = max(0, 8 - total)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val">{total}</div>
        <div class="metric-label">Usuários online</div>
    </div>""", unsafe_allow_html=True)
with c2:
    cor = "#c0392b" if qtd_pendurados > 0 else "#1E3A5F"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val" style="color:{cor}">{qtd_pendurados}</div>
        <div class="metric-label">Pendurados (&gt;{limite} min)</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val">{slots_livres}</div>
        <div class="metric-label">Slots disponíveis (de 8)</div>
    </div>""", unsafe_allow_html=True)

st.divider()

if not usuarios:
    st.info("Nenhum usuário online no momento.")
    st.stop()

# Lista de usuários como cards
st.markdown("#### Usuários conectados")

for u in usuarios:
    pendurado = u["minutos"] is not None and u["minutos"] >= limite
    badge = '<span class="badge-pend">⚠ Pendurado</span>' if pendurado else '<span class="badge-ok">✓ Ativo</span>'
    minutos_txt = f"{u['minutos']} min" if u["minutos"] is not None else "—"
    card_class = "user-card pendurado" if pendurado else "user-card"

    col_info, col_btn = st.columns([5, 1])
    with col_info:
        st.markdown(f"""
        <div class="{card_class}">
            <div>
                <div class="user-name">👤 {u['nome']}</div>
                <div class="user-info">Login: {u['data_login_str']} &nbsp;|&nbsp; {minutos_txt} conectado &nbsp;|&nbsp; IP: {u['ip']}</div>
            </div>
            <div>{badge}</div>
        </div>""", unsafe_allow_html=True)
    with col_btn:
        if pendurado:
            if st.button("Desconectar", key=f"btn_{u['login_id']}", type="primary", use_container_width=True):
                with st.spinner(f"Desconectando {u['nome']}..."):
                    try:
                        sucesso = desconectar_usuario(session, u["login_id"])
                        if sucesso:
                            st.success(f"{u['nome']} desconectado.")
                        else:
                            st.warning(f"Não foi possível desconectar {u['nome']}.")
                        del st.session_state["usuarios"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
        else:
            st.button("Ativo", key=f"btn_{u['login_id']}", disabled=True, use_container_width=True)

st.divider()

# Botão desconectar todos
if qtd_pendurados == 0:
    st.success("Nenhum usuário pendurado. Tudo certo!")
else:
    if st.button(f"⚡ Desconectar todos os pendurados ({qtd_pendurados})", type="primary"):
        with st.spinner("Desconectando..."):
            try:
                portal_login_id = st.session_state.get("portal_login_id")
                desconectados = desconectar_pendurados(session, minutos=limite, excluir_login_id=portal_login_id)
                if desconectados:
                    nomes = ", ".join(d["nome"] for d in desconectados)
                    st.success(f"{len(desconectados)} usuário(s) desconectado(s): {nomes}")
                else:
                    st.warning("Nenhum usuário foi desconectado (talvez já tenham saído).")
                del st.session_state["usuarios"]
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao desconectar: {e}")
