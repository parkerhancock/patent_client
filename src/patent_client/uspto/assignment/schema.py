import datetime
from typing import *

from yankee.xml.schema import fields as f
from yankee.xml.schema import Schema
from yankee.xml.schema import ZipSchema


# Schemas
class Str(f.String):
    def deserialize(self, elem) -> "Optional[str]":
        result = super().deserialize(elem)
        return result if result != "NULL" else None


class Date(f.Date):
    def deserialize(self, elem) -> "Optional[datetime.date]":
        result = super().deserialize(elem)
        return result if result != datetime.date(1, 1, 1) else None


class PropertySchema(ZipSchema):
    invention_title = Str(".//inventionTitle/str")
    inventors = Str(".//inventors/str")
    # Numbers
    appl_id = Str(".//applNum/str")
    pct_num = Str(".//pctNum/str")
    intl_reg_num = Str(".//intlRegNum/str")
    publ_num = Str(".//publNum/str")
    pat_num = Str(".//patNum/str")
    # Dates
    filing_date = Date(".//filingDate/date")
    intl_publ_date = Date(".//intlPublDate/date")
    issue_date = Date(".//issueDate/date")
    publ_date = Date(".//publDate/date")


class AssignorSchema(ZipSchema):
    name = Str(".//patAssignorName/str")
    ex_date = Date(".//patAssignorExDate/date")
    date_ack = Date(".//patAssignorDateAck/date")


class AssigneeSchema(ZipSchema):
    name = Str(".//patAssigneeName/str")
    line_1 = Str(".//patAssigneeAddress1/str")
    line_2 = Str(".//patAssigneeAddress2/str")
    city = Str(".//patAssigneeCity/str")
    state = Str(".//patAssigneeState/str")
    post_code = Str(".//patAssigneePostcode/str")
    country = Str(".//patAssigneeCountryName/str")

    def post_load(self, obj):
        return [{"name": o.name, "address": self.combine_func(o)} for o in obj]

    def combine_func(self, obj):
        address = f"{obj.get('line_1', '')}\n{obj.get('line_2', '')}".strip()
        if "city" in obj:
            address += f"\n{obj.get('city', '')}, {obj.get('state', '')} {obj.get('post_code', '')}".rstrip()
        if "country" in obj:
            address += f" ({obj.get('country', '')})"
        return address


class CorrespondentAddressField(f.Combine):
    corrAddress1 = Str(".//corrAddress1")
    corrAddress2 = Str(".//corrAddress2")
    corrAddress3 = Str(".//corrAddress3")
    corrAddress4 = Str(".//corrAddress4")

    def combine_func(self, obj):
        out = str()
        for i in range(1, 5):
            out += obj.get(f"corrAddress{i}", "") + "\n"
        return out.strip()


class AssignmentSchema(Schema):
    id = Str(".//id")
    conveyance_text = Str(
        ".//conveyanceText",
        formatter=lambda s: s.replace("(SEE DOCUMENT FOR DETAILS).", "").strip(),
    )
    date_produced = Date(".//dateProduced")
    corr_name = Str(".//corrName")
    corr_address = CorrespondentAddressField()
    assignment_record_has_images = f.Bool(".//assignmentRecordHasImages", true_value="Y")
    page_count = f.Int(".//pageCount")
    transaction_date = Date(".//transactionDate")
    last_update_date = Date(".//lastUpdateDate")
    recorded_date = Date(".//recordedDate")
    properties = PropertySchema()
    assignors = AssignorSchema()
    assignees = AssigneeSchema()


class AssignmentPageSchema(Schema):
    num_found = f.Int(".//response/@numFound")
    docs = f.List(AssignmentSchema, ".//response/doc")

    def pre_load(self, obj):
        for e in obj.find(".//result").iter():
            if "name" in e.attrib:
                e.tag = e.attrib["name"]
                del e.attrib["name"]
        return obj
