import lxml.etree as ET
from patent_client.epo.ops.session import session

from .schema import NumberServiceResultSchema


class NumberServiceException(Exception):
    pass


def convert_number(number, doc_type="publication", input_format="original", output_format="docdb"):
    """Number Conversion Service
    number: number to convert. Must include at least country and doc number,
        can optionally include kind code or publication date. e.g.
        MD.20050130
        MD.20050130.A
        MD.20050130.A.20050130
        JP.2006-147056.A.20060526
        JP.2006147056.A.20060526
        US.(08/921,321).A.19970829
    doc_type: type of document (publication / application / priority)
    input_format: input type (original / docdb / epodoc)
    output_format: output type (original / docdb / epodoc)

    """
    response = session.get(
        f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/{input_format}/{number}/{output_format}"
    )
    tree = ET.fromstring(response.text.encode())
    result = NumberServiceResultSchema().load(tree)
    errors = [m for m in result.messages if m.kind == "ERROR"]
    if errors:
        raise NumberServiceException("\n".join(str(e) for e in errors))
    return result
