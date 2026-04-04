import re
from lxml import etree


NS = {"nfe": "http://www.portalfiscal.inf.br/nfe"}
LIMITE_XPROD = 120


def _encontrar_separador_ncm_detalhado(texto_completo):
    """Encontra o separador ' - ' que antecede a descrição detalhada da NCM.

    A descrição detalhada sempre começa com padrões como
    'Tecido de malha', 'Tecido de', etc.
    """
    padrao = re.compile(r"\s*-\s*(Tecido de |Calçado |Borracha |Plástico )", re.IGNORECASE)
    match = padrao.search(texto_completo)
    if match:
        return match.start()
    return None


def _encontrar_inicio_referencia(parte_produto, cprod):
    """Encontra onde começa a referência do produto dentro do texto.

    Usa o cProd como âncora. Se não encontrar, tenta localizar o
    ponto onde termina o prefixo genérico da NCM.
    """
    pos_cprod = parte_produto.find(cprod)
    if pos_cprod >= 0:
        return pos_cprod

    # cProd não está no texto — procurar padrões de código (SIN/TEC seguido de dígitos)
    match = re.search(r"(SIN|TEC|CAL|BOR)\d{5,}", parte_produto)
    if match:
        return match.start()

    # Último recurso: procurar onde termina o texto genérico da NCM
    padroes_prefixo = [
        r"Tecido de malha de trama circular, recoberto\s+em uma das faces com plástico de poliuretano\s+(?:e com aplicação de glitter\s+)?",
        r"Tecido de malha de trama circular,\s+\d+%\s+.*?\)\s+",
        r"Tecido de malha de trama circular,\s+100% poliéster\s+",
        r"Tecido de malha urdidura, recoberto\s+em uma das faces com plástico de poliuretano\s+",
        r"Tecido de malha urdidura, recoberto\s+com plástico de poliuretano\s+(?:e com aplicação de glitter\s+)?",
    ]
    for padrao in padroes_prefixo:
        match = re.match(padrao, parte_produto, re.IGNORECASE)
        if match:
            return match.end()

    return None


def transformar_descricao(xprod, inf_ad_prod, cprod):
    """Reordena a descrição: referência na frente, texto NCM depois.

    Retorna (novo_xprod, novo_inf_ad_prod).
    """
    texto_completo = xprod + inf_ad_prod

    # Encontrar onde começa a descrição detalhada da NCM
    pos_separador = _encontrar_separador_ncm_detalhado(texto_completo)

    if pos_separador is None:
        return xprod, inf_ad_prod

    parte_produto = texto_completo[:pos_separador]
    resto = texto_completo[pos_separador:]
    match_sep = re.match(r"\s*-\s*", resto)
    ncm_detalhado = resto[match_sep.end():] if match_sep else resto[3:]

    inicio_ref = _encontrar_inicio_referencia(parte_produto, cprod)

    if inicio_ref is None:
        return xprod, inf_ad_prod

    referencia = parte_produto[inicio_ref:].strip()

    if referencia.startswith(cprod):
        novo_texto = referencia + " - " + ncm_detalhado
    else:
        novo_texto = cprod + " - " + referencia + " - " + ncm_detalhado

    novo_xprod = novo_texto[:LIMITE_XPROD]
    novo_inf_ad_prod = novo_texto[LIMITE_XPROD:]

    return novo_xprod, novo_inf_ad_prod


def processar_xml(xml_bytes):
    """Processa um XML de NF-e, reordenando as descrições dos itens.

    Retorna (xml_corrigido_bytes, lista_alteracoes).
    Cada alteração é um dict com nItem, cProd, xProd_antes, xProd_depois.
    """
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.fromstring(xml_bytes, parser)

    alteracoes = []
    itens = tree.findall(".//nfe:det", NS)

    for det in itens:
        n_item = det.get("nItem")
        prod = det.find("nfe:prod", NS)
        cprod_el = prod.find("nfe:cProd", NS)
        xprod_el = prod.find("nfe:xProd", NS)
        inf_ad_el = det.find("nfe:infAdProd", NS)

        if cprod_el is None or xprod_el is None:
            continue

        cprod = cprod_el.text or ""
        xprod_antes = xprod_el.text or ""
        inf_ad_antes = inf_ad_el.text if inf_ad_el is not None else ""

        novo_xprod, novo_inf_ad = transformar_descricao(xprod_antes, inf_ad_antes, cprod)

        if novo_xprod != xprod_antes:
            xprod_el.text = novo_xprod
            if inf_ad_el is not None:
                inf_ad_el.text = novo_inf_ad

            alteracoes.append({
                "nItem": n_item,
                "cProd": cprod,
                "xProd_antes": xprod_antes,
                "xProd_depois": novo_xprod,
            })

    xml_corrigido = etree.tostring(tree, xml_declaration=True, encoding="UTF-8")
    return xml_corrigido, alteracoes
