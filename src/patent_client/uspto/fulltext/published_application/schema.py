from ..schema import PublicationSchema, ImageSchema
from .model import PublishedApplication, PublishedApplicationImage

class PublishedApplicationSchema(PublicationSchema):
    __model__ = PublishedApplication

class PublishedApplicationImageSchema(ImageSchema):
    __model__ = PublishedApplicationImage