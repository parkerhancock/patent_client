from patent_client.epo.ops.number_service.schema import DocumentIdSchema
from patent_client.epo.ops.published.schema.biblio import DocDbNumberField
from patent_client.epo.ops.util import Schema
from patent_client.util.xml import ListField
from yankee.xml import fields as f


class PriorityClaimSchema(Schema):
    application_number = DocDbNumberField(".//epo:document-id")
    application_reference = DocumentIdSchema(".//epo:document-id")
    sequence = f.Int("./@sequence")
    kind = f.Str("./@kind")
    active = f.Bool(".//epo:priority-active-indicator", true_value="YES")


class FamilyMemberSchema(Schema):
    publication_number = DocDbNumberField('.//epo:publication-reference/epo:document-id[@document-id-type="docdb"]')
    application_number = DocDbNumberField('.//epo:application-reference/epo:document-id[@document-id-type="docdb"]')
    family_id = f.Str("./@family-id")
    publication_reference = ListField(DocumentIdSchema, ".//epo:publication-reference/epo:document-id")
    application_reference = ListField(DocumentIdSchema, ".//epo:application-reference/epo:document-id")
    priority_claims = ListField(PriorityClaimSchema, ".//epo:priority-claim")


class FamilySchema(Schema):
    publication_reference = DocumentIdSchema(".//ops:patent-family/ops:publication-reference")
    num_records = f.Int(".//ops:patent-family/@total-result-count")
    publication_number = DocDbNumberField(
        './/ops:patent-family/ops:publication-reference/epo:document-id[@document-id-type="docdb"]'
    )
    family_members = ListField(FamilyMemberSchema, ".//ops:family-member")
