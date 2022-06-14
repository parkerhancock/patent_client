from yankee import fields
from yankee import Schema

from patent_client.util.schema import ListField

from .model import Assignee
from .model import Assignment
from .model import Assignor
from .model import Property


# Utility Functions
def separate_dicts_by_prefix(prefix, data):
    keys = [k for k in data.keys() if k.startswith(prefix) and not k.endswith("size")]
    if not any(isinstance(data[k], (tuple, list)) for k in keys):
        filtered_data = [
            {k[len(prefix) + 1 :]: v for k, v in data.items() if k in keys},
        ]
        return filtered_data
    filtered_data = {
        k: v for k, v in data.items() if k in keys and isinstance(v, (tuple, list))
    }
    count = len(next(iter(filtered_data.values())))
    list_of_dicts = [
        {k[len(prefix) + 1 :]: v[i] for k, v in filtered_data.items()}
        for i in range(count)
    ]
    return list_of_dicts


def separate_dicts(keys, data):
    if not any(isinstance(data[k], (tuple, list)) for k in keys):
        filtered_data = [
            {k: v for k, v in data.items() if k in keys},
        ]
        return filtered_data
    filtered_data = {
        k: v for k, v in data.items() if k in keys and isinstance(v, (tuple, list))
    }
    count = len(next(iter(filtered_data.values())))
    list_of_dicts = [{k: v[i] for k, v in filtered_data.items()} for i in range(count)]
    return list_of_dicts


def combine_strings(prefix, data):
    filtered_data = {k: v for k, v in data.items() if k.startswith(prefix)}
    return "\n".join(filtered_data[k] for k in sorted(filtered_data.keys()))


# Schemas


class BaseSchema(Schema):
    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)

    pass


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
    name = fields.Str()
    ex_date = fields.Date()
    date_ack = fields.Date()


class AssigneeSchema(BaseSchema):
    __model__ = Assignee
    name = fields.Str()
    address = fields.Str()
    city = fields.Str()
    state = fields.Str()
    country_name = fields.Str()
    postcode = fields.Str()

    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data["address"] = combine_strings("corr_address", input_data)
        return input_data


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
    corr_address = fields.Str()
    assignment_record_has_images = fields.Bool(true_value="Y")
    page_count = fields.Int()
    transaction_date = fields.Date()
    last_update_date = fields.Date()
    recorded_date = fields.Date()
    properties = ListField(fields.Nested(PropertySchema))
    assignors = ListField(fields.Nested(AssignorSchema))
    assignees = ListField(fields.Nested(AssigneeSchema))

    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data["assignors"] = separate_dicts_by_prefix("pat_assignor", input_data)
        input_data["assignees"] = separate_dicts_by_prefix("pat_assignee", input_data)
        property_fields = [
            f.data_key or f.name for f in PropertySchema().fields.values()
        ]
        input_data["properties"] = separate_dicts(property_fields, input_data)
        input_data["corr_address"] = combine_strings("corr_address", input_data)
        return input_data
