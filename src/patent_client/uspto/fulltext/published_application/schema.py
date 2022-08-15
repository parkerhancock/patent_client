from .model import PublishedApplication, PublishedApplicationImage, PublishedApplicationResult
from ..schema.publication import PublicationSchema
from ..schema.images import ImageSchema

from patent_client.util.xml import Schema, RegexSchema, fields as f

class PublishedApplicationSchema(PublicationSchema):
    __model__ = PublishedApplication

class PublishedApplicationImageSchema(ImageSchema):
    __model__ = PublishedApplicationImage


class PublishedApplicationResultSchema(Schema):
    seq = f.Int(".//td[1]")
    publication_number = f.Str(".//td[2]", formatter=lambda s: s.replace(",", ""))
    title = f.Str(".//td[3]")


class ResultMetaSchema(RegexSchema):
    __regex__ = r"Hits (?P<start>\d+) through (?P<end>\d+) out of (?P<num_results>\d+)"
    start = f.Int(".//start")
    end = f.Int(".//end")
    num_results = f.Int(".//num_results")


class PublishedApplicationResultPageSchema(Schema):
    query = f.Str('.//input[@title="query"]/@value')
    result = ResultMetaSchema("(.//i)[2]", flatten=True)
    results = f.List(PublishedApplicationResultSchema, "(.//table//tr)[position()>1]")
