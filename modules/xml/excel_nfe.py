import re
from openpyxl import load_workbook
from io import BytesIO


def _encontrar_separador_ncm(texto):
    """Encontra o separador que antecede a descrição detalhada da NCM."""
    padrao = re.compile(r"\s*-\s*(Tecido de |Calçado |Borracha |Plástico )", re.IGNORECASE)
    match = padrao.search(texto)
    if match:
        return match.start(), match.end() - len(match.group(1))
    return None, None


def _encontrar_inicio_referencia(parte_produto, cprod):
    """Encontra onde começa a referência do produto."""
    pos = parte_produto.find(cprod)
    if pos >= 0:
        return pos

    match = re.search(r"(SIN|TEC|CAL|BOR)\d{5,}", parte_produto)
    if match:
        return match.start()

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


def transformar_descricao_excel(xprod, cprod):
    """Reordena a descrição no Excel: referência na frente, NCM depois."""
    if not xprod or not cprod:
        return xprod

    if xprod.strip().startswith(cprod):
        return xprod

    pos_sep, pos_ncm_text = _encontrar_separador_ncm(xprod)
    if pos_sep is None:
        return xprod

    parte_produto = xprod[:pos_sep]
    ncm_detalhado = xprod[pos_ncm_text:]

    inicio_ref = _encontrar_inicio_referencia(parte_produto, cprod)
    if inicio_ref is None:
        return xprod

    referencia = parte_produto[inicio_ref:].strip()

    if referencia.startswith(cprod):
        return referencia + " - " + ncm_detalhado
    else:
        return cprod + " - " + referencia + " - " + ncm_detalhado


def encontrar_colunas(ws):
    """Encontra os índices das colunas cProd, xProd e infAdProd no header."""
    header = {cell.value: cell.column for cell in ws[1] if cell.value}
    col_cprod = header.get("ns1:cProd")
    col_xprod = header.get("ns1:xProd")
    col_infad = header.get("ns1:infAdProd")
    col_nitem = header.get("nItem")
    return col_nitem, col_cprod, col_xprod, col_infad


def processar_excel(excel_bytes):
    """Processa um Excel de espelho de NF-e, reordenando as descrições.

    Retorna (excel_corrigido_bytes, lista_alteracoes).
    """
    wb = load_workbook(BytesIO(excel_bytes))
    ws = wb.active

    col_nitem, col_cprod, col_xprod, col_infad = encontrar_colunas(ws)

    if not col_cprod or not col_xprod:
        return excel_bytes, []

    alteracoes = []

    for row in range(2, ws.max_row + 1):
        cprod = ws.cell(row=row, column=col_cprod).value
        xprod = ws.cell(row=row, column=col_xprod).value
        nitem = ws.cell(row=row, column=col_nitem).value if col_nitem else row - 1

        if not cprod or not xprod:
            continue

        cprod = str(cprod)
        xprod = str(xprod)

        novo_xprod = transformar_descricao_excel(xprod, cprod)

        if novo_xprod != xprod:
            ws.cell(row=row, column=col_xprod).value = novo_xprod
            alteracoes.append({
                "nItem": str(nitem),
                "cProd": cprod,
                "xProd_antes": xprod[:120] + "..." if len(xprod) > 120 else xprod,
                "xProd_depois": novo_xprod[:120] + "..." if len(novo_xprod) > 120 else novo_xprod,
            })

    output = BytesIO()
    wb.save(output)
    return output.getvalue(), alteracoes
