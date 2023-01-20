from yankee.json.schema import fields as f
from yankee.json.schema import Schema


class GlobalDossierPublicationSchema(Schema):
    pub_country = f.Str()
    pub_num = f.Str()
    kind_code = f.Str()
    pub_date = f.Date("pubDateStr")


class GlobalDossierPriorityClaimSchema(Schema):
    country = f.Str()
    doc_number = f.Str()
    kind_code = f.Str()


class GlobalDossierDocumentNumberSchema(Schema):
    country = f.Str()
    doc_number = f.Str()
    format = f.Str()
    date = f.Date()
    kind_code = f.Str()


class GlobalDossierApplicationSchema(Schema):
    app_num = f.Str()
    app_date = f.Date("appDateStr")
    country_code = f.Str()
    kind_code = f.Str()
    doc_num = GlobalDossierDocumentNumberSchema("docNum")
    title = f.Str()
    applicantNames = f.Str()
    ip_5 = f.Bool("ip5")
    priority_claim_list = f.List(GlobalDossierPriorityClaimSchema)
    pub_list = f.List(GlobalDossierPublicationSchema)


class GlobalDossierSchema(Schema):
    country = f.Str()
    internal = f.Bool(true_value="true")
    corr_app_num = f.Str()
    id = f.Str()
    type = f.Str()
    applications = f.List(GlobalDossierApplicationSchema, "list")


class DocumentSchema(Schema):
    doc_number = f.Str()
    country = f.Str()
    doc_code = f.Str()
    doc_desc = f.Str()
    doc_id = f.Str()
    date = f.Date("legalDateStr")
    doc_format = f.Str()
    pages = f.Int("numberOfPages")
    doc_code_desc = f.Str()
    doc_group_code = f.Str()
    shareable = f.Bool()


class DocumentListSchema(Schema):
    title = f.Str("title")
    doc_number = f.Str()
    country = f.Str()
    message = f.Str()
    applicant_names = f.List(f.Str())
    office_action_count = f.Int("oaIndCount")
    docs = f.List(DocumentSchema)
    office_action_docs = f.List(DocumentSchema)

    def pre_load(self, obj):
        update_dict = {
            "country": obj["country"],
            "docNumber": obj["docNumber"],
        }
        for doc in obj["docs"]:
            doc.update(update_dict)
        for doc in obj["officeActionDocs"]:
            doc.update(update_dict)
        return obj
