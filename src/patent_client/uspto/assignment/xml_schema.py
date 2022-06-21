import lxml.etree as ET

from yankee.xml import fields as f
from yankee.xml import Schema
from yankee.util import unzip_records

from .model import Assignee
from .model import Assignment
from .model import Assignor
from .model import Property

# Schemas

class BaseSchema(Schema):
    def post_load(self, obj):
        return self.__model__(**obj)

class BaseZipSchema(BaseSchema):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        return unzip_records(obj)

    def post_load(self, obj):
        return [self.__model__(**o) for o in obj]

class PropertySchema(BaseZipSchema):
    __model__ = Property
    invention_title = f.List(f.Str(".//inventionTitle"))
    inventors = f.List(f.Str(".//inventors"))
    # Numbers
    appl_id = f.List(f.Str(".//applNum"))
    pct_num = f.List(f.Str(".//pctNum"))
    intl_reg_num = f.List(f.Str(".//intlRegNum"))
    publ_num = f.List(f.Str(".//publNum"))
    pat_num = f.List(f.Str(".//patNum"))
    # Dates
    filing_date = f.List(f.Date(".//filingDate"))
    intl_publ_date = f.List(f.Date(".//intlPublDate"))
    issue_date = f.List(f.Date(".//issueDate"))
    publ_date = f.List(f.Date(".//publDate"))


class AssignorSchema(BaseZipSchema):
    __model__ = Assignor
    name = f.List(f.Str(".//patAssignorName"))
    ex_date = f.List(f.Date(".//patAssignorExDate"))
    date_ack = f.List(f.Date(".//patAssignorDateAck"))

class AssigneeSchema(BaseZipSchema):
    __model__ = Assignee
    name = f.List(f.Str(".//patAssigneeName"))
    line_1 = f.List(f.Str(".//patAssigneeAddress1"))
    line_2 = f.List(f.Str(".//patAssigneeAddress2"))
    city = f.List(f.Str(".//patAssigneeCity"))
    state = f.List(f.Str(".//patAssigneeState"))
    post_code = f.List(f.Str(".//patAssigneePostcode"))
    country = f.List(f.Str(".//patAssigneeCountryName"))
    
    def deserialize(self, obj):
        return [ {
            "name": o.name,
            "address": self.combine_func(o)
        } for o in super().deserialize(obj)]

    def combine_func(self, obj):
        address = f"{obj.get('line_1', '')}\n{obj.get('line_2', '')}".strip()
        if 'city' in obj:
            address += f"\n{obj.get('city', '')}, {obj.get('state', '')}"
        if 'country' in obj:
            address += f"({obj.get('post_code', '')})"
        return address


class CorrespondentAddressField(f.Combine):
    corrAddress1 = f.Str(".//corrAddress1")
    corrAddress2 = f.Str(".//corrAddress2")
    corrAddress3 = f.Str(".//corrAddress3")
    corrAddress4 = f.Str(".//corrAddress4")

    def combine_func(self, obj):
        out = str()
        for i in range(1, 5):
            out += obj.get(f"corrAddress{i}", '') + "\n"
        return out.strip()

class AssignmentSchema(BaseSchema):
    __model__ = Assignment
    id = f.Str(".//id")
    conveyance_text = f.Str(".//conveyanceText", formatter=lambda s: s.replace("(SEE DOCUMENT FOR DETAILS).", "").strip())
    date_produced = f.Date(".//dateProduced")
    corr_name = f.Str(".//corrName")
    corr_address = CorrespondentAddressField(False)
    assignment_record_has_images = f.Bool(".//assignmentRecordHasImages", true_value="Y")
    page_count = f.Int(".//pageCount")
    transaction_date = f.Date(".//transactionDate")
    last_update_date = f.Date(".//lastUpdateDate")
    recorded_date = f.Date(".//recordedDate")
    properties = PropertySchema
    assignors = AssignorSchema
    assignees = AssigneeSchema

class AssignmentPageSchema(Schema):
    num_found = f.Int(".//result/@numFound")
    docs = f.List(AssignmentSchema, f".//result/doc")

    def pre_load(self, text):
        tree = ET.fromstring(text.encode())
        for e in tree.find(".//result/*").getiterator():
            if "name" in e.attrib:
                e.tag = e.attrib["name"]
                del e.attrib["name"]
        return tree