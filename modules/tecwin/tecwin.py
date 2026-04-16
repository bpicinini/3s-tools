"""
Módulo de automação TecWin — gerencia sessões de usuários online.

Fluxo:
1. login() → abre sessão autenticada, retorna (session, portal_login_id)
2. listar_usuarios_online() → retorna lista com nome, dataLogin, tempo, IP
3. desconectar_usuario() → desconecta um usuário pelo loginId
4. desconectar_pendurados() → desconecta todos acima de N minutos
5. forcar_entrada() → tenta login; se limite atingido, desconecta N usuários e retenta
"""

import requests
from datetime import datetime, timedelta, timezone

# Offset fixo para horário de Brasília (UTC-3)
# Evita dependência de tzdata que pode não estar instalado no Streamlit Cloud
BRT_OFFSET = timedelta(hours=-3)

class LimiteConexoesError(RuntimeError):
    """Erro levantado quando o login falha por limite de conexões simultâneas."""

    def __init__(self, message: str, session: requests.Session, response_data: dict):
        super().__init__(message)
        self.session = session
        self.response_data = response_data


BASE_URL = "https://tecwinweb.aduaneiras.com.br"
URL_LOGIN_HANDLER = f"{BASE_URL}/Handlers/Modulos/Usuario/Login.ashx"
URL_CONFIG_HANDLER = f"{BASE_URL}/Handlers/Modulos/Usuario/Configuracoes.ashx"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/Modulos/Usuario/Login.aspx",
}


def login(email: str, senha: str) -> tuple[requests.Session, str | None]:
    """Autentica no TecWin.

    Retorna (session, portal_login_id) onde portal_login_id é o loginId
    da sessão criada pelo portal — deve ser excluído da listagem de usuários.
    Lança RuntimeError se o login falhar.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    resp = session.post(URL_LOGIN_HANDLER, data={
        "action": "2",
        "login": email,
        "senha": senha,
        "salvarLogin": "false",
    }, timeout=15)
    resp.raise_for_status()

    data = resp.json()
    status = data.get("status", "")

    if status != "OK":
        mensagens = {
            "INVALIDO": "Usuário ou senha inválidos.",
            "PRODUTO": "Sem acesso ao produto.",
            "LIMITE": "Limite de usuários simultâneos atingido.",
            "LOGADOS": "Limite de conexões simultâneas atingido.",
            "INADIMPLENTE": "Cadastro inativado (inadimplência).",
            "LIMITE DE TENTATIVAS": "Muitas tentativas de login. Tente mais tarde.",
        }
        msg = mensagens.get(status, f"Falha no login: {status}")
        if status in ("LIMITE", "LOGADOS"):
            raise LimiteConexoesError(msg, session, data)
        raise RuntimeError(msg)

    # Identificar a sessão criada pelo próprio portal:
    # logo após o login, a sessão mais recente na lista é a nossa
    portal_login_id = _capturar_proprio_login_id(session)

    return session, portal_login_id


def _capturar_proprio_login_id(session: requests.Session) -> str | None:
    """Chama action=12 logo após o login para capturar o loginId da sessão do portal.

    A sessão mais recente (maior dataLogin) que ainda não existia antes é a nossa.
    """
    try:
        resp = session.post(URL_CONFIG_HANDLER, data={"action": "12"}, timeout=15)
        filhotes = resp.json().get("listaFilhotes", [])

        # Pegar o mais recente (último da lista ou maior dataLogin)
        mais_recente = None
        mais_recente_dt = None
        for u in filhotes:
            dt = _parsear_data(u.get("dataLogin", ""))
            if dt and (mais_recente_dt is None or dt > mais_recente_dt):
                mais_recente_dt = dt
                mais_recente = str(u.get("loginId", ""))

        return mais_recente
    except Exception:
        return None


def listar_usuarios_online(session: requests.Session, excluir_login_id: str | None = None) -> list[dict]:
    """Retorna lista de usuários atualmente online.

    excluir_login_id: loginId da própria sessão do portal (para não exibir).

    Cada item tem:
    - login_id (str): identificador para desconexão
    - nome (str): nome do usuário
    - empresa (str): empresa
    - data_login (datetime): momento do login
    - data_login_str (str): data formatada para exibição
    - ip (str): IP de origem
    - tipo (str): Administrador / AdministradorAssociado / Normal
    - minutos (int): minutos desde o login
    """
    resp = session.post(URL_CONFIG_HANDLER, data={"action": "12"}, timeout=15)
    resp.raise_for_status()

    data = resp.json()
    filhotes = data.get("listaFilhotes", [])

    usuarios = []
    for u in filhotes:
        login_id = str(u.get("loginId", ""))

        # Ocultar a sessão criada pelo próprio portal
        if excluir_login_id and login_id == excluir_login_id:
            continue

        data_login = _parsear_data(u.get("dataLogin", ""))
        minutos = _calcular_minutos(data_login) if data_login else None

        usuarios.append({
            "login_id": login_id,
            "nome": u.get("nome", ""),
            "empresa": u.get("empresa", ""),
            "data_login": data_login,
            "data_login_str": u.get("dataLogin", ""),
            "ip": u.get("IP", ""),
            "tipo": u.get("tipo", ""),
            "minutos": minutos,
        })

    return usuarios


def _parsear_data(data_str: str) -> datetime | None:
    formatos = ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S"]
    for fmt in formatos:
        try:
            return datetime.strptime(data_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _calcular_minutos(data_login: datetime) -> int:
    # TecWin envia horários em BRT (UTC-3). Comparamos com agora em BRT.
    agora_brt = datetime.now(timezone.utc).astimezone(timezone(BRT_OFFSET)).replace(tzinfo=None)
    delta = agora_brt - data_login
    return max(0, int(delta.total_seconds() / 60))


def desconectar_usuario(session: requests.Session, login_id: str) -> bool:
    """Desconecta um usuário pelo loginId. Retorna True se bem-sucedido."""
    resp = session.post(URL_CONFIG_HANDLER, data={
        "action": "14",
        "loginId": login_id,
    }, timeout=15)
    resp.raise_for_status()

    try:
        data = resp.json()
        return data.get("status", "") == "OK"
    except Exception:
        return resp.status_code == 200


def _extrair_usuarios(filhotes: list) -> list[dict]:
    """Parseia lista de sessões (listaFilhotes) para o formato padrão."""
    usuarios = []
    for u in filhotes:
        data_login = _parsear_data(u.get("dataLogin", ""))
        minutos = _calcular_minutos(data_login) if data_login else None
        usuarios.append({
            "login_id": str(u.get("loginId", "")),
            "nome": u.get("nome", ""),
            "empresa": u.get("empresa", ""),
            "data_login": data_login,
            "data_login_str": u.get("dataLogin", ""),
            "ip": u.get("IP", ""),
            "tipo": u.get("tipo", ""),
            "minutos": minutos,
        })
    return usuarios


def desconectar_pendurados(session: requests.Session, minutos: int = 30, excluir_login_id: str | None = None) -> list[dict]:
    """Desconecta todos os usuários com sessão aberta há mais de N minutos.

    Usuários do tipo 'Administrador' não são desconectados automaticamente.
    Retorna lista de usuários desconectados.
    """
    usuarios = listar_usuarios_online(session, excluir_login_id=excluir_login_id)
    desconectados = []

    for u in usuarios:
        if u["tipo"] == "Administrador":
            continue
        if u["minutos"] is not None and u["minutos"] >= minutos and u["login_id"]:
            sucesso = desconectar_usuario(session, u["login_id"])
            if sucesso:
                desconectados.append(u)

    return desconectados


def forcar_entrada(
    email: str,
    senha: str,
    qtd_desconectar: int = 2,
) -> tuple[requests.Session, str | None, list[dict]]:
    """Tenta login; se o limite de conexões for atingido, desconecta os
    primeiros *qtd_desconectar* usuários (mais ociosos, não-admin) e retenta.

    Retorna (session, portal_login_id, desconectados).
    *desconectados* é a lista de usuários removidos (vazia se não houve necessidade).
    """
    try:
        session, portal_login_id = login(email, senha)
        return session, portal_login_id, []
    except LimiteConexoesError as exc:
        # 1. Tentar obter a lista de usuários da resposta da API
        usuarios = _extrair_usuarios(exc.response_data.get("listaFilhotes", []))

        # 2. Se a resposta não trouxe a lista, tentar buscar via sessão
        if not usuarios:
            try:
                resp = exc.session.post(
                    URL_CONFIG_HANDLER, data={"action": "12"}, timeout=15,
                )
                usuarios = _extrair_usuarios(resp.json().get("listaFilhotes", []))
            except Exception:
                raise exc

        if not usuarios:
            raise exc

        # 3. Ordenar por mais tempo ocioso (candidatos mais prováveis de estarem inativos)
        usuarios_ordenados = sorted(usuarios, key=lambda u: -(u["minutos"] or 0))

        # 4. Filtrar admins — nunca desconectar automaticamente
        candidatos = [u for u in usuarios_ordenados if u["tipo"] != "Administrador"]

        # 5. Desconectar os primeiros N
        desconectados = []
        for u in candidatos[:qtd_desconectar]:
            if u["login_id"]:
                try:
                    if desconectar_usuario(exc.session, u["login_id"]):
                        desconectados.append(u)
                except Exception:
                    pass

        if not desconectados:
            raise exc

        # 6. Retentar login
        session, portal_login_id = login(email, senha)
        return session, portal_login_id, desconectados
