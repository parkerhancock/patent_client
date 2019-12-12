import math
import re
import datetime
import xml.etree.ElementTree as ET
from dateutil.parser import parse as parse_date
from inflection import underscore

class AssignmentParser:
    def parse(self, text):
        tree = ET.fromstring(text.encode("utf-8"))
        result = tree.find("./result")
        num_found = int(result.attrib["numFound"])
        return num_found, [self.doc(doc) for doc in result]

    def doc(self, element):
        data = self.xml_to_dict(element)
        data[
            "image_url"
        ] = f'http://legacy-assignments.uspto.gov/assignments/assignment-pat-{data["display_id"]}.pdf'
        return data

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