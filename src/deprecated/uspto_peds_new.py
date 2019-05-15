from . import session
from decimal import Decimal

@dataclass
class Manager():
    params: dict = field(default_factory=dict)
    submission_type = "form"
    offset = "offset"
    limit = "limit"
    method = "get"
    page_size = 20

    def filter(self, *args, **kwargs):
        if args:
            kwargs[self.primary_key] = args[0]
        return self.__class__({**self.params, **kwargs})

    def get_params(self):
        return self.params
    
    def get(self, *args, **kwargs):
        manager = self.filter(*args, **kwargs)
        if len(manager) != 1:
            raise ValueError(f"Expected 1 record, found {len(manager)} instead!")
        return next(iter(manager))

    def __iter__(self):
        offset = 0
        limit = self.page_size
        while offset < len(self):
            response = self.request(offset, limit)
            for case_data in response.json(object_hook=json_decoder)["results"]:
                yield globals()[self.model_class](**underscore_dict(case_data))
            offset += limit
    
    def request(self, offset, limit):
        params = {**self.get_params(), **{self.offset: offset, self.limit:limit}}
        if self.submission_type == "json":
            return session.request(self.method, self.url, json=camelize_dict(params))
        else:
            return session.request(self.method, self.url, params=camelize_dict(params))

    # utility functions
    def count(self):
        return len(self)

    def order_by(self, field):
        return self.filter(sort=field)

    def first(self):
        return next(iter(self))

    def values(self, *args):
        for obj in iter(self):
            yield {k: getattr(obj, k, None) for k in args}
    
    def values_list(self, *args, flat=False):
        for dictionary in self.values(*args):
            if flat:
                yield tuple(dictionary.values())[0]
            else:
                yield tuple(dictionary.values())

class USApplicationManager(Manager):
    url = "https://ped.uspto.gov/api/queries"
    model_class = "USApplication"
    primary_key = "appl_id"
    submission_type = "json"
    offset = "start"
    limit = "rows"
    method = "post"

    def __len__(self):
        return self.request(0, 1).json()["queryResults"]["searchResponse"]["response"]["numFound"]

    def get_params(self):
        sort_query = ""
        for s in self.params['sort']:
            if s[0] == "-":
                sort_query += f"{inflection.camelize(s[1:], uppercase_first_letter=False)} desc "
            else:
                sort_query += (
                    f"{inflection.camelize(s, uppercase_first_letter=False)} asc"
                )

        query = ""
        mm_active = True
        for k, v in self.params.items():
            if k == "sort":
                continue
            field = inflection.camelize(k, uppercase_first_letter=False)
            if not v:
                continue
            elif type(v) in (list, tuple):
                body = f" OR ".join(v)
                mm_active = False
            else:
                body = v
            query += f"{field}:({body}) "

        mm = "100%" if "appEarlyPubNumber" not in query else "90%"

        query = {
            "qf": QUERY_FIELDS,
            "fl": "*",
            "searchText": query.strip(),
            "sort": sort_query.strip(),
            "facet": "false",
            "mm": mm,
        }
        if not mm_active:
            del query['mm']
        return query

    
@dataclass
class USApplication():
    # Basic Bibliographic Data
    appl_id: str
    app_attr_dock_number: str = None
    app_cls_sub_cls: str = None
    app_confr_number: str = None
    app_control_number: str = None
    app_entity_status: str = None
    app_filing_date: datetime.date = None
    app_location: str = None
    app_status: str = None
    app_status_date: datetime.date = None
    app_type: str = None
    first_inventor_file: str = None
    first_named_applicant: str = None
    inventor_name: str = None
    patent_title: str = None

    # Expiry Information
    pta_pte_ind: str = None
    a_delay: int = 0
    b_delay: int = 0 
    c_delay: int = 0 
    pto_delay: int = 0 
    applicant_delay: int = 0
    overlap_delay: int = 0
    pto_adjustments: int = 0

    # Publication Data
    app_early_pub_number: str = None
    app_early_pub_date: date.datetime = None
    patent_number: str = None
    patent_issue_date: date.datetime = None
    app_intl_pub_number: str = None
    app_intl_pub_date: date.datetime = None
    wipo_early_pub_number: str = None
    wipo_early_pub_date: date.datetime = None

    # Compound Data
    correspondent: Correspondent = None
    inventors: list = None
    applicants: list = None
    transactions: List[Transaction] = None
    child_continuity: List[Relationship] = None
    parent_continuity: List[Relationship] list = None
    attrny_addr: List[Attorney] = None
    pta_pte_tran_history: list = None
    foreign_priority: ForeignPriority = None

    # Update Metadata
    last_mod_ts: datetime.datetime = None
    last_insert_time: datetime.datetime = None

    def __init__(self, **data):
        for field in self.fields:
        correspondent_data = {k.replace('corr_', ''): v for (k, v) in data.items()}
        self.correspondent = Correspondent(correspondent_data)



@dataclass
class Relationship:
    parent_appl_id: str
    child_appl_id: str
    parent_app_filing_date: str
    relation: str
    
@dataclass
class Transaction:
    date: datetime.date
    code: str 
    description: str

@dataclass
class Correspondent:
    name: str
    cust_no: str
    street_address: str
    city: str
    geo_region_code: str
    postal_code: str

    def __init__(self, **data):
        self.name = line_combine(data, 'name_')
        self.street_address = line_combine(data, "street_")
        for k in ['cust_no', 'city', 'geo_region_code', 'postal_code']:
            setattr(self, k, data[k])

@dataclass
class Attorney:
    registration_no: str
    full_name: str
    phone_num: str
    reg_status: str 

@dataclass
class ForeignPriority:
    country_name: str
    application_number_text: str
    filing_date: datetime.date

@dataclass
class PtaPteHistory:
    number: Decimal
    date: date.datetime 
    description: str
    pto_days: Decimal

def line_combine(data, prefix):
    sort_dict = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
    }
    return "\n".join(
        sorted(
            filter(
                lambda k, v: prefix in k, 
                data.items()
                ),
            key=lambda k, v: sort_dict[k.split('_')[-1]]
        )
    )

