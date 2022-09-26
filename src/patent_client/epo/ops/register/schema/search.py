from patent_client.epo.ops.util import Schema
from patent_client.util.xml import ListField
from yankee.xml import fields as f


class InpadocSchema(Schema):
    family_id = f.Str("./@family-id")
    id_type = f.Str(".//epo:document-id/@document-id-type")
    country = f.Str(".//epo:document-id/epo:country")
    doc_number = f.Str(".//epo:document-id/epo:doc-number")
    kind = f.Str(".//epo:document-id/epo:kind")
    
# class SearchSchema(Schema):
#     query = f.Str(".//ops:query")
#     num_results = f.Int(".//ops:biblio-search/@total-result-count")
#     begin = f.Int(".//ops:range/@begin")
#     end = f.Int(".//ops:range/@end")
#     results = ListField(InpadocSchema, ".//ops:search-result/ops:publication-reference")

###
class EPRegisterSearchSchema(Schema):
    query = f.Str(".//ops:query")
    # num_results = f.Int(".//ops:biblio-search/@total-result-count")
    # begin = f.Int(".//ops:range/@begin")
    # end = f.Int(".//ops:range/@end")
    # results = ListField(InpadocSchema, ".//ops:search-result/ops:publication-reference")
    # family_id = f.Str("./@family-id")

    
    id_type = f.Str(".//reg:document-id/@document-id-type")
    country = f.Str(".//reg:document-id/reg:country")
    doc_number = f.Str(".//reg:document-id/reg:doc-number")
    applicant = f.Str(".//reg:applicant/reg:addressbook/reg:name")
    agent = f.Str(".//reg:agent/reg:addressbook/reg:name")
    
