import datetime
import mimetypes
from pathlib import Path
from functools import partial
from dataclasses import dataclass, field
import inflection
from dateutil.parser import parse as parse_dt

from patent_client import session
from .util import one_to_many, one_to_one

# Utility Functions
def apply_dict(func, dictionary):
    return {func(k): v if not isinstance(v, dict) else apply_dict(func, v)
            for (k, v) in dictionary.items()}

camelize = partial(inflection.camelize, uppercase_first_letter=False)
camelize_dict = partial(apply_dict, camelize)
underscore_dict = partial(apply_dict, inflection.underscore)

def parse_date(k, v):
    if "datetime" in k.lower():
        return parse_dt(v)
    elif "date" in k.lower():
        return parse_dt(v).date()
    else:
        return v

def json_decoder(dictionary):
    return {k: parse_date(k, v) for (k, v) in dictionary.items()}


@dataclass
class PtabManager():
    params: dict = field(default_factory=dict)
    
    def filter(self, *args, **kwargs):
        if args:
            kwargs[self.primary_key] = args[0]
        return self.__class__({**self.params, **kwargs})
    
    def get(self, *args, **kwargs):
        manager = self.filter(*args, **kwargs)
        if len(manager) != 1:
            raise ValueError(f"Expected 1 record, found {len(manager)} instead!")
        return next(iter(manager))

    def __iter__(self):
        offset = 0
        limit = 20
        while offset < len(self):
            params = {**self.params, **dict(offset=offset, limit=limit)}
            response = session.get(self.url, params=camelize_dict(params))
            for case_data in response.json(object_hook=json_decoder)["results"]:
                yield globals()[self.model_class](**underscore_dict(case_data))
            offset += limit
    
    def __len__(self):
        response = session.get(self.url, params=camelize_dict(self.params))
        print(self.params)
        return response.json()['metadata']['count']

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

class PtabTrialManager(PtabManager):
    url = "https://ptabdata.uspto.gov/ptab-api/trials"
    model_class = "PtabTrial"
    primary_key = "trial_number"
    query_fields = [
        "trial_number",
        "prosecution_status",
        "application_number",
        "patent_number",
        "filing_date",
        "filing_date_from",
        "filing_date_to",
        "accorded_filing_date",
        "accorded_filing_date_from",
        "accorded_filing_date_to",
        "institution_decision_date",
        "institution_decision_date_from",
        "institution_decision_date_to",
        "final_decision_date",
        "final_decision_date_from",
        "final_decision_date_to",
        "last_modified_datetime",
        "last_modified_datetime_from",
        "last_modified_datetime_to",
        "patent_owner_name"
    ]

class PtabDocumentManager(PtabManager):
    url = "https://ptabdata.uspto.gov/ptab-api/documents"
    model_class = "PtabDocument"
    primary_key = "trial_number"
    query_fields = [
        "id",
        "title",
        "filing_datetime",
        "filing_datetime_from",
        "filing_datetime_to",
        "filing_party",
        "document_number",
        "size_in_bytes",
        "trial_number",
        "media_type",
        "type",
        "last_modified_datetime",
        "last_modified_datetime_from",
        "last_modified_datetime_to",
    ]

@dataclass
class PtabTrial():
    """
    Ptab Trial
    ==========
    This object wraps the PTAB's public API (https://ptabdata.uspto.gov)

    ---------------------
    To Fetch a PTAB Trial
    ---------------------

    The main way to create a PtabTrial is by querying the PtabTrial manager at PtabTrial.objects

        PtabTrial.objects.filter(query) -> obtains multiple matching applications
        PtabTrial.objects.get(query) -> obtains a single matching application, errors if more than one is retreived

    The query can either be a single number, which is treated as a trial number, or a keyword argument:

        PtabTrial.objects.get('IPR2016-00831') -> Retreives a single trial
        PtabTrial.objects.filter(patent_number='6103599') -> retreives all PTAB trials involving US Patent Number 6103599

    A complete list of query fields is available at PtabTrial.objects.query_fields

    --------------
    Using the Data
    --------------
    A list of available attributes is provided at PtabTrial.__dataclass_fields__

    A PtabTrial also has access to the related documents, available at trial.documents

    ------------
    Related Data
    ------------
    A PtabTrial is also linked to other resources avaialble through patent_client, including:
        
        trial.us_application -> application which granted as the challenged patent

    """
    # Class Property
    objects = PtabTrialManager()
    # Dataclass Attributes
    trial_number: str
    application_number: str
    patent_number: str
    petitioner_party_name: str
    patent_owner_name: str
    inventor_name: str
    prosecution_status: str
    filing_date: datetime.date
    accorded_filing_date: datetime.date
    institution_decision_date: datetime.date
    last_modified_datetime: datetime.datetime
    links: dict

    @property
    def documents(self):
        return PtabDocument.objects.filter(self.trial_number)
    
    us_application = one_to_one(
        "patent_client.USApplication", appl_id="application_number"
    )

@dataclass
class PtabDocument():
    # Class Property
    objects = PtabDocumentManager()
    # Dataclass Attributes
    trial_number: str 
    size_in_bytes: int
    filing_party: str
    filing_datetime: datetime.datetime
    last_modified_datetime: datetime.datetime
    document_number: str
    title: str
    media_type: str
    id: int
    type: str
    links: dict

    @property
    def trial(self):
        return PtabTrial.objects.get(self.trial_number)
    
    def download(self, path="."):
        url = self.links[1]["href"]
        extension = mimetypes.guess_extension(self.media_type)
        base_name = self.title.replace("/", "_") + extension
        fpath = Path(path) / base_name
        response = session.get(url, stream=True)
        with open(fpath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
