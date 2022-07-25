import lxml.etree as ET
import datetime

from yankee.xml import fields as f
from yankee.xml import Schema
from yankee.util import unzip_records

from .model import Assignee, AssignmentPage
from .model import Assignment
from .model import Assignor
from .model import Property

# Schemas

class BaseSchema(Schema):
    def post_load(self, obj):
        if not obj:
            return None
        try:
            return self.__model__(**obj)
        except TypeError as e:
            raise TypeError(f"{e.args[0]}\nInput Data: {obj}")

class BaseZipSchema(BaseSchema):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        return unzip_records(obj)

    def post_load(self, obj):
        return [self.__model__(**o) for o in obj]

class Str(f.String):
    def deserialize(self, elem) -> "Optional[str]":
        result = super().deserialize(elem)
        return result if result != "NULL" else None

class Date(f.Date):
    def deserialize(self, elem) -> "Optional[datetime.date]":
        result = super().deserialize(elem)
        return result if result != datetime.date(1, 1, 1) else None

class PropertySchema(BaseZipSchema):
    __model__ = Property
    invention_title = f.List(Str(),".//inventionTitle/str")
    inventors = f.List(Str(),".//inventors/str")
    # Numbers
    appl_id = f.List(Str(),".//applNum/str")
    pct_num = f.List(Str(),".//pctNum/str")
    intl_reg_num = f.List(Str(),".//intlRegNum/str")
    publ_num = f.List(Str(),".//publNum/str")
    pat_num = f.List(Str(),".//patNum/str")
    # Dates
    filing_date = f.List(Date(), ".//filingDate/date")
    intl_publ_date = f.List(Date(), ".//intlPublDate/date")
    issue_date = f.List(Date(), ".//issueDate/date")
    publ_date = f.List(Date(), ".//publDate/date")


class AssignorSchema(BaseZipSchema):
    __model__ = Assignor
    name = f.List(Str(), ".//patAssignorName/str")
    ex_date = f.List(Date(), ".//patAssignorExDate/date")
    date_ack = f.List(Date(), ".//patAssignorDateAck/date")  


class AssigneeSchema(BaseZipSchema):
    __model__ = Assignee
    name = f.List(Str(), ".//patAssigneeName/str")
    line_1 = f.List(Str(), ".//patAssigneeAddress1/str")
    line_2 = f.List(Str(), ".//patAssigneeAddress2/str")
    city = f.List(Str(), ".//patAssigneeCity/str")
    state = f.List(Str(), ".//patAssigneeState/str")
    post_code = f.List(Str(), ".//patAssigneePostcode/str")
    country = f.List(Str(), ".//patAssigneeCountryName/str")
    
    def deserialize(self, obj):
        return [ {
            "name": o.name,
            "address": self.combine_func(o)
        } for o in super().deserialize(obj)]

    def combine_func(self, obj):
        address = f"{obj.get('line_1', '')}\n{obj.get('line_2', '')}".strip()
        if 'city' in obj:
            address += f"\n{obj.get('city', '')}, {obj.get('state', '')} {obj.get('post_code', '')}".rstrip()
        if 'country' in obj:
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
            out += obj.get(f"corrAddress{i}", '') + "\n"
        return out.strip()

class AssignmentSchema(BaseSchema):
    __model__ = Assignment
    id = Str(".//id")
    conveyance_text = Str(".//conveyanceText", formatter=lambda s: s.replace("(SEE DOCUMENT FOR DETAILS).", "").strip())
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

class AssignmentPageSchema(BaseSchema):
    __model__ = AssignmentPage
    num_found = f.Int(".//response/@numFound")
    docs = f.List(AssignmentSchema, ".//response/doc")

    def pre_load(self, text):
        tree = ET.fromstring(text.encode())
        for e in tree.find(".//result").iter():
            if "name" in e.attrib:
                e.tag = e.attrib["name"]
                del e.attrib["name"]
        return tree