import re

from patent_client.epo.ops.util import Schema
from patent_client.util.claims.parser import ClaimsParser
from yankee.xml import fields as f


class FTDocumentIdSchema(Schema):
    country = f.Str("./ft:country")
    doc_number = f.Str("./ft:doc-number")
    kind = f.Str("./ft:kind")


class ClaimsSchema(Schema):
    document_id = FTDocumentIdSchema(".//ft:document-id")
    claims = f.Str(".//ft:claims", formatter=ClaimsParser().parse)
    claim_text = f.Str(".//ft:claims", formatter=lambda text: text)


class DescriptionField(f.Field):
    format_re = re.compile(r"\s+\n+\s+")

    def post_load(self, obj):
        text = "\n\n".join(p.strip() for p in obj.itertext()).strip()
        return self.format_re.sub("\n\n", text)


class DescriptionSchema(Schema):
    document_id = FTDocumentIdSchema(".//ft:document-id")
    description = DescriptionField(".//ft:description")
