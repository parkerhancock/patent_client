import re

from yankee.base import fields as jf
from yankee.base import Schema as JsonSchema
from yankee.xml import fields as f

from .base import Schema as HtmlSchema


class SectionSchema(JsonSchema):
    name = jf.Str("name")
    start = jf.Int("start_page")
    end = jf.Int("end_page")
    pdf_url = jf.Str("pdf_url")


class ImageSchema(JsonSchema):
    pdf_url = jf.Str()
    sections = jf.List(SectionSchema, "sections")


pdf_id_re = re.compile(r"/([\d/]+)/1.pdf")


def pdf_url_id_formatter(text):
    match = pdf_id_re.search(text)
    if match is None:
        return None
    return match.group(1)


class ImageHtmlSchema(HtmlSchema):
    pdf_url_id = f.Str(".//embed/@src", formatter=pdf_url_id_formatter)
    start_page = f.Str('//comment()[contains(., "PageNum")]', formatter=lambda s: int(s.split("=")[1]))
    num_pages = f.Str('//comment()[contains(., "NumPages")]', formatter=lambda s: int(s.split("=")[1]))
    sections = f.Dict(
        './/img[@src="/templates/redball.gif"]/parent::a',
        key=f.Str(),
        value=f.Str(".//@href"),
    )
