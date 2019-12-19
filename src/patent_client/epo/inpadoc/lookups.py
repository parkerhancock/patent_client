
import importlib
import datetime as dt
import xml.etree.ElementTree as ET
from .session import session

# Utility Objects and Functions

NS = {
    'ft': 'http://www.epo.org/fulltext',
    'ops': 'http://ops.epo.org',
    'ex': 'http://www.epo.org/exchange'
}

def etree_els_to_text(els):
    segments = [' '.join(e.itertext()) for e in els]
    return "\n".join(segments)

def docid_to_inpadoc(doc, model_name='Inpadoc'):
    klass = getattr(importlib.import_module('patent_client.epo.inpadoc.model'), model_name)
    date = doc.find('./ex:date', NS)
    if date is not None:
        date = dt.datetime.strptime(date.text, '%Y%m%d').date()
    return klass(
        doc_type=doc.attrib['document-id-type'],
        country=doc.find('./ex:country', NS).text,
        number=doc.find('./ex:doc-number', NS).text,
        kind_code=doc.find('./ex:kind', NS).text,
        date=date,
    )

def parse_family_member(member):
    family_class = getattr(importlib.import_module('patent_client.epo.inpadoc.model'), 'InpadocFamilyMember')
    priority_claim_class = getattr(importlib.import_module('patent_client.epo.inpadoc.model'), 'InpadocFamilyPriorityClaim') 
    pub = member.find('.//ex:publication-reference/ex:document-id[@document-id-type="docdb"]', NS)
    app = member.find('.//ex:application-reference/ex:document-id[@document-id-type="docdb"]', NS)
    family_id = int(member.attrib['family-id'])
    priority = member.findall('.//ex:priority-claim', NS)
    priority_claims = list()
    for c in priority:
        doc = docid_to_inpadoc(c.find('.//ex:document-id[@document-id-type="docdb"]', NS), 'Inpadoc')
        active = c.find('.//ex:priority-active-indicator', NS).text == 'YES'
        link_type = c.find('.//ex:priority-linkage-type', NS)
        link_type = link_type.text if link_type is not None else link_type
        seq = c.attrib['sequence']
        kind = c.attrib.get('kind', None)
        priority_claims.append(priority_claim_class(**{
            'seq': int(seq),
            'kind': kind,
            'link_type': link_type,
            'active': active,
            'doc': doc,
        }))
    return family_class(**{
        'publication': docid_to_inpadoc(pub, 'InpadocPublication'),
        'application': docid_to_inpadoc(app, 'InpadocApplication'),
        'priority_claims': priority_claims,
        'family_id': family_id,
    })

# Lookup Functions

def lookup_claims():
    @property
    def get(self) -> str:
        url = f"http://ops.epo.org/3.2/rest-services/published-data/publication/{self.doc_type}/{self.num}/claims"
        response = session.get(url)
        claim_els = ET.fromstring(response.text).findall('.//ft:claim-text', NS)
        return etree_els_to_text(claim_els)
    return get

def lookup_description():
    @property
    def get(self) -> str:
        url = f"http://ops.epo.org/3.2/rest-services/published-data/publication/{self.doc_type}/{self.num}/description"
        response = session.get(url)
        description_els = ET.fromstring(response.text).findall('.//ft:p', NS)
        return etree_els_to_text(description_els)
    return get

def lookup_family():
    @property
    def get(self):
        url = f"http://ops.epo.org/3.2/rest-services/family/publication/{self.doc_type}/{self.num}"
        response = session.get(url)
        members = ET.fromstring(response.text).findall('.//ops:family-member', NS)
        return [parse_family_member(m) for m in members]
    return get

