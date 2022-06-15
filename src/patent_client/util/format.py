import re

whitespace_except_newlines_re = re.compile(r"[ \t\r\f\v]+")
newlines_re = re.compile(r"\n+")

def clean_whitespace(string, preserve_newlines=False):
    string = string.strip()
    string = whitespace_except_newlines_re.sub(" ", string)
    if preserve_newlines:
        string = newlines_re.sub("\n", string)
    else:
        string = newlines_re.sub(" ", string)
    return string