import re

SERIAL_RE = re.compile(r"[\d\-\/\,]{2,}")
NUMBER_CLEAN_RE = re.compile(r"[^\d]+")
PUNCTUATION_AND_WHITESPACE_CLEAN_RE = re.compile(r"\W+")
COUNTRY_CODE_RE = re.compile(r"^[A-Z]{2,3}")
KIND_CODE_RE = re.compile(r"[A-Z]\d?$")
COUNTRY_CODES = ["US", "EP", "PCT", "WO", "CA"]

"""
RESOURCES:

General Info: https://www.epo.org/searching-for-patents/helpful-resources.html
Numbering Systems: http://www.wipo.int/export/sites/www/standards/en/pdf/07-02-02.pdf
Kind Codes: http://www.wipo.int/export/sites/www/standards/en/pdf/07-03-02.pdf


"""


def parse(number, *args, **kwargs):
    if type(number) == str and "PCT" in number:
        return PCTApplication(number, *args, **kwargs)
    else:
        return PatentNumber(number, *args, **kwargs)


class PatentNumber:
    def __init__(self, number, country=None):
        self.number = None
        self.kind_code = None
        self.country = country
        self.number = number

        if type(number) == str:
            number = number.strip().upper()
            if "RE" in number:
                number = number.replace("US", "")
                self.number = PUNCTUATION_AND_WHITESPACE_CLEAN_RE.sub("", number)
                self._handle_us_number()
                return

            kind_code_match = KIND_CODE_RE.search(number)
            if kind_code_match:
                self.kind_code = kind_code_match.group()
            if not country:
                country_code_match = COUNTRY_CODE_RE.match(number)
                if country_code_match:
                    country_code = country_code_match.group()
                    self.country = country_code
                    number = SERIAL_RE.search(number).group()
                    self.number = PUNCTUATION_AND_WHITESPACE_CLEAN_RE.sub("", number)
            if self.country == "US":
                self._handle_us_number()
            elif self.country == "CA":
                self._handle_ca_number()
            else:
                self.number = NUMBER_CLEAN_RE.sub("", number)
                self._handle_us_number()

        if type(number) == int:
            self.number = str(number)
            self._handle_us_number()

    def __repr__(self):
        return f"<PatentNumber(type={self.type}, country={self.country}, number={self.number}, kind={self.kind_code})>"

    def _handle_us_number(self):
        if "RE" in self.number:
            self.country = "US"
            self.type = "patent"
            self.kind_code = "E1"
        elif int(self.number) > 90_000_000:
            self.country = "US"
            self.type = "pre-grant publication"
            self.kind_code = "A1"
        elif int(self.number) < 11_000_000:
            self.country = "US"
            self.type = "patent"
            self.kind_code = "B2"
        else:
            self.country = "US"
            self.type = "application"
            self.kind_code = ""

    def _handle_ca_number(self):
        if not self.kind_code:
            self.kind_code = "A"

        ca_kind_codes = {
            "A": "application",
            "A1": "publication",
            "B": "patent",
            "C": "patent",
            "E": "reissue patent",
            "F": "reexamined patent",
        }
        self.type = ca_kind_codes[self.kind_code]

    def display(self):
        if self.country == "US":
            if self.type == "pre-grant publication":
                formatted_number = self.number[:4] + "/" + self.number[4:]
            elif self.type == "patent" and self.number.isdigit():
                formatted_number = "{:,}".format(int(self.number))
            elif self.type == "patent":
                formatted_number = self.number
            elif self.type == "application":
                formatted_number = (
                    self.number[:2] + "/" + "{:,}".format(int(self.number[2:]))
                )
            return f"US {formatted_number} {self.kind_code}".strip()
        elif self.country == "CA":
            return f"CA {self.number} {self.kind_code}"

    def abbreviation(self):
        if self.type == "pre-grant publication":
            return "U.S. Pub. Patent App."
        elif self.type == "patent":
            return "U.S. Patent"
        elif self.type == "application":
            return "U.S. Patent App."

    def __str__(self):
        return f"{self.country}{self.number}{self.kind_code}"


class PCTApplication:
    def __init__(self, number):
        chunks = number.split("/")
        if len(chunks) == 3:
            self.country, year = chunks[1][:2], chunks[1][2:]
            if len(year) == 2:
                if int(year) < 50:
                    year = "20" + year
                else:
                    year = "19" + year
            self.year = year
            self.number = chunks[2].rjust(6, "0")
            self.type = "international application"
            self.kind_code = ""

    def display(self, style="old"):
        if style == "old":
            return f"PCT/{self.country}{self.year[2:]}/{self.number[-5:]}"
        elif style == "new":
            return f"PCT/{self.country}{self.year}/{self.number}"
        else:
            raise ValueError()

    def __str__(self):
        return f"PCT{self.country}{self.year}{self.number}"

    def __repr__(self):
        return f"<PCTApplication(country_code={self.country}, year={self.year}, number={self.number})>"
