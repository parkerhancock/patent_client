from marshmallow import Schema, fields, EXCLUDE, pre_load, post_load
from patent_client.util.manager import resolve
from patent_client.util import QuerySet, ListField

from .model import Inpadoc, CpcClass, InpadocBiblio, InpadocApplication, InpadocPublication, InpadocPriorityClaim

class BaseSchema(Schema):
    @post_load
    def make_object(self, data, **kwargs):
        if hasattr(self, '__model__'):
            return self.__model__(**data)
        return data

class InpadocResultSchema(BaseSchema):
    __model__ = Inpadoc
    country = fields.Str(data_key='country')
    number = fields.Str(data_key='doc-number')
    kind_code = fields.Str(data_key='kind')
    doc_type = fields.Str(data_key='@document-id-type')
    family_id = fields.Int(data_key='@family-id')

    @pre_load
    def pre_load(self, data, *args, **kwargs):
        for k, v in data['document-id'].items():
            data[k] = v
        del data['document-id']
        return data

    
    class Meta:
        unknown=EXCLUDE

def flatten(data, subfield):
    data = {**data, **data[subfield]}
    del data[subfield]
    return data

class InpadocSchema(BaseSchema):
    __model__ = Inpadoc
    country = fields.Str(data_key='country')
    number = fields.Str(data_key='doc-number')
    kind_code = fields.Str(data_key='kind')
    doc_type = fields.Str(data_key='@document-id-type')
    date = fields.Date(format='%Y%m%d')

class InpadocApplicationSchema(InpadocSchema):
    __model__ = InpadocApplication
    class Meta:
        unknown=EXCLUDE

class InpadocPublicationSchema(InpadocSchema):
    __model__ = InpadocPublication
    class Meta:
        unknown=EXCLUDE

class PriorityClaimSchema(BaseSchema):
    __model__ = InpadocPriorityClaim
    doc_type = fields.Str(data_key='@document-id-type')
    kind_code = fields.Str(data_key='@kind')
    date = fields.Date(format="%Y%m%d")
    number = fields.Str(data_key='doc-number')

    class Meta:
        unknown=EXCLUDE

class CpcClassSchema(BaseSchema):
    __model__ = CpcClass
    sequence = fields.Str(data_key='@sequence')
    section = fields.Str()
    cpc_class = fields.Str(data_key='class')
    subclass = fields.Str()
    main_group = fields.Str(data_key='main-group')
    sub_group = fields.Str(data_key='subgroup')
    classification_value = fields.Str(data_key='classification-value')
    generating_office = fields.Str(data_key='generating-office')

    class Meta:
        unknown=EXCLUDE

class UsClassSchema(BaseSchema):
    symbol = fields.Str(data_key = 'classification-symbol')

    class Meta:
        unknown=EXCLUDE

class InpadocBiblioSchema(BaseSchema):
    __model__ = InpadocBiblio

    family_id = fields.Str(data_key='@family-id')
    country = fields.Str(data_key='@country')
    number = fields.Str(data_key='@doc-number')
    kind_code = fields.Str(data_key='@kind')
    abstract = fields.Method(deserialize='get_abstract')
    inventors = fields.Method(deserialize='get_inventors')
    applicants = fields.Method(deserialize='get_applicants')
    publications = ListField(fields.Nested(InpadocPublicationSchema))
    ipc_classes = ListField(fields.Str(), allow_none=True)
    cpc_classes = ListField(fields.Nested(CpcClassSchema), allow_none=True)
    us_classes = ListField(fields.Nested(UsClassSchema), allow_none=True)
    applications = ListField(fields.Nested(InpadocApplicationSchema))
    priority_claims = ListField(fields.Nested(PriorityClaimSchema))
    title = fields.Str()

    def get_abstract(self, data):
        if isinstance(data, dict):
            return data['p']
        else:
            abstract = next((d for d in data if d['@lang'] == 'en'), data[0])
            return abstract['p']

    def get_inventors(self, data):
        return [ i['inventor-name']['name'] for i in data if i['@data-format'] == 'original']

    def get_applicants(self, data):
        return [ i['applicant-name']['name'] for i in data if i['@data-format'] == 'original']

    def pre_load_priority_claims(self, bib):
        pcs = resolve(bib, 'priority-claims.priority-claim')
        out = list()
        pcs = pcs if isinstance(pcs, list) else [pcs,]
        for pc in pcs:
            if isinstance(pc['document-id'], list):
                doc_id = pc['document-id'][0]
            else:
                doc_id = pc['document-id']
            pc = {**pc, **doc_id}
            del pc['document-id']
            out.append(pc)
        return out

    @pre_load
    def pre_load(self, data, *args, **kwargs):
        data = data['exchange-document']
        bib = data['bibliographic-data']
        del data['bibliographic-data']
        data['publications'] = resolve(bib, 'publication-reference.document-id')
        ipc_class = resolve(bib, 'classifications-ipcr.classification-ipcr')
        if ipc_class:
            data['ipc_classes'] = [c['text'] for c in ipc_class]
        classifications = resolve(bib, 'patent-classifications.patent-classification')
        if classifications: 
            data['cpc_classes'] = [c for c in classifications if resolve(c, 'classification-scheme.@scheme') == 'CPCI']
            data['us_classes'] = [c for c in classifications if resolve(c, 'classification-scheme.@scheme') == 'UC']
        data['applications'] = resolve(bib, 'application-reference.document-id')
        data['priority_claims'] = self.pre_load_priority_claims(bib)
        data['applicants'] = resolve(bib, 'parties.applicants.applicant')
        data['inventors'] = resolve(bib, 'parties.inventors.inventor')
        titles = resolve(bib, 'invention-title')
        if isinstance(titles, list):
            data['title'] = next(t['#text'] for t in titles if t['@lang'] == 'en') 
        else:
            data['title'] = titles['#text']
        return data

    class Meta:
        unknown=EXCLUDE