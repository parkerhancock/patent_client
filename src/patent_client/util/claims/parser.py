import re
from itertools import zip_longest

from yankee.data import ListCollection
from yankee.util import AttrDict

from .model import Claim

SPLIT_RE = re.compile(r"^\s*([\d\-\.]+[\)\.]|\.Iadd\.[\d\-\.]+\.|\.\[[\d\-\.]+\.)", flags=re.MULTILINE)
NUMERIC_RE = re.compile(r"\d")

LIMITATION_RE = re.compile(r"(\s*[:;]\s*and|\s*[:;]\s*)", flags=re.IGNORECASE)
NUMBER_RE = re.compile(r"(?P<number>\d+)[\)\.]\s+")
WHITESPACE_RE = re.compile(r"\s+")
CLAIM_INTRO_RE = re.compile(r"^[^\d\.\[]+")

DEPENDENCY_RE = re.compile(r"claims? (?P<number>[\d,or ]+)", flags=re.IGNORECASE)
DEPENDENT_CLAIMS_RE = re.compile(r"(?P<number>\d+)([^\d]|$)")
DEPEND_ALL_RE = re.compile(r"(any of the foregoing claims|any of the previous claims)", flags=re.IGNORECASE)

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
        claim_dictionary = {c.number: c for c in claim_data}
        for claim in claim_data:
            for d in claim.depends_on:
                claim_dictionary[d].dependent_claims.append(claim["number"])
        return ListCollection(Claim(**d) for d in claim_data)

    def split_and_clean_claims(self, claim_text):
        claim_text = CLAIM_INTRO_RE.sub("", claim_text)
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
            if "-" in claim_number:  # Handle cancelled claims (e.g. in reissues)
                claim_number = claim_number.replace(".", "")
                start, end, *_ = re.split(r"[^\d]+", claim_number)
                claim_range = list(str(num) for num in range(int(start), int(end) + 1))
                for num in claim_range:
                    claims.append(num + ". " + claim_str[1])
            else:
                claim_string = " ".join(claim_str)
                claims.append(claim_string)
        return claims

    def parse_claim_string(self, text):
        number = int(NUMBER_RE.search(text).group("number"))
        text = NUMBER_RE.sub("", text)
        return AttrDict.convert(
            {
                "number": number,
                # "text": NUMBER_RE.sub("", text),
                "limitations": [clean_text("".join(lim)) for lim in list(grouper(LIMITATION_RE.split(text), 2, ""))],
                "depends_on": self.parse_dependency(text, number),
                "dependent_claims": list(),
            }
        )

    def parse_dependency(self, text, number):
        dependency = DEPENDENCY_RE.search(text)
        if dependency is not None:
            claims = dependency.groupdict()["number"]
            claim_numbers = [int(m.groupdict()["number"]) for m in DEPENDENT_CLAIMS_RE.finditer(claims)]
            return claim_numbers
        elif DEPEND_ALL_RE.search(text):
            return list(range(1, number))
        else:
            return list()
