from yankee.json import fields
from yankee.json import Schema

from .model import Assignee
from .model import Assignment
from .model import Assignor
from .model import Property

# Schemas

class BaseSchema(Schema):
    def post_load(self, obj):
        return self.__model__(**obj)

class PropertySchema(BaseSchema):
    __model__ = Property
    invention_title = fields.Str()
    inventors = fields.Str()
    # Numbers
    appl_id = fields.Str(data_key="appl_num")
    pct_num = fields.Str()
    intl_reg_num = fields.Str()
    publ_num = fields.Str()
    pat_num = fields.Str()
    # Dates
    filing_date = fields.Date()
    intl_publ_date = fields.Date()
    issue_date = fields.Date()
    publ_date = fields.Date()


class AssignorSchema(BaseSchema):
    __model__ = Assignor
    name = fields.Str(data_key="patAssignorName")
    ex_date = fields.Date(data_key="patAssignorExDate")
    date_ack = fields.Date(data_key="patAssignorDateAck")

    def deserialize(self, obj) -> "Dict":
        d_obj = super().deserialize(obj)
        return d_obj

class AssigneeAddress(fields.Combine):
    line_1 = fields.Str("patAssigneeAddress1")
    line_2 = fields.Str("patAssigneeAddress2")
    city = fields.Str("patAssigneeCity")
    state = fields.Str("patAssigneeState")
    post_code = fields.Str("patAssigneePostcode")
    country = fields.Str("patAssigneeCountryName")

    def combine_func(self, obj):
        address = f"{obj.get('line_1', '')}\n{obj.get('line_2', '')}".strip()
        if 'city' in obj:
            address += f"\n{obj.get('city', '')}, {obj.get('state', '')}"
        if 'country' in obj:
            address += f"({obj.get('post_code', '')})"
        return address

class AssigneeSchema(BaseSchema):
    __model__ = Assignee
    name = fields.Str(data_key="patAssigneeName")
    address = AssigneeAddress(None)


class CorrespondentAddressField(fields.Combine):
    corrAddress1 = fields.Str()
    corrAddress2 = fields.Str()
    corrAddress3 = fields.Str()
    corrAddress4 = fields.Str()

    def combine_func(self, obj):
        out = str()
        for i in range(1, 5):
            out += obj.get(f"corrAddress{i}", '') + "\n"
        return out.strip()

class AssignmentSchema(BaseSchema):
    __model__ = Assignment
    id = fields.Str()
    conveyance_text = fields.Str(formatter=lambda s: s.replace("(SEE DOCUMENT FOR DETAILS).", "").strip())
    date_produced = fields.Date()
    corr_name = fields.Str()
    corr_address = CorrespondentAddressField(False)
    assignment_record_has_images = fields.Bool(true_value="Y")
    page_count = fields.Int()
    transaction_date = fields.Date()
    last_update_date = fields.Date()
    recorded_date = fields.Date()
    properties = fields.List(PropertySchema)
    assignors = fields.List(AssignorSchema)
    assignees = fields.List(AssigneeSchema)
