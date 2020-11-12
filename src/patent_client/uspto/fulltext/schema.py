import re
from patent_client.util.schema import *
from dateutil.parser import parse as parse_dt

from .model import Publication, Inventor, Applicant, Assignee, RelatedPatentDocument, PriorPublication, USReference, ForeignReference, NPLReference, CpcClass, USClass, ForeignPriority

# Related People

class InventorSchema(Schema):
    __model__ = Inventor
    city = StringField()
    first_name = StringField()
    last_name = StringField()
    region = StringField()

class ApplicantSchema(Schema):
    __model__ = Applicant
    city = StringField()
    country = StringField()
    name = StringField()
    state = StringField()
    type = StringField()

class AssigneeSchema(Schema):
    __model__ = Assignee
    name = StringField()
    city = StringField(required=False)
    region = StringField(required=False)

# Classification Types

class CpcClassSchema(Schema):
    __model__ = CpcClass
    classification = StringField("class")
    version = StringField()

class IntlClassSchema(CpcClassSchema):
    pass

class USClassSchema(Schema):
    __model__ = USClass
    classification = StringField("class")
    subclassification = StringField("subclass")

# Foreign Priority

class ForeignPrioritySchema(Schema):
    __model__ = ForeignPriority
    date = DateField()
    country_code = StringField()
    number = StringField()

# Cited Reference Types

class USReferenceSchema(Schema):
    __model__ = USReference
    date = StringField()
    name = StringField()
    publication_number = StringField()

class ForeignReferenceSchema(Schema):
    __model__ = ForeignReference
    publication_number = StringField()
    name = StringField()
    country_code = StringField()

class NPLReferenceSchema(Schema):
    __model__ = NPLReference
    citation = StringField()

# Related Document Types

class PriorPublicationSchema(Schema):
    __model__ = PriorPublication
    publication_number = StringField()
    publication_date = DateField()

class RelatedPatentDocumentSchema(Schema):
    __model__ = RelatedPatentDocument
    appl_id = StringField()
    filing_date = DateField(required=False)
    patent_number = StringField(required=False)

class PublicationSchema(Schema):
    publication_number = StringField()
    kind_code = StringField()
    publication_date = DateField()
    title = StringField()

    description = StringField()
    abstract = StringField()
    claims = StringField()
    
    appl_id = StringField("appl_no", formatter=lambda x: re.sub(r"[^\d]", "", x.replace("D", "29")), required=False)
    filing_date = DateField("filed")
    family_id = StringField(required=False)

    pct_filing_date = DateField("pct_filed", required=False)
    pct_number = StringField("pct_no", required=False)
    national_stage_entry_date = DateField("371_date", required=False)
    foreign_priority = Nested(ForeignPrioritySchema(), many=True, required=False)

    inventors = Nested(InventorSchema(), many=True)
    applicants = Nested(ApplicantSchema(), many=True, required=False)
    assignees = Nested(AssigneeSchema(), data_key="assignee", many=True, required=False)
    examiner = StringField(required=False)
    agent = StringField(required=False)

    prior_publications = Nested(PriorPublicationSchema(), many=True)
    related_us_applications = Nested(RelatedPatentDocumentSchema(), many=True)
    
    cpc_classes = Nested(CpcClassSchema(), data_key="current_cpc_class", many=True, required=False)
    intl_classes = Nested(IntlClassSchema(), data_key="current_international_class", many=True)
    us_classes = Nested(USClassSchema(), many=True, data_key="current_us_class")   
    field_of_search = Nested(USClassSchema(), many=True, data_key="field_of_search", required=False)
    
    us_references = Nested(USReferenceSchema(), many=True, required=False)
    foreign_references = Nested(ForeignReferenceSchema(), many=True, required=False)
    npl_references = Nested(NPLReferenceSchema(), many=True, required=False)

class ImageSchema(Schema):
    publication_number = StringField()
    pdf_url = StringField()
    sections = Field()