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
            "numFound": num_found,
            "docs": docs
        }

    def parse_doc(self, element):
        doc = self.xml_to_dict(element)
        doc[
            "imageUrl"
        ] = f'http://legacy-assignments.uspto.gov/assignments/assignment-pat-{doc["displayId"]}.pdf'
        doc['assignors'] = self.lists_to_records(doc, ["patAssignorName", "patAssignorExDate", "patAssignorDateAck"])
        doc['assignees'] = self.lists_to_records(doc, ["patAssigneeName", "patAssigneeAddress1", "patAssigneeAddress2", "patAssigneeCity", "patAssigneeState", "patAssigneeCountryName", "patAssigneePostcode"])
        doc['properties'] = self.lists_to_records(doc, ["inventionTitle", "inventionTitleLang", "applNum", "filingDate", "intlPubDate", "intlRegNum", "inventors", "issueDate", "patNum", "pctNum", "publDate", "publNum"])
        return doc

    def lists_to_records(self, doc, fields):
        lists = [doc.get(f, list()) for f in fields]
        max_length = max(len(l) for l in lists)
        for l in lists:
            l += [None, ] * (max_length - len(l))

        records = [dict(zip(fields, v)) for v in zip(*lists)]
        for f in fields:
            if f in doc: del doc[f]
        return records

    def xml_to_dict(self, el):
        if el.tag in ("arr", "lst"):
            return [self.xml_to_dict(e) for e in el]
        elif el.text == "NULL":
            return None
        elif el.tag in ("str", "date"):
            return el.text
        elif el.tag == "int" or el.tag == "long":
            return int(el.text)
        else:
            return {e.attrib['name']: self.xml_to_dict(e) for e in el}

    """
    def xml_to_list(self, element):
        output = list()
        for el in element:
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
            if el.tag in ("arr", "lst"):
                value = self.xml_to_list(el)
            else:
                value = self.xml_to_pytype(el)
            output[key] = value
        return output
    """