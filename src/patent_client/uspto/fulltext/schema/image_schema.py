from yankee import Schema, fields as f

class SectionSchema(Schema):
    name = f.Str("name")
    start = f.Int("start_page")
    end = f.Int("end_page")
    pdf_url = f.Str("pdf_url")


class ImageSchema(Schema):
    pdf_url = f.Str()
    sections = f.List(SectionSchema, "sections")
