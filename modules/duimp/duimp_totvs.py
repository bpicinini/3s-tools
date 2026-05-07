import re
from datetime import datetime, timezone

from lxml import etree


_UTC = timezone.utc


def _ms_to_utc(ms_str: str) -> datetime | None:
    try:
        return datetime.fromtimestamp(int(ms_str) / 1000, tz=_UTC)
    except (ValueError, TypeError):
        return None


def _fmt_datetime(ms_str: str) -> str:
    dt = _ms_to_utc(ms_str)
    return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else ""


def _text(el, default: str = "") -> str:
    if el is None or el.text is None:
        return default
    return el.text.strip()


def _find_text(root, path: str, default: str = "") -> str:
    parts = path.split("/")
    node = root
    for part in parts:
        if node is None:
            return default
        node = node.find(part)
    return _text(node, default)


def _fmt4(val: str) -> str:
    try:
        return f"{float(val):.4f}"
    except (ValueError, TypeError):
        return "0.0000"


def _fmt2(val: str) -> str:
    try:
        return f"{float(val):.2f}"
    except (ValueError, TypeError):
        return "0.00"


def _fmt5(val: str) -> str:
    try:
        return f"{float(val):.5f}"
    except (ValueError, TypeError):
        return "0.00000"


def _local_desembaraco(descricao: str) -> str:
    prefixes = [
        "AEROPORTO INTERNACIONAL DE ",
        "AEROPORTO DE ",
        "PORTO SECO DE ",
        "PORTO DE ",
    ]
    upper = descricao.upper()
    for prefix in prefixes:
        if upper.startswith(prefix):
            return descricao[len(prefix):].title()
    return descricao.title()


def _extract_br_valor(text: str, pattern: str) -> str:
    m = re.search(pattern, text)
    if not m:
        return "0.0000"
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        return f"{float(raw):.4f}"
    except ValueError:
        return "0.0000"


def _get_tributo_lt(eg, codigo: str):
    for lt in eg.findall("listaTributos"):
        if _find_text(lt, "tributo/codigo") == codigo:
            return lt
    return None


def _get_tributo_tc(ei, codigo: str):
    for tc in ei.findall("tributosCalculados"):
        if _find_text(tc, "tributo/codigo") == codigo:
            return tc
    return None


def _build_item_adicao_map(eg) -> dict[str, str]:
    """Retorna mapeamento de número do item (str) → número da adição (zero-padded)."""
    mapping: dict[str, str] = {}
    for la in eg.findall("listaAdicoes"):
        num_adicao = _find_text(la, "numeroAdicao")
        itens_raw = _find_text(la, "numerosItens")
        for item_num in itens_raw.split(","):
            item_num = item_num.strip()
            if item_num:
                mapping[item_num] = num_adicao.zfill(3)
    return mapping


def _codigo_class_trib(ei) -> str:
    for atr in ei.findall("atributos"):
        nome = _find_text(atr, "nomeApresentacao")
        if "ClassTrib" in nome or "cClassTrib" in nome:
            valor = _find_text(atr, "valor")
            return valor.split(" - ")[0].strip().zfill(6)
    return _find_text(ei, "codigoProduto").zfill(6)


def converter_duimp_totvs(xml_bytes: bytes) -> bytes:
    root = etree.fromstring(xml_bytes)
    eg = root.find("extratoGeral")
    if eg is None:
        raise ValueError("XML não contém bloco <extratoGeral>. Verifique se é uma DUIMP válida.")

    # --- Identificação geral ---
    numero_duimp = _find_text(eg, "numeroDuimp")
    data_duimp = _fmt_datetime(_find_text(eg, "dataRegistro"))

    # Data de desembaraço: evento código 418 no histórico
    data_desembaraco = ""
    for hev in eg.findall("historicoEventos"):
        if _find_text(hev, "codigoEvento") == "418":
            data_desembaraco = _fmt_datetime(_find_text(hev, "dataEvento"))
            break

    uf = _find_text(eg, "identificacao/endereco/uf")
    local = _local_desembaraco(_find_text(eg, "urfDespacho/descricao"))
    cotacao = _fmt4(_find_text(eg, "seguroMoedaNegociadaTaxa"))

    # Taxa Siscomex: tributo código "I"
    taxa_lt = _get_tributo_lt(eg, "I")
    taxa_siscomex = _fmt4(_find_text(taxa_lt, "valorARecolher") if taxa_lt is not None else "")

    # ICMS e Despesas Aduaneiras: extraídos do texto complementar
    info_comp = _find_text(eg, "informacaoComplementar")
    despesas = _extract_br_valor(
        info_comp,
        r"DESPESAS ADUANEIRAS\s+\(TRIBUTADAS\):\s*R\$\s*([\d.]+,\d+)",
    )
    icms = _extract_br_valor(
        info_comp,
        r"ICMS\s+\(.*?\):\s*R\$\s*([\d.]+,\d+)",
    )

    # Frete e Seguro
    carga = eg.find("carga")
    frete = _fmt4(_find_text(carga, "totalFreteReal") if carga is not None else "")
    seguro = _fmt4(_find_text(eg, "seguroValorMoedaReal"))

    # Tributos federais do extrato geral
    ii_lt = _get_tributo_lt(eg, "1")
    ipi_lt = _get_tributo_lt(eg, "2")
    pis_lt = _get_tributo_lt(eg, "6")
    cofins_lt = _get_tributo_lt(eg, "7")

    ii_val = _fmt4(_find_text(ii_lt, "valorARecolher") if ii_lt is not None else "")
    ipi_val = _fmt4(_find_text(ipi_lt, "valorARecolher") if ipi_lt is not None else "")
    pis_val = _fmt4(_find_text(pis_lt, "valorARecolher") if pis_lt is not None else "")
    cofins_val = _fmt4(_find_text(cofins_lt, "valorARecolher") if cofins_lt is not None else "")

    # Totais em dólar e real
    vmle_dolar = _fmt4(_find_text(eg, "vmleDolar"))
    vmle_real = _fmt4(_find_text(eg, "vmleReal"))

    # Total CIF: soma do valor aduaneiro de todos os itens
    total_cif = 0.0
    for ei in root.findall("extratoItens"):
        vmld_val = _find_text(ei, "vmld") or _find_text(ei, "valorMercadoriaCondicaoVendaReal")
        try:
            total_cif += float(vmld_val)
        except (ValueError, TypeError):
            pass
    total_cif_str = f"{total_cif:.4f}"

    item_adicao_map = _build_item_adicao_map(eg)

    # --- Montagem do XML de saída ---
    out = etree.Element("DUIMP")

    def sub(parent, tag: str, text: str = "") -> etree._Element:
        el = etree.SubElement(parent, tag)
        el.text = text
        return el

    sub(out, "NUMERODUIMP", numero_duimp)
    sub(out, "DATADUIMP", data_duimp)
    sub(out, "DATADESEMBARACO", data_desembaraco)
    sub(out, "UFDESEMBARACO", uf)
    sub(out, "LOCALDESEMBARACO", local)
    sub(out, "COTACAODOLAR", cotacao)
    sub(out, "TAXASISCOMEX", taxa_siscomex)
    sub(out, "DESPESASADUANEIRAS", despesas)
    sub(out, "FRETE", frete)
    sub(out, "SEGURO", seguro)
    sub(out, "IPI", ipi_val)
    sub(out, "PIS", pis_val)
    sub(out, "COFINS", cofins_val)
    sub(out, "II", ii_val)
    sub(out, "ICMS", icms)
    sub(out, "TOTALMATERIAISDOLAR", vmle_dolar)
    sub(out, "TOTALMATERIAISREAIS", vmle_real)
    sub(out, "TOTALMATERIAISCIF", total_cif_str)
    sub(out, "INFOCOMPLEMENTARES", info_comp)

    produtos_el = etree.SubElement(out, "PRODUTOS")

    for idx, ei in enumerate(root.findall("extratoItens"), start=1):
        item_el = etree.SubElement(produtos_el, "ITEM")
        item_el.set("IT", str(idx))

        numero_item = _find_text(ei, "numeroItem")
        adicao = item_adicao_map.get(str(numero_item), str(idx).zfill(3))

        sub(item_el, "NUMEROADICAO", adicao)
        sub(item_el, "NUMEROITEM", str(numero_item).zfill(4))
        sub(item_el, "CODIGO", _codigo_class_trib(ei))
        sub(item_el, "DESCRICAO", _find_text(ei, "produto/descricao"))
        sub(item_el, "NCM", _find_text(ei, "ncm/codigo"))
        sub(item_el, "UNIDADE", _find_text(ei, "unidadeComercial"))
        sub(item_el, "QUANTIDADE", _fmt5(_find_text(ei, "quantidadeComercial")))
        sub(item_el, "VALORUNITARIODOLAR", _fmt5(_find_text(ei, "valorUnitarioMoedaNegociada")))

        pis_tc = _get_tributo_tc(ei, "6")
        sub(item_el, "ALIQUOTAPIS", _fmt2(_find_text(pis_tc, "valorAliquota") if pis_tc is not None else ""))
        sub(item_el, "VALORPIS", _fmt2(_find_text(pis_tc, "valorARecolher") if pis_tc is not None else ""))

        cofins_tc = _get_tributo_tc(ei, "7")
        sub(item_el, "ALIQUOTACOFINS", _fmt2(_find_text(cofins_tc, "valorAliquota") if cofins_tc is not None else ""))
        sub(item_el, "VALORCOFINS", _fmt2(_find_text(cofins_tc, "valorARecolher") if cofins_tc is not None else ""))

        ipi_tc = _get_tributo_tc(ei, "2")
        sub(item_el, "ALIQUOTAIPI", _fmt2(_find_text(ipi_tc, "valorAliquota") if ipi_tc is not None else ""))
        sub(item_el, "VALORIPI", _fmt2(_find_text(ipi_tc, "valorARecolher") if ipi_tc is not None else ""))

        ii_tc = _get_tributo_tc(ei, "1")
        sub(item_el, "ALIQUOTAII", _fmt2(_find_text(ii_tc, "valorAliquota") if ii_tc is not None else ""))
        sub(item_el, "VALORII", _fmt2(_find_text(ii_tc, "valorARecolher") if ii_tc is not None else ""))

        sub(item_el, "EXPORTADOR", _find_text(ei, "exportadorNome"))
        sub(item_el, "FABRICANTE", _find_text(ei, "fabricanteNome"))

    return etree.tostring(out, encoding="utf-8", xml_declaration=True, pretty_print=True)
