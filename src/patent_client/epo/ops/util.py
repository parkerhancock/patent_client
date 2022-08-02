from patent_client.util.xml import Schema as XmlSchema
from patent_client.util import one_to_one, Model

class Schema(XmlSchema):
    class Meta:
        namespaces = {
        "ops": "http://ops.epo.org",
        "epo": "http://www.epo.org/exchange",
        "ft": "http://www.epo.org/fulltext",
    }


class InpadocModel(Model):
    biblio = one_to_one("patent_client.epo.ops.published.model.InpadocBiblio", doc_number="docdb_number")
    claims = one_to_one("patent_client.epo.ops.published.model.Claims", attribute="claims", doc_number="docdb_number")
    claim_text = one_to_one("patent_client.epo.ops.published.model.Claims", attribute="claim_text", doc_number="docdb_number")
    description = one_to_one("patent_client.epo.ops.published.model.Description", attribute="description", doc_number="docdb_number")
    family = one_to_one("patent_client.epo.ops.family.model.Family", attribute="family_members", doc_number="docdb_number")
    images = one_to_one("patent_client.epo.ops.published.model.Images", doc_number="docdb_number")
    legal = one_to_one("patent_client.epo.ops.legal.model.Legal", doc_number="docdb_number")