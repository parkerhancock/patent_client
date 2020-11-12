import re
from itertools import zip_longest

from .model import Claim

SPLIT_RE = re.compile(
    r"^\s*([\d\-\.]+[\)\.]|\.Iadd\.[\d\-\.]+\.|\.\[[\d\-\.]+\.)", flags=re.MULTILINE
)
NUMERIC_RE = re.compile(r"\d")
DEPENDENCY_RE = re.compile(r"(c|C)laim (?P<number>\d+)")
LIMITATION_RE = re.compile(r"(\s*[:;]\s*and|\s*[:;]\s*)", flags=re.IGNORECASE)
NUMBER_RE = re.compile(r"(?P<number>\d+)[\)\.]\s+")
WHITESPACE_RE = re.compile(r"\s+")

clean_text = lambda text: WHITESPACE_RE.sub(" ", text).strip()

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

class ClaimsParser(object):
    def parse(self, claim_text):
        claim_strings = self.split_and_clean_claims(claim_text)
        claim_data = [self.parse_claim_string(string) for string in claim_strings]
        claims = [Claim(**d) for d in claim_data]
        claim_dictionary = {c.number: c for c in claims}
        for claim in claims:
            if claim.depends_on is not None:
                depends_on = claim_dictionary[claim.depends_on]
                claim.depends_on_claim = depends_on
                depends_on.dependent_claims.append(claim)
        return claims
                


    def split_and_clean_claims(self, claim_text):
        claim_strs = [claim.strip() for claim in SPLIT_RE.split(claim_text)]
        # Remove preamble - e.g. "We Claim:"
        while not NUMERIC_RE.search(claim_strs[0]):
            claim_strs.pop(0)
        # Group number and subsequent claim together
        claim_strs = list(grouper(claim_strs, 2))
        # Join strings

        claims = list()
        for claim_str in claim_strs:
            claim_number = claim_str[0]
            if "-" in claim_number: # Handle cancelled claims (e.g. in reissues)
                claim_number = claim_number.replace(".", "")
                start, end, *_ = re.split(r"[^\d]+", claim_number)
                claim_range = list(
                    str(num) for num in range(int(start), int(end) + 1)
                )
                for num in claim_range:
                    claims.append(num + ". " + claim_str[1])
            else:
                claim_string = " ".join(claim_str)
                claims.append(claim_string)
        return claims

    def parse_claim_string(self, text):
        def get_dependency(text):
            dependency = DEPENDENCY_RE.search(text)
            return None if dependency is None else int(dependency.group("number"))
        number = int(NUMBER_RE.search(text).group("number"))
        text = NUMBER_RE.sub("", text)
        return {
            "number": number,
            #"text": NUMBER_RE.sub("", text),
            "limitations": [
                clean_text("".join(lim))
                for lim in list(grouper(LIMITATION_RE.split(text), 2, ""))
            ],
            "depends_on": get_dependency(text)
        }