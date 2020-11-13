SEARCH_PARAMS = {
    "Sect1": "PTO2",
    "Sect2": "HITOFF",
    "p": "1",
    "u": "/netahtml/PTO/search-adv.html",
    "r": "0",
    "f": "S",
    "l": "50",
    "d": "PG01",
    "Query": "query",
}

SEARCH_FIELDS = {
    "document_number": "DN",
    "publication_date": "PD",
    "title": "TTL",
    "abstract": "ABST",
    "claims": "ACLM",
    "specification": "SPEC",
    "current_us_classification": "CCL",
    "current_cpc_classification": "CPC",
    "current_cpc_classification_class": "CPCL",
    "international_classification": "ICL",
    "application_serial_number": "APN",
    "application_date": "APD",
    "application_type": "APT",
    "government_interest": "GOVT",
    "patent_family_id": "FMID",
    "parent_case_information": "PARN",
    "related_us_app._data": "RLAP",
    "related_application_filing_date": "RLFD",
    "foreign_priority": "PRIR",
    "priority_filing_date": "PRAD",
    "pct_information": "PCT",
    "pct_filing_date": "PTAD",
    "pct_national_stage_filing_date": "PT3D",
    "prior_published_document_date": "PPPD",
    "inventor_name": "IN",
    "inventor_city": "IC",
    "inventor_state": "IS",
    "inventor_country": "ICN",
    "applicant_name": "AANM",
    "applicant_city": "AACI",
    "applicant_state": "AAST",
    "applicant_country": "AACO",
    "applicant_type": "AAAT",
    "assignee_name": "AN",
    "assignee_city": "AC",
    "assignee_state": "AS",
    "assignee_country": "ACN",
}

SEARCH_URL = "http://appft.uspto.gov/netacgi/nph-Parser"

PUBLICATION_URL = (
    "http://appft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&"
    "Sect2=HITOFF&d=PG01&p=1&u=%2Fnetahtml%2FPTO%2Fsrchnum.html&r=1&f=G&l=50&"
    "s1=%22{publication_number}%22.PGNR.&OS=DN/{publication_number}&RS=DN/{publication_number}"
)