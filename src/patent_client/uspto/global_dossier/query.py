import csv
import re
from collections import defaultdict
from pathlib import Path


class QueryException(Exception):
    pass


class QueryBuilder:
    def __init__(self):
        input_file = Path(__file__).parent / "gd_input.csv"
        with input_file.open() as f:
            reader = csv.DictReader(f)
            self.input_schema = list(reader)
        for row in self.input_schema:
            row["pattern"] = re.compile(row["pattern"])
        self.pattern_index = defaultdict(dict)
        for row in self.input_schema:
            self.pattern_index[row["office_code"]][row["type_code"]] = row["pattern"]

        self.country_codes = ["US", "CN", "EP", "KR", "JP", "AU"]

    def validate_query(self, query):
        pattern = self.pattern_index[query["office_code"]][query["type_code"]]
        if not pattern.fullmatch(query["doc_number"]):
            raise QueryException(
                f"{query['doc_number']} is not a valid number for office: {query['office_code']}, type: {query['type_code']}!"
            )
        return query

    def build_query(self, *args, **kwargs):
        query = self.get_candidate_query(*args, **kwargs)
        return self.validate_query(query)

    def get_candidate_query(self, *args, **kwargs):
        if args and len(args) > 1:
            raise QueryException("Cannot provide more than one non-keyword argument!")
        elif args:
            arg = args[0]
            if arg[:2] in ["US", "CN", "EP", "KR", "JP"]:
                country = arg[:2]
                number = arg[2:]
                if "type" in kwargs:
                    return {"office_code": country, "type_code": kwargs["type"], "doc_number": number}
                candidates = [
                    r for r in self.input_schema if r["office_code"] == country and r["pattern"].fullmatch(number)
                ]
                if not candidates:
                    raise QueryException(
                        f"While country was detected as {country}, no number format matched {number}, please check your number"
                    )
                if len(candidates) > 1:
                    raise QueryException(
                        f"Cannot determine number type. Possible types are {[c['type_name'] for c in candidates]}"
                    )
                return {"office_code": country, "doc_number": number, "type_code": candidates[0]["type_code"]}
            elif arg[:3] == "PCT":
                return {"office_code": "WIPO", "type_code": "application", "doc_number": arg}
            elif arg[:2] == "WO":
                return {"office_code": "WIPO", "type_code": "publication", "doc_number": arg}
            elif arg[:2] == "AU":
                if "type" in kwargs:
                    return {"office_code": "CASE", "type_code": kwargs["type"], "doc_number": arg}
                else:
                    raise QueryException(
                        "While country was detected as AU, no type can be inferred. Please pass a 'type' keyword to specify application/publication"
                    )
            else:
                office_code = kwargs.get("office", "US")
                candidates = [
                    r for r in self.input_schema if r["office_code"] == office_code and r["pattern"].fullmatch(arg)
                ]
                if not candidates:
                    raise QueryException(
                        f"While country was detected as {office_code}, no number format matched {arg}, please check your number"
                    )
                if len(candidates) > 1:
                    types = [c["type_name"] for c in candidates]
                    if "Application" in types and office_code == "US":
                        return {"office_code": office_code, "doc_number": arg, "type_code": "application"}
                    raise QueryException(f"Cannot determine number type. Possible types are {types}")
                return {"office_code": office_code, "doc_number": arg, "type_code": candidates[0]["type_code"]}

        elif kwargs:
            numbers = {k: v for k, v in kwargs.items() if k in ("publication", "application", "patent")}
            if len(numbers) > 1:
                raise QueryException("You may only pass one keyword from the set of (application, publication, patent)")
            elif not numbers:
                raise QueryException("No number passed! Please pass a valid number")
            key, value = list(numbers.items())[0]
            if value[:2] in ["US", "CN", "EP", "KR", "JP"]:
                return {"office_code": value[:2], "type_code": key, "doc_number": value[2:]}
            elif value[:2] == "WO" or value[:3] == "PCT":
                return {"office_code": "WIPO", "type_code": key, "doc_number": value}
            elif value[:2] == "AU":
                return {"office_code": "CASE", "type_code": key, "doc_number": value}
            else:
                office_code = kwargs.get("office", "US")
                return {"office_code": office_code, "type_code": key, "doc_number": value}
