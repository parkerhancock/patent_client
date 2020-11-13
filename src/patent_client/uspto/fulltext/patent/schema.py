from ..schema import PublicationSchema, ImageSchema
from .model import Patent, PatentImage

class PatentSchema(PublicationSchema):
    __model__ = Patent

class PatentImageSchema(ImageSchema):
    __model__ = PatentImage