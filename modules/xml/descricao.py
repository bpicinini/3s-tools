import re


LIMITE_XPROD = 120
PREFIXOS_CODIGO = r"(SIN|TEC|CAL|BOR)\d{5,}"
PADRAO_NCM_DETALHADO = re.compile(
    r"\s*-\s*(Tecido de |Calçado |Borracha |Plástico )",
    re.IGNORECASE,
)
PADROES_PREFIXO = [
    r"Tecido de malha de trama circular, recoberto\s+em uma das faces com plástico de poliuretano\s+(?:e com aplicação de glitter\s+)?",
    r"Tecido de malha de trama circular,\s+\d+%\s+.*?\)\s+",
    r"Tecido de malha de trama circular,\s+100% poliéster\s+",
    r"Tecido de malha urdidura, recoberto\s+em uma das faces com plástico de poliuretano\s+",
    r"Tecido de malha urdidura, recoberto\s+com plástico de poliuretano\s+(?:e com aplicação de glitter\s+)?",
]


def encontrar_separador_ncm(texto_completo: str) -> int | None:
    match = PADRAO_NCM_DETALHADO.search(texto_completo)
    return match.start() if match else None


def encontrar_inicio_referencia(parte_produto: str, cprod: str) -> int | None:
    pos_cprod = parte_produto.find(cprod)
    if pos_cprod >= 0:
        return pos_cprod

    match = re.search(PREFIXOS_CODIGO, parte_produto)
    if match:
        return match.start()

    for padrao in PADROES_PREFIXO:
        match = re.match(padrao, parte_produto, re.IGNORECASE)
        if match:
            return match.end()

    return None


def transformar_texto_descricao(texto_completo: str, cprod: str) -> str:
    if not texto_completo or not cprod:
        return texto_completo

    pos_separador = encontrar_separador_ncm(texto_completo)
    if pos_separador is None:
        return texto_completo

    parte_produto = texto_completo[:pos_separador]
    resto = texto_completo[pos_separador:]
    match_sep = re.match(r"\s*-\s*", resto)
    ncm_detalhado = resto[match_sep.end():].strip() if match_sep else resto[3:].strip()

    inicio_ref = encontrar_inicio_referencia(parte_produto, cprod)
    if inicio_ref is None:
        return texto_completo

    referencia = parte_produto[inicio_ref:].strip()
    if not referencia:
        return texto_completo

    if referencia.startswith(cprod):
        return f"{referencia} - {ncm_detalhado}"

    return f"{cprod} - {referencia} - {ncm_detalhado}"


def dividir_descricao(texto: str, limite_xprod: int = LIMITE_XPROD) -> tuple[str, str]:
    return texto[:limite_xprod], texto[limite_xprod:]


def transformar_descricao(xprod: str, inf_ad_prod: str, cprod: str, limite_xprod: int = LIMITE_XPROD) -> tuple[str, str]:
    texto_completo = f"{xprod or ''}{inf_ad_prod or ''}"
    novo_texto = transformar_texto_descricao(texto_completo, cprod)
    return dividir_descricao(novo_texto, limite_xprod=limite_xprod)
