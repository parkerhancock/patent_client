import datetime
import math
import re
import xml.etree.ElementTree as ET

from dateutil.parser import parse as parse_date
from inflection import underscore


class AssignmentParser:
    def parse(self, text):
        tree = ET.fromstring(text.encode("utf-8"))
        result = tree.find("./result")
        docs = [self.parse_doc(e) for e in result]
        num_found = int(result.attrib["numFound"])
        return {
            "num_found": num_found,
            "docs": docs
        }

    def parse_doc(self, element):
        doc = self.xml_to_dict(element)
        doc[
            "image_url"
        ] = f'http://legacy-assignments.uspto.gov/assignments/assignment-pat-{doc["display_id"]}.pdf'
        doc['assignors'] = self.lists_to_records(doc, ["patAssignorName", "patAssignorExDate", "patAssignorDateAck"])
        doc['assignees'] = self.lists_to_records(doc, ["patAssigneeName", "patAssigneeAddress1", "patAssigneeAddress2", "patAssigneeCity", "patAssigneeState", "patAssigneeCountryName", "patAssigneePostcode"])
        doc['properties'] = self.lists_to_records(doc, ["inventionTitle", "inventionTitleLang", "applNum", "filingDate", "intlPubDate", "intlRegNum", "inventors", "issueDate", "patNum", "pctNum", "publDate", "publNum"])
        return doc

    def lists_to_records(self, doc, fields):
        lists = [doc[f] for f in fields]
        records = [dict(zip(fields, v)) for v in zip(*lists)]
        for f in fields:
            del doc[f]
        return records

    def xml_to_list(self, element):
        output = list()
        for el in list(element):
            output.append(self.xml_to_pytype(el))
        if len(output) == 1:
            output = output[0]
        return output

    def xml_to_pytype(self, element):
        if element.text == "NULL":
            return None
        elif element.tag == "str":
            return element.text
        elif element.tag == "date":
            # To ensure the result is JSON-serializable, convert to isoformat
            date = parse_date(element.text).date()
            if date < parse_date("1776-01-01").date():
                return None
            return date.isoformat()
        elif element.tag == "int" or element.tag == "long":
            return int(element.text)

    def xml_to_dict(self, element):
        output = dict()
        for el in list(element):
            key = el.attrib["name"]
            key = underscore(key)
            if el.tag == "arr" or el.tag == "lst":
                value = self.xml_to_list(el)
            else:
                value = self.xml_to_pytype(el)
            output[key] = value
        return output