# ********************************************************************************
# *  WARNING: This code is automatically generated by unasync.py. Do not edit!   *
# ********************************************************************************
import lxml.etree as ET

from ..http_client import PatentClientHttpClient
from .auth import ops_auth
from patent_client import function_cache


class NumberServiceApi:
    http_client = PatentClientHttpClient(auth=ops_auth)

    @classmethod
    @function_cache
    def convert_number(
        cls,
        number,
        doc_type="publication",
        input_format="original",
        output_format="docdb",
    ) -> ET._Element:
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
        response = cls.http_client.get(
            f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/{input_format}/{number}/{output_format}",
        )
        response.raise_for_status()
        return ET.fromstring(response.content)