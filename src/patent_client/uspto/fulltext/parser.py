import re

from bs4 import BeautifulSoup as bs

from .exceptions import FullTextNotAvailable

WHITESPACE_RE = re.compile(r"\s+")
ALPHA_RE = re.compile(r"[^\w ]")

clean_whitespace = lambda string: WHITESPACE_RE.sub(" ", string).strip()
clean_key = lambda string: WHITESPACE_RE.sub(
    "_", ALPHA_RE.sub("", string).strip().lower()
)


class FullTextParser(object):
    def parse(self, html_text):
        # r"\n\s*<BR>": avoiding possible intermediate tail whitespaces from r"\n\s*"
        # r"\n\s*": \s* is only for extra heading spaces in appft
        # r"<BR>\s*": \s is only for extra heading spaces in patft
        text = re.sub(
            r"<BR>\s*",
            "\n",
            re.sub(r"\n\s*", " ", re.sub(r"\n\s*<BR>", "<BR>", html_text)),
        )
        sections = text.split("<HR>")
        parsed_sections = [
            bs(section.replace("&nbsp", " "), "lxml") for section in sections
        ]

        if "Full text is not available for this patent" in text:
            raise FullTextNotAvailable()
            # This is for very old patents. Fail gently and get what you can.
            # data = dict([c.text.strip() for c in r.find_all(("td", "th"))] for r in parsed_sections[1].find_all("tr"))
            # return {
            #    "publication_number": data['United States Patent'].replace(",", ""),
            #    "publication_date": data['Issue Date:'],
            #    **self.get_classifications(parsed_sections),
            # }

        return {
            "publication_number": self.get_publication_number(parsed_sections),
            "kind_code": self.get_kind_code(parsed_sections),
            "publication_date": self.get_publication_date(parsed_sections),
            "title": self.get_title(parsed_sections),
            "abstract": self.get_abstract(parsed_sections),
            "description": self.get_description(parsed_sections),
            "claims": self.get_claims(parsed_sections),
            "foreign_priority": self.get_foreign_priority_data(parsed_sections),
            "prior_publications": self.get_prior_publication_data(parsed_sections),
            "related_us_applications": self.get_related_patent_documents(
                parsed_sections
            ),
            **self.get_classifications(parsed_sections),
            **self.get_bibliographic_data(parsed_sections),
            **self.get_references_agent_and_examiner(parsed_sections),
        }

    def get_title(self, parsed_sections):
        return clean_whitespace(parsed_sections[2].find("font").text)

    def get_abstract(self, parsed_sections):
        try:
            return clean_whitespace(parsed_sections[2].find("p").text)
        except AttributeError:
            return None

    def get_description(self, parsed_sections):
        section_number = [
            s.find("center", text="Description") is not None for s in parsed_sections
        ].index(True) + 1
        return parsed_sections[section_number].text

    def get_claims(self, parsed_sections):
        section_number = [
            s.find("center", text="Claims") is not None for s in parsed_sections
        ].index(True) + 1
        return parsed_sections[section_number].text

    def get_foreign_priority_data(self, parsed_sections):
        try:
            section_number = [
                s.find("center", text="Foreign Application Priority Data") is not None
                for s in parsed_sections
            ].index(True)
        except ValueError:
            return None
        section = parsed_sections[section_number]
        table = section.find("b", text="Foreign Application Priority Data").find_next(
            "table"
        )

        FOREIGN_PRIORITY_RE = re.compile(
            r"(?P<date>[^[]*)\[(?P<country_code>[^]]*)\](?P<number>.*)"
        )
        return [
            FOREIGN_PRIORITY_RE.match(t.text.strip()).groupdict()
            for t in table.find_all("tr")
            if t.text.strip()
        ]

    def get_classifications(self, parsed_sections):
        cpc_re = re.compile(
            r"(?P<class>[A-Z]\d{2}[A-Z] \d{1,}/\d{2,}) \(?(?P<version>\d{8})?\)?"
        )

        def parse_cpc(element):
            text = element.text.strip()
            try:
                return [cpc_re.search(c).groupdict() for c in text.split(";")]
            except AttributeError:  # Design Patent
                return [
                    {"class": text, "version": None},
                ]

        def parse_us_class(element):
            strings = element.text.strip().strip(";").split("; ")
            return list(
                {"class": c.split("/")[0], "subclass": c.split("/")[1]} for c in strings
            )

        def parse_field_of_search(element):
            groups = element.text.strip().strip(";").split(" ;")
            output = list()
            for group in groups:
                cl, *subcls = re.split("[,/]", group)
                output += [{"class": cl, "subclass": subcl} for subcl in subcls]
            return output

        section_number = [
            s.find("b", text="Current U.S. Class:") is not None for s in parsed_sections
        ].index(True)
        rows = (
            parsed_sections[section_number]
            .find("b", text="Current U.S. Class:")
            .find_parent("table")
            .find_all("tr")
        )

        parsers = {
            "current_cpc_class": parse_cpc,
            "current_international_class": parse_cpc,
            "current_us_class": parse_us_class,
            "class_at_publication": parse_us_class,
            "field_of_search": parse_field_of_search,
        }
        cells = [row.find_all("td") for row in rows]
        data = {clean_key(c[0].text.strip()[:-1]): c[1] for c in cells}
        if "international_class" in data:
            data["current_international_class"] = data["international_class"]
            del data["international_class"]
        return {k: parsers[k](v) for k, v in data.items()}

    def get_bibliographic_data(self, parsed_sections):
        def parse_applicant(element):
            def html_table_to_records(table):
                data = [
                    [c.text.strip() for c in r.find_all(["td", "th"])]
                    for r in table.find_all("tr")
                ]
                headings = [clean_key(k) for k in data[0]]
                return [dict(zip(headings, r)) for r in data[1:]]

            return html_table_to_records(element.find_next("table"))

        def parse_inventors(element):
            inventor_pattern = re.compile(
                r"(?P<last_name>[^;]+); (?P<first_name>[^;]+);? \((?P<city>[^,]+), (?P<region>[^)]+)\)"
            )
            inventors = element.text.strip().split(" ; ")
            return [inventor_pattern.search(i).groupdict() for i in inventors]

        def parse_assignee(element):
            assignee_pattern = re.compile(
                r"(?P<name>[^;]+) \((?P<city>[^,]+), (?P<region>[^)]+)\)"
            )
            assignees = clean_whitespace(element.text.strip()).split(" ; ")
            try:
                return [assignee_pattern.search(a).groupdict() for a in assignees]
            except AttributeError:
                result = list()
                for assignee in assignees:
                    if len(assignee.rsplit(" ", 2)) < 3:  # Where only a name is given
                        result.append({"name": assignee})
                    else:
                        name, city, region = assignee.rsplit(" ", 2)
                        result.append({"name": name, "city": city, "region": region})
                return result

        section_number = [
            s.find(("th", "td"), text="Inventors:") is not None for s in parsed_sections
        ].index(True)
        section = parsed_sections[section_number]

        rows = [r for table in section.find_all("table") for r in table.find_all("tr")]

        data = {
            r.find_all(("td", "th"))[0].text.strip()[:-1]: r.find_all(("td", "th"))[1]
            for r in rows
        }
        parsers = {
            "Applicant": parse_applicant,
            "Inventors": parse_inventors,
            "Assignee": parse_assignee,
        }
        result = {
            clean_key(k): parsers.get(k, lambda x: x.text.strip())(v)
            for k, v in data.items()
        }
        return result

    def get_references_agent_and_examiner(self, parsed_sections):
        def get_us_references(ref_section):
            section = ref_section.find("center", text="U.S. Patent Documents")
            if section is None:
                return list()
            table = section.find_next("table")
            keys = ("publication_number", "date", "name")
            data = [
                [cell.text.strip() for cell in row.find_all(["td", "th"])]
                for row in table.find_all("tr")
            ]
            data = [row for row in data if any(row)]
            return list(dict(zip(keys, row)) for row in data if len(row) == len(keys))

        def get_foreign_references(ref_section):
            section = ref_section.find("center", text="Foreign Patent Documents")
            if section is None:
                return list()
            table = section.find_next("table")
            rows = [row for row in table.find_all("tr") if row.text.strip()]
            return [
                {
                    "publication_number": row.select_one(
                        "td:nth-child(2)"
                    ).text.strip(),
                    "name": row.select_one("td:nth-child(4)").text.strip(),
                    "country_code": row.select_one("td:nth-child(6)").text.strip(),
                }
                for row in rows
            ]

        def get_npl_references(ref_section):
            section = ref_section.find("center", text="Other References")
            if section is None:
                return list()
            return [
                {"citation": cite}
                for cite in section.find_next("td").text.strip().split("\n")
            ]

        try:
            section_number = [
                "References Cited" in s.text for s in parsed_sections
            ].index(True) + 1
        except ValueError:
            return dict()
        section = parsed_sections[section_number]
        examiner = section.find("i", text="Primary Examiner:").next_sibling.strip()

        try:
            agent = (
                section.find("i", text="Attorney, Agent or Firm:")
                .find_next("coma")
                .text.strip()
            )
        except AttributeError:
            agent = None

        return {
            "examiner": examiner,
            "agent": agent,
            "us_references": get_us_references(section),
            "foreign_references": get_foreign_references(section),
            "npl_references": get_npl_references(section),
        }

    def get_publication_date(self, parsed_sections):
        return (
            parsed_sections[1]
            .find_all("td", align=re.compile("right", re.IGNORECASE))[-1]
            .text.strip()
            .replace(",", "")
        )

    def get_publication_number(self, parsed_sections):
        return (
            parsed_sections[1]
            .find("td", align=re.compile("right", re.IGNORECASE))
            .text.strip()
            .replace(",", "")
        )

    def get_kind_code(self, parsed_sections):
        section = parsed_sections[1]
        headings = [
            i.text.strip()
            for i in section.find_all("td", align=re.compile("left", re.IGNORECASE))
        ]
        if "Kind Code" in headings:
            return section.select("td[align='RIGHT']")[1].text.strip()

        has_publication_data = any(
            s.find("center", text="Prior Publication Data") is not None
            for s in parsed_sections
        )
        if has_publication_data:
            return "B2"
        else:
            return "B1"

    def get_prior_publication_data(self, parsed_sections):
        try:
            section_number = [
                s.find("center", text="Prior Publication Data") is not None
                for s in parsed_sections
            ].index(True) + 1
        except ValueError:
            return list()
        section = parsed_sections[section_number]
        to_text = lambda lst: [i.text.strip() for i in lst]
        return [
            dict(
                zip(
                    ("publication_number", "publication_date"),
                    to_text(r.find_all("td")[1:]),
                )
            )
            for r in section.find("table").find_all("tr")[2:-1]
        ]

    def get_related_patent_documents(self, parsed_sections):
        try:
            section_number = [
                s.find("center", text="Related U.S. Patent Documents") is not None
                for s in parsed_sections
            ].index(True) + 1
        except ValueError:
            return list()
        section = parsed_sections[section_number]
        to_text = lambda lst: [i.text.strip() for i in lst]

        return [
            dict(
                zip(
                    ("appl_id", "filing_date", "patent_number"),
                    to_text(r.find_all("td")[1:]),
                )
            )
            for r in section.find("table").find_all("tr")[2:-1]
        ]
