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


non_digit_re = re.compile(r"[^\d]+")


def clean_number(string):
    return non_digit_re.sub("", string)


def clean_appl_id(string):
    return string.replace(",", "").replace("/", "").replace("D", "29").strip()
