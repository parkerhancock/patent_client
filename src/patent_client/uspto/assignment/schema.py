from marshmallow import EXCLUDE
from marshmallow import Schema
from marshmallow import ValidationError
from marshmallow import fields
from marshmallow import post_load
from marshmallow import pre_load

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


# Custom Fields


class YesNoField(fields.Field):
    """Converts to and from boolean values represented
    as a yes or no
    """

    def _deserialize(self, value, *args, **kwargs) -> bool:
        if value not in ("Y", "N"):
            raise ValidationError("YesNo must be a Y or N")
        return value == "Y"


# Schemas


class BaseSchema(Schema):
    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)

    pass


class PropertySchema(BaseSchema):
    __model__ = Property
    invention_title = fields.Str(allow_none=True)
    inventors = fields.Str(allow_none=True)
    # Numbers
    appl_id = fields.Str(allow_none=True, data_key="appl_num")
    pct_num = fields.Str(allow_none=True)
    intl_reg_num = fields.Str(allow_none=True)
    publ_num = fields.Str(allow_none=True)
    pat_num = fields.Str(allow_none=True)
    # Dates
    filing_date = fields.Date(allow_none=True)
    intl_publ_date = fields.Date(allow_none=True)
    issue_date = fields.Date(allow_none=True)
    publ_date = fields.Date(allow_none=True)


class AssignorSchema(BaseSchema):
    __model__ = Assignor
    name = fields.Str()
    ex_date = fields.Raw()
    date_ack = fields.Raw()

    class Meta:
        unknown = EXCLUDE


class AssigneeSchema(BaseSchema):
    __model__ = Assignee
    name = fields.Str()
    address = fields.Str()
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country_name = fields.Str(allow_none=True)
    postcode = fields.Str(allow_none=True)

    @pre_load
    def pre_load(self, input_data, **kwargs):
        input_data["address"] = combine_strings("corr_address", input_data)
        return input_data

    class Meta:
        unknown = EXCLUDE


class AssignmentSchema(BaseSchema):
    __model__ = Assignment
    assignment_record_has_images = YesNoField()
    page_count = fields.Int()
    transaction_date = fields.Raw(allow_none=True)
    last_update_date = fields.Raw(required=True)
    recorded_date = fields.Raw(required=True)
    assignment_record_has_images = fields.Boolean(required=True)
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
        input_data["conveyance_text"] = (
            input_data["conveyance_text"]
            .replace("(SEE DOCUMENT FOR DETAILS).", "")
            .strip()
        )
        return input_data

    class Meta:
        unknown = EXCLUDE
        additional = (
            "id",
            "conveyance_text",
            "date_produced",
            "assignment_record_has_images",
            "corr_name",
            "corr_address",
            "assignor",
            "assignee",
        )
