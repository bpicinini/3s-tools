"""
Módulo de automação TecWin — gerencia sessões de usuários online.

Fluxo:
1. login() → abre sessão autenticada
2. listar_usuarios_online() → retorna lista com nome, dataLogin, tempo, IP
3. desconectar_usuario() → desconecta um usuário pelo loginId
4. desconectar_pendurados() → desconecta todos acima de N minutos
"""

import requests
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_BR = ZoneInfo("America/Sao_Paulo")

BASE_URL = "https://tecwinweb.aduaneiras.com.br"
URL_LOGIN_HANDLER = f"{BASE_URL}/Handlers/Modulos/Usuario/Login.ashx"
URL_CONFIG_HANDLER = f"{BASE_URL}/Handlers/Modulos/Usuario/Configuracoes.ashx"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/Modulos/Usuario/Login.aspx",
}


def login(email: str, senha: str) -> requests.Session:
    """Autentica no TecWin e retorna a sessão com cookies ativos.

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
        raise RuntimeError(mensagens.get(status, f"Falha no login: {status}"))

    return session


def listar_usuarios_online(session: requests.Session) -> list[dict]:
    """Retorna lista de usuários atualmente online.

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


def _parsear_data(data_str: str) -> datetime | None:
    formatos = ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S"]
    for fmt in formatos:
        try:
            return datetime.strptime(data_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _calcular_minutos(data_login: datetime) -> int:
    # Usa horário de Brasília para comparar com os tempos enviados pelo TecWin
    agora = datetime.now(TZ_BR).replace(tzinfo=None)
    delta = agora - data_login
    return int(delta.total_seconds() / 60)


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


def desconectar_pendurados(session: requests.Session, minutos: int = 30) -> list[dict]:
    """Desconecta todos os usuários com sessão aberta há mais de N minutos.

    Usuários do tipo 'Administrador' não são desconectados automaticamente.
    Retorna lista de usuários desconectados.
    """
    usuarios = listar_usuarios_online(session)
    desconectados = []

    for u in usuarios:
        if u["tipo"] == "Administrador":
            continue
        if u["minutos"] is not None and u["minutos"] >= minutos and u["login_id"]:
            sucesso = desconectar_usuario(session, u["login_id"])
            if sucesso:
                desconectados.append(u)

    return desconectados
