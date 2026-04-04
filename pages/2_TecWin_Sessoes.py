import streamlit as st
import pandas as pd
from modules.tecwin.tecwin import login, listar_usuarios_online, desconectar_usuario, desconectar_pendurados

st.set_page_config(page_title="Sessões TecWin — 3S Tools", layout="wide")
st.title("Gerenciador de Sessões TecWin")
st.caption("Visualize e desconecte usuários pendurados no sistema.")

# Carregar credenciais dos secrets (nunca expostas ao usuário)
try:
    TECWIN_LOGIN = st.secrets["TECWIN_LOGIN"]
    TECWIN_SENHA = st.secrets["TECWIN_SENHA"]
    LIMITE_MINUTOS = int(st.secrets.get("TECWIN_LIMITE_MINUTOS", 30))
except Exception:
    st.error("Credenciais TecWin não configuradas. Fale com o administrador do portal.")
    st.stop()

st.divider()

col1, col2 = st.columns([3, 1])
with col1:
    limite = st.number_input(
        "Limite de sessão (minutos)",
        min_value=5, max_value=480, value=LIMITE_MINUTOS, step=5,
        help="Usuários conectados há mais tempo que isso serão marcados como pendurados."
    )
with col2:
    st.write("")
    st.write("")
    atualizar = st.button("Atualizar lista", use_container_width=True)

st.divider()

# Buscar usuários (ao carregar ou ao clicar em Atualizar)
if "usuarios" not in st.session_state or atualizar:
    with st.spinner("Conectando ao TecWin..."):
        try:
            session = login(TECWIN_LOGIN, TECWIN_SENHA)
            usuarios = listar_usuarios_online(session)
            st.session_state["usuarios"] = usuarios
            st.session_state["session"] = session
        except RuntimeError as e:
            st.error(f"Erro ao conectar: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
            st.stop()

usuarios = st.session_state.get("usuarios", [])
session = st.session_state.get("session")

if not usuarios:
    st.info("Nenhum usuário online no momento.")
    st.stop()

# Montar DataFrame
linhas = []
for u in usuarios:
    pendurado = u["minutos"] is not None and u["minutos"] >= limite
    linhas.append({
        "Nome": u["nome"],
        "Login às": u["data_login_str"],
        "Tempo (min)": u["minutos"] if u["minutos"] is not None else "—",
        "IP": u["ip"],
        "Status": "PENDURADO" if pendurado else "OK",
        "_login_id": u["login_id"],
        "_pendurado": pendurado,
    })

df = pd.DataFrame(linhas)

pendurados = [u for u in usuarios if u["minutos"] is not None and u["minutos"] >= limite]
total = len(usuarios)
qtd_pendurados = len(pendurados)

m1, m2, m3 = st.columns(3)
m1.metric("Usuários online", total)
m2.metric("Pendurados (>%d min)" % limite, qtd_pendurados)
m3.metric("Slots livres", max(0, 8 - total))

st.divider()

# Colorir linhas penduradas
def colorir_linha(row):
    if row["Status"] == "PENDURADO":
        return ["background-color: #ffd6d6"] * len(row)
    return [""] * len(row)

df_exibir = df[["Nome", "Login às", "Tempo (min)", "IP", "Status"]].copy()
styled = df_exibir.style.apply(colorir_linha, axis=1)

st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    if qtd_pendurados == 0:
        st.success("Nenhum usuário pendurado. Tudo certo!")
    else:
        if st.button(
            f"Desconectar todos os pendurados ({qtd_pendurados})",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Desconectando..."):
                try:
                    desconectados = desconectar_pendurados(session, minutos=limite)
                    if desconectados:
                        nomes = ", ".join(d["nome"] for d in desconectados)
                        st.success(f"{len(desconectados)} usuário(s) desconectado(s): {nomes}")
                    else:
                        st.warning("Nenhum usuário foi desconectado (talvez já tenham saído).")
                    # Limpar cache para atualizar na próxima vez
                    del st.session_state["usuarios"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao desconectar: {e}")

with col_b:
    st.write("**Desconectar individualmente:**")
    for u in usuarios:
        if not u["login_id"]:
            continue
        label = f"{u['nome']} ({u['minutos']} min)" if u["minutos"] is not None else u["nome"]
        pendurado = u["minutos"] is not None and u["minutos"] >= limite
        if pendurado:
            if st.button(f"Desconectar {label}", key=f"btn_{u['login_id']}", use_container_width=True):
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
            st.button(f"{label} — ativo", key=f"btn_{u['login_id']}", disabled=True, use_container_width=True)
