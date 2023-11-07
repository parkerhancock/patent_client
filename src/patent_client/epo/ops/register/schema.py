from yankee.xml import fields as f
from patent_client.epo.ops.util import Schema
from patent_client.util.xml import ListField

# EP Register Schema at http://ops.epo.org/schema/rplus.xsd

class TitleSchema(Schema):
    title = f.Str("./text()")
    language = f.Str("./@lang")

class EpoResultSchema(Schema):
    publication_number = f.Str("./reg:bibliographic-data/reg:publication-reference/reg:document-id/reg:doc-number", formatter=lambda s: "EP" + s)
    publication_date = f.Date("./reg:bibliographic-data/reg:publication-reference/reg:document-id/reg:date")
    application_number = f.Str("./reg:bibliographic-data/reg:application-reference/reg:document-id/reg:doc-number", formatter=lambda s: "EP" + s)
    title = f.Str('./reg:bibliographic-data/reg:invention-title[@lang="en"]')
    title_localized = ListField(TitleSchema, './reg:bibliographic-data/reg:invention-title')
    applicants = ListField(f.Str, "./reg:bibliographic-data/reg:parties/reg:applicants/reg:applicant/reg:addressbook/reg:name")
    agents = ListField(f.Str, "./reg:bibliographic-data/reg:parties/reg:agents/reg:agent/reg:addressbook/reg:name")

class EpoSearchSchema(Schema):
    query = f.Str(".//ops:register-search/ops:query")
    num_results = f.Int(".//ops:register-search/@total-result-count")
    begin = f.Int(".//ops:register-search/ops:range/@begin")
    end = f.Int(".//ops:register-search/ops:range/@end")
    results = ListField(EpoResultSchema, ".//ops:register-search/reg:register-documents/reg:register-document")

class StatusSchema(Schema):
    date = f.Date("./@change-date")
    code = f.Str("./@status-code")
    description = f.Str("./text()")

class DocumentIdSchema(Schema):
    language = f.Str('./@lang')
    country = f.Str("./reg:country")
    number = f.Str("./reg:doc-number")
    kind = f.Str("./reg:kind")
    date = f.Date("./reg:date")

class PublicationSchema(Schema):
    gazette_number = f.Str("./@change-gazette-num")
    language = f.Str('./reg:document-id/@lang')
    country = f.Str("./reg:document-id/reg:country")
    number = f.Str("./reg:document-id/reg:doc-number")
    kind = f.Str("./reg:document-id/reg:kind")
    date = f.Date("./reg:document-id/reg:date")

class AddressField(f.Combine):
    line_one = f.Str("./reg:address-1")
    line_two = f.Str("./reg:address-1")
    country = f.Str("./reg:country")

    def combine_func(self, obj):
        if not obj:
            return None
        street = f"{obj.get('line_one', '')}\n{obj.get('line_two', '')}"
        if obj.country:
            return street + f" [{obj.country}]"
        return street

class PersonSchema(Schema):
    name = f.Str("./reg:addressbook/reg:name")
    address = AddressField("./reg:addressbook/reg:address")
    change_date = f.Date("./ancestor::reg:agents/@change-date")
    change_gazette_num = f.Str("./ancestor::reg:agents/@change-gazette-num")

class ApplicantSchema(PersonSchema):
    type = f.Str("./@app-type")
    designation = f.Str("./@designation")
    sequence = f.Int("./@sequence")

class InventorSchema(PersonSchema):
    sequence = f.Int("./@sequence")

class AgentSchema(PersonSchema):
    pass

class PriorityClaimSchema(Schema):
    country = f.Str("./reg:country")
    document_number = f.Str("./reg:doc-number")
    date = f.Date("./reg:date")
    kind = f.Str("./@kind")
    seq = f.Int("./@sequence")

class LapsedSchema(Schema):
    country = f.Str("./reg:country")
    date = f.Date("./reg:date")

class DateRightsEffectiveSchema(Schema):
    date_entering_into_force = f.Date("./reg:date-entering-into-force")
    first_examination_report_despatched = f.Date(".//reg:first-examination-report-despatched")
    notification_of_rights_after_appeal = f.Date(".//reg:notification-of-rights-after-appeal")
    patent_maintained_as_amended = f.Date(".//reg:patent-maintained-as-amended")
    proceedings_interrupted = f.Date(".//reg:proceedings-interrupted")
    proceedings_resumed = f.Date(".//reg:proceedings-resumed")
    proceedings_stay = f.Date(".//reg:proceedings-stay")
    request_for_conversion_to_national_application = f.Date(".//reg:request-for-conversion-to-national-application")
    request_for_examination = f.Date(".//reg:request-for-examination")

class CitationSchema(Schema):
    cited_phase = f.Str("./@cited-phase")
    office = f.Str("./@office")
    document = DocumentIdSchema("./reg:patcit/reg:document-id")
    text = f.Str("./reg:patcit/reg:text")
    category = f.Str("./reg:category")
    npl_citation = f.Str(".//reg:nplcit/*[self::reg:article or self::reg:book or self::reg:online or self::reg:othercit or self::reg:text]")
    npl_type = f.Str(".//reg:nplcit/reg:npl-type")
    doi = f.Str(".//reg:doi")
    
class EpoDocumentSubSchema(Schema):
    """Omitted Elements
        ./reg:bibliographic-data/plain-language-classification
        ./reg:bibliographic-data/classification-ipc
        ./reg:bibliographic-data/classification-ipcr
        ./reg:bibliographic-data/classification-national
        ./reg:bibliographic-data/classification-locarno
        ./reg:bibliographic-data/classification-udc
    """
    # Bibliographic Data
    register_id = f.Str("./reg:bibliographic-data/@id")
    lang = f.Str("./reg:bibliographic-data/@lang")
    status = f.Str("./reg:bibliographic-data/@status")
    publications = ListField(PublicationSchema, "./reg:bibliographic-data/reg:publication-reference")
    application_number = f.Str("./reg:bibliographic-data/reg:application-reference/reg:document-id/reg:doc-number", formatter=lambda s: "EP" + s)
    filing_language = f.Str("./reg:bibliographic-data/reg:language-of-filing")
    priority_claims = ListField(PriorityClaimSchema, "./reg:bibliographic-data/reg:priority-claims/reg:priority-claim")
    
    applicants = ListField(ApplicantSchema, "./reg:bibliographic-data/reg:parties/reg:applicants[1]/reg:applicant")
    inventors = ListField(InventorSchema, "./reg:bibliographic-data/reg:parties/reg:inventors[1]/reg:inventor")
    agent = AgentSchema("./reg:bibliographic-data/reg:parties/reg:agents[1]/reg:agent")
    agent_history = ListField(AgentSchema, "./reg:bibliographic-data/reg:parties/reg:agents/reg:agent")
    title = f.Str('./reg:bibliographic-data/reg:invention-title[@lang="en"]')
    title_localized = ListField(TitleSchema, './reg:bibliographic-data/reg:invention-title')
    lapsed_states = ListField(LapsedSchema, "./reg:bibliographic-data/reg:term-of-grant[1]/reg:lapsed-in-country")

    references_cited = ListField(CitationSchema, ".//reg:bibliographic-data/reg:references-cited/reg:citation")

    # Patent Status

    status_history = ListField(StatusSchema, "./reg:ep-patent-statuses/reg:ep-patent-status")


class EpoDocumentSchema(Schema):
    document = EpoDocumentSubSchema("./ops:register-search/reg:register-documents/reg:register-document", flatten=True)