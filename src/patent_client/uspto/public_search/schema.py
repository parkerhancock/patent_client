import lxml.html as ETH
import datetime
from yankee.json.schema import Schema, ZipSchema, RegexSchema, fields as f

class HtmlField(f.Field):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        return "".join(ETH.fromstring(obj).itertext()) if obj else None

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


class PatentBiblioSchema(Schema):
    guid = f.String("guid")
    
    application_number = f.String("applicationNumber")
    application_filing_date = f.Date("applicationFilingDate.0")
    related_appl_filing_date = f.List(f.Date, "relatedApplFilingDate")
    publication_reference_document_number = f.String("publicationReferenceDocumentNumber")
    kind_code = f.String("kindCode.0")
    date_published = f.Date("datePublished")
    invention_title = HtmlField("inventionTitle")
    
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
    urpn = f.List(f.String, "urpn")
    urpn_code = f.List(f.String, "urpnCode")
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

class DocumentSchema(Schema):
    abstract = HtmlField("abstractHtml")
    background = HtmlField("backgroundTextHtml")
    description = HtmlField("descriptionHtml")
    brief = HtmlField("briefHtml")
    claim_statement = f.String("claimStatement")
    claims = HtmlField("claimsHtml")

class UsReferenceSchema(ZipSchema):
    publication_number = f.String("urpn")
    us_class = f.String("usRefClassification")
    cpc_class = f.String("usRefCpcClassification")
    #group = f.String("usRefGroup")
    pub_month = f.Date("usRefIssueDate", dt_converter=lambda s: datetime.datetime(year=int(s[:4]), month=int(s[4:6]), day=1))
    patentee_name = f.String("usRefPatenteeName")
    cited_by_examiner = f.Boolean("usRefGroup", true_func=lambda s: "examiner" in s)

class ForeignReferenceSchema(ZipSchema):
    citation_classification = f.String("foreignRefCitationClassification")
    citation_cpc = f.String("foreignRefCitationCpc")
    country_code = f.String("foreignRefCountryCode")
    #group = f.String("foreignRefGroup")
    patent_number = f.String("foreignRefPatentNumber")
    pub_month = f.Date("foreignRefPubDate", dt_converter=lambda s: datetime.datetime(year=int(s[:4]), month=int(s[4:6]), day=1))
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
    #group = f.String("applicantGroup")
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

class PatentDocumentSchema(Schema):
    guid = f.String("guid")
    publication_date = f.Date("datePublished")

    appl_id = f.String("applicationNumber", formatter=lambda s: s.replace("/", ""))
    app_filing_date = f.Date("applicationFilingDate.0")
    application_type = f.String("applicationRefFilingType")
    family_identifier_cur = f.Integer("familyIdentifierCur")
    related_apps = RelatedApplicationSchema(data_key=False)

    # Parties
    inventors = InventorSchema(data_key=False)
    inventors_short = f.String("inventorsShort")
    applicants = ApplicantSchema(data_key=False)
    assignees = AssigneeSchema(data_key=False)
    assistant_examiner = f.List(f.String, "assistantExaminer")
    attorney_name = f.List(f.String, "attorneyName")

    # Text Data
    document = DocumentSchema(data_key=False)
    document_structure = DocumentStructureSchema(data_key=False)

    # Image Data
    image_file_name = f.String("imageFileName")
    image_location = f.String("imageLocation")

    cert_of_correction_flag = f.Bool("certOfCorrectionFlag", true_value="yes")

    
    composite_id = f.String("compositeId")
    database_name = f.String("databaseName")
    derwent_week_int = f.Integer("derwentWeekInt")

    continuity_data = f.List(f.String, "continuityData")
    country = f.String("country")

    # References Cited
    us_references = UsReferenceSchema(data_key=False)
    foreign_references = ForeignReferenceSchema(data_key=False)
    npl_references = f.DelimitedString(NplReferenceSchema, "otherRefPub.0", delimeter="<br />")

    # Classifications
    cpc_inventive = f.List(CpcCodeSchema)
    cpc_additional = f.List(CpcCodeSchema)
    """
    cpc_additional = f.List(f.String, "cpcAdditional")
    cpc_additional_flattened = f.String("cpcAdditionalFlattened")
    cpc_combination_classification_cur = f.List(f.String, "cpcCombinationClassificationCur")
    cpc_combination_sets_cur_highlights = f.List(f.String, "cpcCombinationSetsCurHighlights")
    cpc_combination_tally_cur = f.List(f.String, "cpcCombinationTallyCur")
    cpc_cur_additional_class = f.List(f.String, "cpcCurAdditionalClass")
    cpc_cur_classification_group = f.List(f.String, "cpcCurClassificationGroup")
    cpc_cur_inventive_class = f.List(f.String, "cpcCurInventiveClass")
    cpc_inventive = f.DelimitedString(f.String(), "cpcInventiveFlattened", delimiter=";")

    cur_cpc_classification_full = f.List(f.String, "curCpcClassificationFull")
    cur_cpc_subclass_full = f.List(f.String, "curCpcSubclassFull")
    cur_intl_patent_classification_noninvention = f.List(f.String, "curIntlPatentClassificationNoninvention")
    cur_intl_patent_classification_primary = f.List(f.String, "curIntlPatentClassificationPrimary")
    cur_intl_patent_classification_secondary = f.List(f.String, "curIntlPatentClassificationSecondary")
    cur_us_classification_us_primary_class = f.String("curUsClassificationUsPrimaryClass")
    current_us_cross_reference_classification = f.List(f.String, "currentUsCrossReferenceClassification")
    current_us_original_classification = f.String("currentUsOriginalClassification")
    current_us_patent_class = f.List(f.String, "currentUsPatentClass")


    document_id = f.String("documentId")
    document_size = f.Integer("documentSize")
    group_art_unit = f.String("examinerGroup")

    

    field_of_search = f.List(f.String, "fieldOfSearchClassSubclassHighlights")
    field_of_search_cpc = f.List(f.String, "fieldOfSearchCpcClassification")
    
    government_interest = f.List(f.String, "governmentInterest")




    intl_further_classification = f.List(f.String, "intlFurtherClassification")
    intl_pub_classification_class = f.List(f.String, "intlPubClassificationClass")
    intl_pub_classification_group = f.List(f.String, "intlPubClassificationGroup")
    intl_pub_classification_non_invention = f.List(f.String, "intlPubClassificationNonInvention")
    intl_pub_classification_primary = f.List(f.String, "intlPubClassificationPrimary")
    intl_pub_classification_secondary = f.List(f.String, "intlPubClassificationSecondary")
    invention_title = f.String("inventionTitle")
    
    ipc_class = f.DelimitedString(f.String, "ipcCodeFlattened", delimeter=";")

    kind_code = f.String("kindCode.0")
    language_indicator = f.String("languageIndicator")
    legal_firm_name = f.List(f.String, "legalFirmName")
    legal_representative_country = f.String("legalRepresentativeCountry")
    main_classification_code = f.String("mainClassificationCode")
    object_contents = f.String("objectContents")
    object_description = f.String("objectDescription")
    

    primary_examiner = f.String("primaryExaminer")
    primary_examiner_highlights = f.String("primaryExaminerHighlights")
    principal_attorney_name = f.List(f.String, "principalAttorneyName")
    pub_ref_country_code = f.String("pubRefCountryCode")
    publication_number = f.String("pubRefDocNumber")


    


    score = f.Float("score")
    term_of_extension = f.Int("termOfExtension")
    type = f.String("type")
    us_class = f.DelimitedString(f.String, "uspcFullClassificationFlattened", delimeter=";")
    """
