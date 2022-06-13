from ..schema import ImageSchema
from ..schema import PublicationSchema
from .model import PublishedApplication
from .model import PublishedApplicationImage


class PublishedApplicationSchema(PublicationSchema):
    __model__ = PublishedApplication


class PublishedApplicationImageSchema(ImageSchema):
    __model__ = PublishedApplicationImage
