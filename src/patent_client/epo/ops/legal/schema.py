from typing import *

from patent_client.epo.ops.number_service.schema import DocumentIdSchema
from patent_client.epo.ops.util import Schema
from yankee.util import clean_whitespace
from yankee.xml import fields as f

from .national_codes import LegalCodes

code_db = LegalCodes()


def ip_type_formatter(string):
    types = {
        "PI": "Patent of Invention",
        "UM": "Utility Model",
    }
    return types.get(string, None)


def status_of_data_formatter(string):
    types = {"N": "New", "D": "Deleted", "O": "Optional", "C": "Backfile"}
    return types.get(string, None)


class DocumentNumberField(f.Combine):
    country = f.Str(".//ops:L001EP")
    doc_number = f.Str(".//ops:L003EP")
    kind_code = f.Str(".//ops:L004EP")

    def combine_func(self, obj):
        return f"{obj.country}{obj.doc_number}{obj.kind_code}"


class CorrespondingPatentField(f.Combine):
    doc_number = f.Str(".//ops:L503EP")
    country = f.Str(".//ops:L504EP")
    kind_code = f.Str(".//ops:L506EP")

    def combine_func(self, obj):
        if not obj.country and not obj.doc_number:
            return None
        return f"{obj.country}{obj.doc_number}{obj.get('kind_code', '')}"


class MetaDataSchema(Schema):
    status_of_data = f.Str(".//ops:L013", formatter=status_of_data_formatter)
    docdb_publication_number = f.Str(".//ops:L017EP")
    subscriber_exchange_date = f.Date(".//ops:L018EP")
    epo_created_date = f.Date(".//ops:L018EP")
    docdb_integer = f.Int(".//ops:L020EP")


class TextRecord(f.Combine):
    lines = f.List(f.Str(formatter=clean_whitespace), ".//ops:pre")

    def combine_func(self, obj):
        return "\n".join(obj.lines)


class LegalEventSchema(Schema):
    """
    Field descriptions are here:
    https://documents.epo.org/projects/babylon/eponot.nsf/0/EF223017D933B30AC1257B50005A042E/$File/14.11_User_Documentation_3.1_en.pdf

    """

    filing_or_publication = f.Str(".//ops:L002EP")
    document_number = DocumentNumberField()
    ip_type = f.Str(".//ops:L005EP", formatter=ip_type_formatter)
    metadata = MetaDataSchema()
    text_record = TextRecord()

    event_date = f.Date(".//ops:L007EP")
    event_code = f.Str(".//ops:L008EP")
    event_country = f.Str(".//ops:L501EP")
    country_code = f.Str(".//ops:L001EP")
    regional_event_code = f.Str(".//ops:L502EP")

    corresponding_patent = CorrespondingPatentField()
    corresponding_patent_publication_date = f.Date(".//ops:L505EP")

    designated_states = f.Str(".//ops:L507EP")
    extension_name = f.Str(".//ops:L508EP")
    new_owner_name = f.Str(".//ops:L509EP")
    free_text = f.Str(".//ops:L510EP")
    spc_number = f.Str(".//ops:L511EP")
    spc_filing_date = f.Str(".//ops:L512EP")
    expiry = f.Str(".//ops:L513EP")
    publication_language = f.Str(".//ops:L514EP")
    inventor_name = f.Str(".//ops:L515EP")
    ipc_class = f.Str(".//ops:L516EP")
    representative_name = f.Str(".//ops:L517EP")
    payment_date = f.Str(".//ops:L518EP")
    opponent_name = f.Str(".//ops:L519EP")
    year_of_fee_payment = f.Str(".//ops:L520EP")
    name_of_requester = f.Str(".//ops:L522EP")
    date_extension_granted = f.Str(".//ops:L523EP")
    extension_states = f.Str(".//ops:L524EP", formatter=lambda x: x.split(" "))
    effective_date = f.Date(".//ops:L525EP")
    date_of_withdrawal = f.Str(".//ops:L526EP")

    def deserialize(self, obj) -> "Dict":
        obj = super().deserialize(obj)
        if obj.event_code == "REG":
            code_data = code_db.get_code_data(obj.event_country, obj.regional_event_code)
            obj["event_code"] = obj.event_country + "." + obj.regional_event_code
        else:
            code_data = code_db.get_code_data(obj.country_code, obj.event_code)
            obj["event_code"] = obj.country_code + "." + obj.event_code
        obj["event_description"] = code_data["description"]
        return obj


class LegalSchema(Schema):
    publication_reference = DocumentIdSchema(".//ops:patent-family/ops:publication-reference")
    events = f.List(LegalEventSchema, ".//ops:legal")
