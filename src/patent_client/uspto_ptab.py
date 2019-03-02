import json
import mimetypes
import os
import shutil
import importlib

import inflection
import requests
from patent_client import CACHE_BASE, TEST_BASE
from patent_client.util import Manager
from patent_client.util import Model
from patent_client.util import hash_dict
from patent_client.util import one_to_many
from patent_client.util import one_to_one

CACHE_DIR = CACHE_BASE / "ptab"
CACHE_DIR.mkdir(exist_ok=True)
TEST_DIR = TEST_BASE / "ptab"
TEST_DIR.mkdir(exist_ok=True)

session = requests.Session()


class PtabManager(Manager):
    page_size = 25

    def get_item(self, key):
        offset = int(key / self.page_size) * self.page_size
        position = key % self.page_size
        data = self.request(dict(offset=offset))
        results = data["results"]
        return self.get_obj_class()(results[position])

    def __len__(self):
        response = self.request()
        response_data = response
        count = response_data["metadata"]["count"]
        return count

    def request(self, params=dict()):
        params = {
            inflection.camelize(k, uppercase_first_letter=False): v
            for (k, v) in {**self.config['filter'], **dict(sort=self.config['order_by'])}.items()
        }
        if self.test_mode:
            fname = TEST_DIR / f"{self.__class__.__name__}-{hash_dict(params)}.json"
        else:
            fname = CACHE_DIR / f"{self.__class__.__name__}-{hash_dict(params)}.json"
        if not fname.exists():
            response = session.get(self.base_url, params=params)
            with open(fname, "w") as f:
                json.dump(response.json(), f, indent=True)
        return json.load(open(fname))

    @property
    def allowed_filters(self):
        return self.query_fields

    
    def get_obj_class(self):
        module, klass = self.obj_class.rsplit(".", 1)
        mod = importlib.import_module(module)
        return getattr(mod, klass)


class PtabTrialManager(PtabManager):
    base_url = "https://ptabdata.uspto.gov/ptab-api/trials"
    obj_class = "patent_client.uspto_ptab.PtabTrial"
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
    base_url = "https://ptabdata.uspto.gov/ptab-api/documents"
    obj_class = "patent_client.uspto_ptab.PtabDocument"
    primary_key = "id"
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


class PtabTrial(Model):
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
    A PtabTrial object has the following attributes:

        trial_number
        application_number
        patent_number
        petitioner_party_name
        patent_owner_name
        inventor_name
        prosecution_status
        filing_date
        accorded_filing_date
        institution_decision_date
        last_modified_datetime

    A PtabTrial also has access to the related documents, available at trial.documents

    ------------
    Related Data
    ------------
    A PtabTrial is also linked to other resources avaialble through patent_client, including:
        
        trial.us_application -> application which granted as the challenged patent

    """

    objects = PtabTrialManager()
    attrs = [
        "trial_number",
        "application_number",
        "patent_number",
        "petitioner_party_name",
        "patent_owner_name",
        "inventor_name",
        "prosecution_status",
        "filing_date",
        "accorded_filing_date",
        "institution_decision_date",
        "last_modified_datetime",
        "documents",
    ]

    us_application = one_to_one(
        "patent_client.USApplication", appl_id="application_number"
    )
    documents = one_to_many("patent_client.PtabDocument", trial_number="trial_number")

    def __repr__(self):
        return f"<PtabTrial(trial_number={self.trial_number})>"


class PtabDocument(Model):
    """
    Ptab Document
    ==========
    This object wraps documents obtained from PTAB's public API (https://ptabdata.uspto.gov)

    ---------------------
    To Fetch a PTAB Document
    ---------------------

    There are two ways to get a PTAB Document. First, you can fetch a PtabTrial, and then get a list of document
    objects:
    
        PtabTrial.objects.get('IPR2016-00831').documents -> a list of Ptab Document objects

    Or, you can search and filter for specific documents by various critera (e.g. date ranges, filing party, etc.)

        PtabDocumemt.objects.filter(trial_number='IPR2016-00831', filing_party='board') -> retreives all documents from Trial IPR2016-00831 filed by the Board

    A complete list of query fields is available at PtabDocument.objects.query_fields

    --------------
    Using the Data
    --------------
    A PtabTrial object has the following attributes:

        trial_number
        size_in_bytes
        filing_party
        filing_datetime
        last_modified_datetime
        document_number
        title
        media_type
        id
        type

    A PtabTrial also has access to the trial object it is associated with at document.trial

    A document can also be downloaded to your working directory by running document.download()

    """

    objects = PtabDocumentManager()
    attrs = [
        "trial_number",
        "size_in_bytes",
        "filing_party",
        "filing_datetime",
        "last_modified_datetime",
        "document_number",
        "title",
        "media_type",
        "id",
        "type",
    ]
    trial = one_to_one("patent_client.PtabTrial", trial_number="trial_number")

    def download(self, path="."):
        url = self.links[1]["href"]
        extension = mimetypes.guess_extension(self.media_type)
        base_name = self.title.replace("/", "_") + extension
        if self.objects.test_mode:
            cdir = os.path.join(TEST_DIR, self.trial_number)
        else:
            cdir = os.path.join(CACHE_DIR, self.trial_number)
        os.makedirs(cdir, exist_ok=True)
        cname = os.path.join(cdir, base_name)
        oname = os.path.join(path, base_name)
        if not os.path.exists(cname):
            response = session.get(url, stream=True)
            with open(cname, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        shutil.copy(cname, oname)

    def __repr__(self):
        return f"<PtabDocument(title={self.title})>"
