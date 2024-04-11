from pydantic import Field, model_validator
from typing import Optional, List, Any
from enum import Enum
import datetime

from patent_client.util.pydantic_util import BaseModel

## Request Models

class Filter(BaseModel):
    name: str
    value: List[str]
    
class Range(BaseModel):
    field: str = Field(examples=["grantDate"])
    valueFrom: str = Field(examples=["2020-01-01"])
    valueTo: str = Field(examples=["2020-12-31"])
    
    @model_validator(mode="before")
    @classmethod
    def add_default_dates(cls, data: Any) -> Any:
        if data.get("valueFrom") is None:
            data["valueFrom"] = "1776-07-04"
        if data.get("valueTo") is None:
            data["valueTo"] = datetime.date.today().isoformat()
        return data
        

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
    Asc = "Asc"
    Desc = "Desc"

class Sort(BaseModel):
    field: str = Field(examples=["grantDate"])
    order: SortOrder = Field(examples=[SortOrder.desc])
    
class Pagination(BaseModel):
    offset: int = Field(examples=[0], default=0, ge=0)
    limit: int = Field(examples=[25], default=25, ge=1)

class SearchRequest(BaseModel):
    q: str = Field(default="")
    filters: Optional[List[Filter]] = Field(default=None)
    rangeFilters: Optional[List[Range]] = Field(default=None)
    sort: Optional[List[Sort]] = Field(default=None)
    fields: Optional[List[str]] = Field(default=None)
    pagination: Optional[Pagination] = Field(default=None)
    facets: Optional[List[str]] = Field(default=None)
    
class SearchGetRequest(BaseModel):
    q: str = Field(default="")
    sort: str = Field(default="filingDate")
    fields: str = Field(default="")
    offset: int = Field(default=0)
    limit: int = Field(default=25)

