from ..schema import ImageSchema
from ..schema import PublicationSchema
from .model import Patent
from .model import PatentImage


class PatentSchema(PublicationSchema):
    __model__ = Patent


class PatentImageSchema(ImageSchema):
    __model__ = PatentImage
