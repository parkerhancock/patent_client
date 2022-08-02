from yankee.util import clean_whitespace
from yankee.xml import fields as f

from patent_client.epo.ops.number_service.schema import DocumentIdSchema
from patent_client.epo.ops.util import Schema
from patent_client.util.xml import ListField


class CpcClassificationSchema(f.Combine):
    section = f.Str("./epo:section")
    klass = f.Str("./epo:class")
    subclass = f.Str("./epo:subclass")
    main_group = f.Str("./epo:main-group")
    subgroup = f.Str("./epo:subgroup")
    value = f.Str("./epo:classification-value")
    generating_office = f.Str("./epo:generating-office")

    def combine_func(self, obj):
        return f"{obj.section}{obj.klass}{obj.subclass} {obj.main_group}/{obj.subgroup}"


class CitationSchema(Schema):
    cited_phase = f.Str("./@cited-phase")
    cited_by = f.Str("./@cited-by")
    epodoc = DocumentIdSchema('.//epo:document-id[@document-id-type="epodoc"]')
    docdb = DocumentIdSchema('.//epo:document-id[@document-id-type="docdb"]')
    original = DocumentIdSchema('.//epo:document-id[@document-id-type="original"]')


class TitleSchema(Schema):
    lang = f.Str("./@lang")
    text = f.Str()


class DocDbNumberField(f.Combine):
    country = f.Str(".//epo:country")
    number = f.Str(".//epo:doc-number")
    kind = f.Str(".//epo:kind")

    def combine_func(self, obj):
        if not obj:
            return None
        return f"{obj.get('country', '')}{obj.number}{obj.get('kind', '')}"


class InpadocBiblioSchema(Schema):
    country = f.Str("./@country")
    doc_number = f.Str("./@doc-number")
    kind = f.Str("./@kind")
    family_id = f.Str("./@family-id")
    publication_number = DocDbNumberField('.//epo:publication-reference/epo:document-id[@document-id-type="docdb"]')
    publication_reference_docdb = DocumentIdSchema(
        './/epo:publication-reference/epo:document-id[@document-id-type="docdb"]'
    )
    publication_reference_epodoc = DocumentIdSchema(
        './/epo:publication-reference/epo:document-id[@document-id-type="epodoc"]'
    )
    publication_reference_original = DocumentIdSchema(
        './/epo:publication-reference/epo:document-id[@document-id-type="original"]'
    )
    application_number = DocDbNumberField('.//epo:application-reference/epo:document-id[@document-id-type="docdb"]')
    application_reference_docdb = DocumentIdSchema(
        './/epo:application-reference/epo:document-id[@document-id-type="docdb"]'
    )
    application_reference_epodoc = DocumentIdSchema(
        './/epo:application-reference/epo:document-id[@document-id-type="epodoc"]'
    )
    application_reference_original = DocumentIdSchema(
        './/epo:application-reference/epo:document-id[@document-id-type="original"]'
    )
    intl_class = ListField(
        f.Str(formatter=clean_whitespace), "./epo:bibliographic-data/epo:classifications-ipcr/epo:classification-ipcr"
    )
    cpc_class = ListField(
        CpcClassificationSchema, './/epo:classification-scheme[@scheme="CPCI"]/ancestor::epo:patent-classification'
    )
    us_class = ListField(
        f.Str(), './/epo:classification-scheme[@scheme="UC"]/following-sibling::epo:classification-symbol'
    )
    priority_claims = ListField(DocumentIdSchema, ".//epo:priority-claim/epo:document-id")
    title = f.Str('.//epo:invention-title[@lang="en"]')
    titles = ListField(TitleSchema, ".//epo:invention-title")
    abstract = f.Str('.//epo:abstract[@lang="en"]')
    citations = ListField(CitationSchema, ".//epo:citation")
    applicants_epodoc = ListField(f.Str(), './/epo:applicant[@data-format="epodoc"]//epo:name')
    applicants_original = ListField(f.Str(), './/epo:applicant[@data-format="original"]//epo:name')
    inventors_epodoc = ListField(f.Str(), './/epo:inventor[@data-format="epodoc"]')
    inventors_original = ListField(f.Str(), './/epo:inventor[@data-format="original"]')


class BiblioResultSchema(Schema):
    documents = ListField(InpadocBiblioSchema, ".//epo:exchange-document")
