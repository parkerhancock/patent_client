import re
from yankee.xml import fields as f
from .base import Schema

class SectionSchema(Schema):
    name = f.Str("name")
    start = f.Int("start_page")
    end = f.Int("end_page")
    pdf_url = f.Str("pdf_url")


class ImageSchema(Schema):
    pdf_url = f.Str()
    sections = f.List(SectionSchema, "sections")

pdf_id_re = re.compile(r"/([\d/]+)/1.pdf")


def pdf_url_id_formatter(text):
    match = pdf_id_re.search(text)
    if match is None:
        return None
    return match.group(1)


class ImageHtmlSchema(Schema):
    pdf_url_id = f.Str(".//embed/@src", formatter=pdf_url_id_formatter)
    start_page = f.Str('//comment()[contains(., "PageNum")]', formatter=lambda s: int(s.split("=")[1]))
    num_pages = f.Str('//comment()[contains(., "NumPages")]', formatter=lambda s: int(s.split("=")[1]))
    sections = f.Dict(
        './/img[@src="/templates/redball.gif"]/parent::a',
        key=f.Str(),
        value=f.Str(".//@href"),
    )