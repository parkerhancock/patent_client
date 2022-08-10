from yankee.xml import fields as f
from yankee.xml.util import xpath_intersection
from patent_client.util.format import clean_whitespace

def text_section_xpath(heading):
    ns1 = f'//i[contains(text(), "{heading}")]/ancestor::center/following::hr[1]/following::text()'
    ns2 = f'//i[contains(text(), "{heading}")]/ancestor::center/following::hr[2]/preceding::text()'
    return xpath_intersection(ns1, ns2)

class TextField(f.List):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, item_schema=f.Field(), **kwargs)

    def load(self, obj):
        result = super().load(obj)
        text = "\n".join(result).strip()
        return "\n\n".join([clean_whitespace(p) for p in text.split("\n\n")])