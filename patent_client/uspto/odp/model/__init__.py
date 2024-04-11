from pydantic import ConfigDict
from patent_client.util.pydantic_util import BaseModel
from pydantic.alias_generators import to_camel

class BaseODPModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    
from .api_models import *
from .data_models import *

