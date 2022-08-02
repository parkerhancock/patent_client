from .family.api import FamilyApi
from .legal.api import LegalApi
from .number_service.api import convert_number
from .published.api import PublishedApi


class OpsApi:
    family = FamilyApi
    legal = LegalApi
    published = PublishedApi
    convert_number = convert_number
