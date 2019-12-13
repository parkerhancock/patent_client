from dataclasses import dataclass
from typing import List, Optional
import datetime
from collections import OrderedDict

from patent_client import session
from patent_client.util import one_to_one, one_to_many, Model

@dataclass(frozen=True)
class Property(Model):
    invention_title: str
    inventors: str
    # Numbers
    appl_id: str
    pct_num: str
    intl_reg_num: str
    publ_num: str
    pat_num: str
    # Dates
    filing_date: datetime.date
    intl_publ_date: datetime.date
    issue_date: datetime.date
    publ_date: datetime.date

    us_application = one_to_one("patent_client.USApplication", appl_id="appl_id")

@dataclass
class Person(Model):
    name: str
    address: str
    city: str
    state: str
    post_code: str
    country_name: str

@dataclass
class Assignor(Model):
    name: str
    ex_date: datetime.date
    date_ack: datetime.datetime

@dataclass
class Assignee(Model):
    name: str
    address: str
    city: str
    state: str
    country_name: str
    postcode: str

@dataclass
class Assignment(Model):
    """
    Assignments
    ===========
    This object wraps the USPTO Assignment API (https://assignments.uspto.gov)

    ----------------------
    To Fetch an Assignment
    ----------------------
    The main way to create an Assignment is by querying the Assignment manager at Assignment.objects

    Assignment.objects.filter(query) -> obtains multiple matching applications
    Assignment.objects.get(query) -> obtains a single matching application, errors if more than one is retreived

    The query can either be a single number, which is treated as a reel/frame number (e.g. "123-1321"), or a keyword.
    Available query types are: 
        patent_number, 
        appl_id (application #), 
        app_early_pub_number (publication #), 
        assignee,
        assignor,
        pct_number (PCT application #),
        correspondent,
        reel_frame

    --------------
    Using the Data
    --------------
    An Assignment object has the following properties:
        id (reel/frame #)
        attorney_dock_num
        conveyance_text
        last_update_date
        page_count
        recorded_date
        correspondent
        assignees
        assignors
        properties

    Additionally, the original assignment document can be downloaded to the working directory by calling:

    assignment.download()
    
    ------------
    Related Data
    ------------
    An Assignment is also linked to other resources available through patent_client. 
    A list of all assigned applications is available at:

    assignment.us_applications

    Additionally, each property entry in properties links to the corresponding application at:

    assignment.properties[0].us_application


    """
    id: str
    conveyance_text: str
    last_update_date: str
    page_count: int
    recorded_date: datetime.date
    corr_name: str
    corr_address: str
    assignors: List[Assignor]
    assignees: List[Assignee]
    properties: List[Property]
    assignment_record_has_images: bool
    transaction_date: Optional[datetime.date] = None
    date_produced: Optional[datetime.date] = None

    us_applications = one_to_many("patent_client.USApplication", appl_id="appl_num")

    @property
    def image_url(self):
        reel, frame = self.id.split('-')
        reel = reel.rjust(6, '0')
        frame = frame.rjust(4, '0')
        return f'http://legacy-assignments.uspto.gov/assignments/assignment-pat-{reel}-{frame}.pdf'

    def download(self):
        response = session.get(self.image_url, stream=True)
        with open(f"{self.id}.pdf", "wb") as f:
            f.write(response.raw.read())



