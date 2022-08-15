from yankee.xml import fields as f
from yankee.xml.util import xpath_intersection
from patent_client.util.format import clean_whitespace

import re

whitespace_except_newlines_re = re.compile(r"[ \t\r\f\v]+")
newlines_re = re.compile(r"\n+")

def text_section_xpath(heading):
    ns1 = f'//i[contains(text(), "{heading}")]/ancestor::center/following::hr[1]/following::text()'
    ns2 = f'//i[contains(text(), "{heading}")]/ancestor::center/following::hr[2]/preceding::text()'
    return xpath_intersection(ns1, ns2)

def clean_whitespace(string, preserve_newlines=False):
    ## TODO: Move this to Yankee
    string = string.strip()
    string = whitespace_except_newlines_re.sub(" ", string)
    if preserve_newlines:
        string = newlines_re.sub("\n", string)
    else:
        string = newlines_re.sub(" ", string)
    string = whitespace_except_newlines_re.sub(" ", string)
    return string

class TextField(f.List):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, item_schema=f.Field(), **kwargs)

    def load(self, obj):
        result = super().load(obj)
        text = "\n\n".join(clean_whitespace(p) for p in result).strip()
        #clean_text = "\n\n".join([clean_whitespace(p).strip() for p in text.split("\n\n")])
        return text