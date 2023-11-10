import re

import lxml.html as ETH

newline_re = re.compile(r"<br />\s*")
bad_break_re = re.compile(r"<br />\s+")


def html_to_text(html):
    html = newline_re.sub("\n\n", html)
    # html = bad_break_re.sub(" ", html)
    return "".join(ETH.fromstring(html).itertext())
