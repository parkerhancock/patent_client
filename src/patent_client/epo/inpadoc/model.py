from __future__ import annotations
from dataclasses import dataclass, field
import typing
import importlib

import datetime as dt
from patent_client.util import Model, one_to_one, one_to_many, QuerySet
from .lookups import lookup_claims, lookup_description, lookup_family

# Core INPADOC Models

@dataclass
class Inpadoc(Model):
    __manager__ = 'patent_client.epo.inpadoc.manager.InpadocManager'
    number: str
    doc_type: str
    kind_code: typing.Optional[str] = None
    country: typing.Optional[str] = None
    family_id: typing.Optional[str] = None
    date: typing.Optional[dt.date] = None

    biblio = one_to_one('patent_client.epo.inpadoc.model.InpadocBiblio', publication='num')
    claims = lookup_claims()
    description = lookup_description()
    family = lookup_family()

    @property
    def num(self):
        return f"{self.country}{self.number}{self.kind_code}"
    
    @property
    def us_application(self):
        klass = getattr(importlib.import_module('patent_client.uspto.peds.model'), 'USApplication')
        if self.kind_code == 'A1':
            pub_num = self.country + self.number[:4] + self.number[4:].rjust(7, '0') + self.kind_code
            return klass.objects.get(app_early_pub_number=pub_num)
        else:
            return klass.objects.get(patent_number=self.number)
        
@dataclass
class InpadocPublication(Inpadoc):
    biblio = one_to_one('patent_client.epo.inpadoc.model.InpadocBiblio', publication='num')

@dataclass
class InpadocApplication(Inpadoc):
    biblio = one_to_one('patent_client.epo.inpadoc.model.InpadocBiblio', application='num') 

# INPADOC Detail Models

@dataclass
class InpadocPriorityClaim(Inpadoc):
    children = one_to_many('patent_client.epo.inpadoc.model.Inpadoc', priority_claim='num')
    biblio = one_to_one('patent_client.epo.inpadoc.model.InpadocBiblio', application='num')  

@dataclass
class InpadocBiblio(Model):
    __manager__ = 'patent_client.epo.inpadoc.manager.InpadocBiblioManager'
    family_id: str
    title: str
    number: str
    kind_code: str
    country: str
    applications: typing.List['InpadocApplication']
    publications: typing.List['InpadocPublication']
    applicants: typing.List[str]
    inventors: typing.List[str]
    abstract: str = None
    ipc_classes: typing.List[str] = field(default_factory=list)
    cpc_classes: typing.List[CpcClass] = field(default_factory=list)
    us_classes: typing.List[str] = field(default_factory=list)
    priority_claims: QuerySet[InpadocPriorityClaim] = field(default_factory=list)

    @property
    def num(self):
        return f"{self.country}{self.number}{self.kind_code}"


# INPADOC Family Models

@dataclass
class InpadocFamilyPriorityClaim(Model):
    doc: Inpadoc
    active: bool
    seq: int
    kind: str
    active: str
    link_type: typing.Optional[str] = None

@dataclass
class InpadocFamilyMember(Model):
    publication: 'InpadocPublication'
    application: 'InpadocApplication'
    priority_claims: typing.List['InpadocPriorityClaim']
    family_id:str 

# Classification Models

@dataclass
class CpcClass(Model):
    sequence: str
    section: str
    cpc_class: str
    subclass: str
    main_group: str
    sub_group: str
    classification_value: str
    generating_office: str





