import datetime
import re
from collections.abc import Sequence

import lxml.html as ETH
from yankee.json.schema import fields as f
from yankee.json.schema import RegexSchema
from yankee.json.schema import Schema
from yankee.json.schema import ZipSchema

newline_re = re.compile(r"<br />\s*")
bad_break_re = re.compile(r"<br />\s+")


def html_to_text(html):
    html = newline_re.sub("\n\n", html)
    # html = bad_break_re.sub(" ", html)
    return "".join(ETH.fromstring(html).itertext())


class HtmlField(f.Field):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        if obj is None:
            return None
        elif isinstance(obj, Sequence) and not isinstance(obj, str):
            return "\n\n".join(html_to_text(s) for s in obj)
        else:
            return html_to_text(obj)


def format_appl_id(string):
    if string.startswith("D"):
        string = "29" + string[1:]
    return string.replace("/", "")


class DocumentStructureSchema(Schema):
    number_of_claims = f.Integer("numberOfClaims")
    number_of_drawing_sheets = f.Integer("numberOfDrawingSheets")
    number_of_figures = f.Integer("numberOfFigures")
    page_count = f.Integer("pageCount")
    front_page_end = f.Integer("frontPageEnd")
    front_page_start = f.Integer("frontPageStart")
    bib_start = f.Integer("bibStart")
    bib_end = f.Integer("bibEnd")
    abstract_start = f.Integer("abstractStart")
    abstract_end = f.Integer("abstractEnd")
    drawings_start = f.Integer("drawingsStart")
    drawings_end = f.Integer("drawingsEnd")
    description_start = f.Integer("descriptionStart")
    description_end = f.Integer("descriptionEnd")
    specification_start = f.Integer("specificationStart")
    specification_end = f.Integer("specificationEnd")
    claims_end = f.Integer("claimsEnd")
    claims_start = f.Integer("claimsStart")
    amend_start = f.Integer("amendStart")
    amend_end = f.Integer("amendEnd")
    cert_correction_end = f.Integer("certCorrectionEnd")
    cert_correction_start = f.Integer("certCorrectionStart")
    cert_reexamination_end = f.Integer("certReexaminationEnd")
    cert_reexamination_start = f.Integer("certReexaminationStart")
    ptab_start = f.Integer("ptabStart")
    ptab_end = f.Integer("ptabEnd")
    search_report_start = f.Integer("searchReportStart")
    search_report_end = f.Integer("searchReportEnd")
    supplemental_start = f.Integer("supplementalStart")
    supplemental_end = f.Integer("supplementalEnd")


class PublicSearchSchema(Schema):
    guid = f.String("guid")

    appl_id = f.String("applicationNumber", formatter=format_appl_id)
    app_filing_date = f.Date("applicationFilingDate.0")
    related_appl_filing_date = f.List(f.Date, "relatedApplFilingDate")
    publication_number = f.String("publicationReferenceDocumentNumber")
    kind_code = f.String("kindCode.0")
    publication_date = f.Date("datePublished")
    patent_title = HtmlField("inventionTitle")

    inventors_short = f.String("inventorsShort")
    applicant_name = f.List(f.String, "applicantName")
    assignee_name = f.List(f.String, "assigneeName")
    government_interest = f.List(f.String, "governmentInterest")
    primary_examiner = f.String("primaryExaminer")
    assistant_examiner = f.List(f.String, "assistantExaminer")

    main_classification_code = f.String("mainClassificationCode")
    cpc_additional = f.DelimitedString(f.Str(), "cpcAdditionalFlattened", delimeter=";")
    cpc_inventive = f.DelimitedString(f.Str(), "cpcInventiveFlattened", delimeter=";")
    ipc_code = f.DelimitedString(f.Str(), "ipcCodeFlattened", delimeter=";")
    uspc_full_classification = f.DelimitedString(f.Str(), "uspcFullClassificationFlattened", delimeter=";")

    image_file_name = f.String("imageFileName")
    image_location = f.String("imageLocation")
    document_structure = DocumentStructureSchema(data_key=False)

    type = f.String("type")
    database_name = f.String("databaseName")
    composite_id = f.String("compositeId")
    document_id = f.String("documentId")
    document_size = f.Integer("documentSize")
    family_identifier_cur = f.Integer("familyIdentifierCur")
    language_indicator = f.String("languageIndicator")

    score = f.Float("score")


class SpecificationField(f.Combine):
    pass


class DocumentSchema(Schema):
    abstract = HtmlField("abstractHtml")
    government_interest = HtmlField("governmentInterest")
    background = HtmlField("backgroundTextHtml")
    brief = HtmlField("briefHtml")
    description = HtmlField("descriptionHtml")
    claim_statement = f.String("claimStatement")
    claims = HtmlField("claimsHtml")


class UsReferenceSchema(ZipSchema):
    publication_number = f.String("urpn")
    # us_class = f.String("usRefClassification")
    # cpc_class = f.String("usRefCpcClassification")
    # group = f.String("usRefGroup")
    pub_month = f.Date(
        "usRefIssueDate", dt_converter=lambda s: datetime.datetime(year=int(s[:4]), month=int(s[4:6]), day=1)
    )
    patentee_name = f.String("usRefPatenteeName")
    cited_by_examiner = f.Boolean("usRefGroup", true_func=lambda s: "examiner" in s)


class ForeignReferenceSchema(ZipSchema):
    citation_classification = f.String("foreignRefCitationClassification")
    citation_cpc = f.String("foreignRefCitationCpc")
    country_code = f.String("foreignRefCountryCode")
    # group = f.String("foreignRefGroup")
    patent_number = f.String("foreignRefPatentNumber")
    pub_month = f.Date(
        "foreignRefPubDate", dt_converter=lambda s: datetime.datetime(year=int(s[:4]), month=int(s[4:6]), day=1)
    )
    cited_by_examiner = f.Boolean("foreignRefGroup", true_func=lambda s: "examiner" in s)


class NplReferenceSchema(RegexSchema):
    __regex__ = r"(?P<citation>.*)(?P<cited_by_examiner>cited by (applicant|examiner).?$)"
    citation = f.String()
    cited_by_examiner = f.Bool(true_func=lambda s: "examiner" in s)


class RelatedApplicationSchema(ZipSchema):
    child_patent_country = f.String("relatedApplChildPatentCountry")
    child_patent_number = f.String("relatedApplChildPatentNumber")
    country_code = f.String("relatedApplCountryCode")
    filing_date = f.Date("relatedApplFilingDate")
    number = f.String("relatedApplNumber")
    parent_status_code = f.String("relatedApplParentStatusCode")
    patent_issue_date = f.Date("relatedApplPatentIssueDate")
    patent_number = f.String("relatedApplPatentNumber")


class InventorSchema(ZipSchema):
    name = f.String("inventorsName")
    city = f.String("inventorCity")
    country = f.String("inventorCountry")
    postal_code = f.String("inventorPostalCode")
    state = f.String("inventorState")


class ApplicantSchema(ZipSchema):
    city = f.String("applicantCity")
    country = f.String("applicantCountry")
    # group = f.String("applicantGroup")
    name = f.String("applicantName")
    state = f.String("applicantState")
    zip_code = f.String("applicantZipCode")
    authority_type = f.String("applicantAuthorityType")


class AssigneeSchema(ZipSchema):
    city = f.String("assigneeCity")
    country = f.String("assigneeCountry")
    name = f.String("assigneeName")
    postal_code = f.String("assigneePostalCode")
    state = f.String("assigneeState")
    type_code = f.String("assigneeTypeCode")


class CpcCodeSchema(RegexSchema):
    __regex__ = r"(?P<cpc_class>.{4})(?P<cpc_subclass>[^ ]+) (?P<version>\d{8})"
    cpc_class = f.Str()
    cpc_subclass = f.Str()
    version = f.Date()


class IntlCodeSchema(RegexSchema):
    __regex__ = r"(?P<intl_class>.{4})(?P<intl_subclass>[^ ]+) (?P<version>\d{8})"
    intl_class = f.Str()
    intl_subclass = f.Str()
    version = f.Date()


class ForeignPriorityApplicationSchema(ZipSchema):
    country = f.Str("priorityClaimsCountry")
    app_filing_date = f.Date("priorityClaimsDate")
    app_number = f.Str("priorityClaimsDocNumber")


class PublicSearchDocumentSchema(Schema):
    guid = f.String("guid")
    publication_number = f.String("pubRefDocNumber")
    publication_date = f.Date("datePublished")

    appl_id = f.String("applicationNumber", formatter=format_appl_id)
    patent_title = HtmlField("inventionTitle")
    app_filing_date = f.Date("applicationFilingDate.0")
    application_type = f.String("applicationRefFilingType")
    family_identifier_cur = f.Integer("familyIdentifierCur")
    related_apps = RelatedApplicationSchema(data_key=False)
    foreign_priority = ForeignPriorityApplicationSchema(data_key=False)
    type = f.String("type")

    # Parties
    inventors = InventorSchema(data_key=False)
    inventors_short = f.String("inventorsShort")
    applicants = ApplicantSchema(data_key=False)
    assignees = AssigneeSchema(data_key=False)

    group_art_unit = f.String("examinerGroup")
    primary_examiner = f.String("primaryExaminer")
    assistant_examiner = f.List(f.String, "assistantExaminer")
    legal_firm_name = f.List(f.String, "legalFirmName")
    attorney_name = f.List(f.String, "attorneyName")

    # Text Data
    document = DocumentSchema(data_key=False)
    document_structure = DocumentStructureSchema(data_key=False)

    # Image Data
    image_file_name = f.String("imageFileName")
    image_location = f.String("imageLocation")

    # Metadata
    composite_id = f.String("compositeId")
    database_name = f.String("databaseName")
    derwent_week_int = f.Integer("derwentWeekInt")

    # References Cited
    us_references = UsReferenceSchema(data_key=False)
    foreign_references = ForeignReferenceSchema(data_key=False)
    npl_references = f.DelimitedString(NplReferenceSchema, "otherRefPub.0", delimeter="<br />")

    # Classifications
    cpc_inventive = f.List(CpcCodeSchema)
    cpc_additional = f.List(CpcCodeSchema)

    intl_class_issued = f.DelimitedString(f.String, "ipcCodeFlattened", delimeter=";")
    intl_class_current_primary = f.List(IntlCodeSchema, "curIntlPatentClassificationPrimary")
    intl_class_currrent_secondary = f.List(IntlCodeSchema, "curIntlPatentClassificationSecondary")

    us_class_current = f.DelimitedString(f.Str(), "uspcFullClassificationFlattened", delimeter=";")
    us_class_issued = f.List(f.Str, "issuedUsClassificationFull")

    field_of_search_us = f.List(f.Str(), "fieldOfSearchClassSubclassHighlights")
    field_of_search_cpc = f.List(f.Str(), "fieldOfSearchCpcClassification")
