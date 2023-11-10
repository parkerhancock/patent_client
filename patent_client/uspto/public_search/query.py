import csv
import datetime
from collections.abc import Sequence
from pathlib import Path

from dateutil.parser import parse as parse_dt
from dateutil.parser._parser import ParserError


class QueryException(Exception):
    pass


class QueryBuilder:
    def __init__(self):
        config_file = Path(__file__).parent / "query_config.csv"
        with config_file.open(encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            config = list(reader)
        self.search_keywords = {r["keyword"]: r["query_field"] for r in config if r["query_field"]}
        self.order_by_keywords = {r["keyword"]: r["order_by_field"] for r in config if r["order_by_field"]}
        self.date_fields = [r["keyword"] for r in config if r["is_date"] == "X"]

    def convert_date(self, date):
        if isinstance(date, str):
            try:
                return parse_dt(date).strftime("%Y%m%d")
            except ParserError:
                raise QueryException(f"{date} is not a valid date!")
        elif isinstance(date, (datetime.date, datetime.datetime)):
            return date.strftime("%Y%m%d")
        else:
            raise QueryException(f"{date} is not a valid date!")

    def is_sequence(self, value):
        return isinstance(value, Sequence) and not isinstance(value, str)

    def query_value(self, key, value):
        field, *_ = key.split("__")
        if field in self.date_fields and "__" not in key:
            if isinstance(value, str) and "->" in value:
                start, end = value.split("->")
                return f"@{self.search_keywords[key]}>={self.convert_date(start)}<={self.convert_date(end)}"
            else:
                return f'@{self.search_keywords[key]}="{self.convert_date(value)}"'
        elif field in self.date_fields and "__" in key:
            field, modifier = key.split("__")
            if modifier == "range":
                if not self.is_sequence(value) and len(value) == 2:
                    raise ValueError(f"Input {value} is not a valid date range! Must be a tuple/list of length 2")
                # breakpoint()
                return f"@{self.search_keywords[field]}>={self.convert_date(value[0])}<={self.convert_date(value[1])}"
            elif modifier == "lt":
                return f'@{self.search_keywords[field]}<"{self.convert_date(value)}"'
            elif modifier == "lte":
                return f'@{self.search_keywords[field]}<="{self.convert_date(value)}"'
            elif modifier == "gt":
                return f'@{self.search_keywords[field]}>"{self.convert_date(value)}"'
            elif modifier == "gte":
                return f'@{self.search_keywords[field]}>="{self.convert_date(value)}"'
            else:
                raise ValueError(f"Modifier {modifier} is invalid! must be one of range, lt, lte, gt, gte")
        elif self.is_sequence(value) and len(value) > 1:
            value = " ".join(f'"{v}"' for v in value)
            return f"({value}).{self.search_keywords[key]}."
        elif self.is_sequence(value) and len(value) == 1:
            return f'"{value[0]}".{self.search_keywords[key]}.'
        else:
            return f'"{value}".{self.search_keywords[key]}.'

    def build_query(self, config):
        query_components = list()
        for key, value in config.filter.items():
            if key == "query":
                query_components.append(value)
                continue
            if key.split("__")[0] not in self.search_keywords:
                raise QueryException(f"{key} is not a valid search field!")
            else:
                query_components.append(self.query_value(key, value))
        default_operator = config.options.get("default_operator", "AND")
        return f" {default_operator} ".join(query_components)

    def build_order_by(self, config):
        if not config.order_by:
            return "date_publ desc"
        order_str = list()
        for value in config.order_by:
            if value.startswith("+"):
                order_str.append(f"{self.order_by_keywords[value[1:]]} asc")
            elif value.startswith("-"):
                order_str.append(f"{self.order_by_keywords[value[1:]]} desc")
            else:
                order_str.append(f"{self.order_by_keywords[value]} asc")
        return " ".join(order_str)
