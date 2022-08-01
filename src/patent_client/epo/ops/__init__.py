from lib2to3.pytree import convert
from .family.api import FamilyApi
from .legal.api import LegalApi
from .number_service.api import convert_number
from .published.api import PublishedDataApi, PublishedFulltextApi, PublishedSearchApi

class PublishedApi():
    data = PublishedDataApi
    full_text = PublishedFulltextApi
    search = PublishedSearchApi

class OpsApi():
    family = FamilyApi
    legal = LegalApi
    published = PublishedApi
    convert_number = convert_number
    