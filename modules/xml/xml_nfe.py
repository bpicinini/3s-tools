from lxml import etree

from modules.xml.descricao import transformar_descricao


NS = {"nfe": "http://www.portalfiscal.inf.br/nfe"}


def _criar_ou_atualizar_inf_ad_prod(det, prod, inf_ad_el, novo_inf_ad):
    if inf_ad_el is not None:
        inf_ad_el.text = novo_inf_ad or None
        return

    if not novo_inf_ad:
        return

    novo_el = etree.Element(f"{{{NS['nfe']}}}infAdProd")
    novo_el.text = novo_inf_ad
    indice_prod = list(det).index(prod)
    det.insert(indice_prod + 1, novo_el)


def _remover_horario_data(tree, campos, alteracoes):
    for campo in campos:
        for el in tree.findall(f".//nfe:{campo}", NS):
            valor = el.text or ""
            if "T" in valor:
                novo_valor = valor[:10]
                el.text = novo_valor
                alteracoes.append({
                    "nItem": campo,
                    "cProd": "",
                    "xProd_antes": valor,
                    "xProd_depois": novo_valor,
                })


def processar_xml(xml_bytes, regras=None):
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.fromstring(xml_bytes, parser)

    alteracoes = []

    for regra in regras or []:
        if regra.get("tipo") == "remover_horario_data":
            _remover_horario_data(tree, regra.get("campos", []), alteracoes)

    itens = tree.findall(".//nfe:det", NS)

    for det in itens:
        n_item = det.get("nItem")
        prod = det.find("nfe:prod", NS)
        if prod is None:
            continue

        cprod_el = prod.find("nfe:cProd", NS)
        xprod_el = prod.find("nfe:xProd", NS)
        inf_ad_el = det.find("nfe:infAdProd", NS)

        if cprod_el is None or xprod_el is None:
            continue

        cprod = cprod_el.text or ""
        xprod_antes = xprod_el.text or ""
        inf_ad_antes = inf_ad_el.text if inf_ad_el is not None else ""

        novo_xprod, novo_inf_ad = transformar_descricao(xprod_antes, inf_ad_antes, cprod)

        if novo_xprod != xprod_antes or novo_inf_ad != inf_ad_antes:
            xprod_el.text = novo_xprod
            _criar_ou_atualizar_inf_ad_prod(det, prod, inf_ad_el, novo_inf_ad)
            alteracoes.append({
                "nItem": n_item,
                "cProd": cprod,
                "xProd_antes": xprod_antes,
                "xProd_depois": novo_xprod,
            })

    xml_corrigido = etree.tostring(tree, xml_declaration=True, encoding="UTF-8")
    return xml_corrigido, alteracoes
