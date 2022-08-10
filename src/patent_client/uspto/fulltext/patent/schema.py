import re
from ..schema.images import ImageSchema
from .model import PatentImage, Patent
from yankee.xml import fields as f

from patent_client.uspto.fulltext.schema.base import Schema, RegexSchema
from patent_client.uspto.fulltext.schema.publication import PublicationSchema
from patent_client.uspto.fulltext.schema.images import ImageSchema

class PatentSchema(PublicationSchema):
    __model__ = Patent

class PatentImageSchema(ImageSchema):
    __model__ = PatentImage


class PatentResultSchema(Schema):
    seq = f.Int(".//td[1]")
    publication_number = f.Str(".//td[2]", formatter=lambda s: s.replace(",", ""))
    title = f.Str(".//td[4]")


class ResultMetaSchema(RegexSchema):
    __regex__ = r"Hits (?P<start>\d+) through (?P<end>\d+) out of (?P<num_results>\d+)"
    start = f.Int(".//start")
    end = f.Int(".//end")
    num_results = f.Int(".//num_results")


class PatentResultPageSchema(Schema):
    query = f.Str('.//span[@id="srchtext"]')
    result = ResultMetaSchema('.//span[@id="srchtext"]/following::i', flatten=True)
    results = f.List(PatentResultSchema, "((.//table)[2]//tr)[position()>1]")
