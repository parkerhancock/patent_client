from patent_client import session

class UsptoException(Exception):
    pass

def force_list(obj):
    if not isinstance(obj, list):
        return [obj,]
    return obj

class PublicSearchApi():

    @classmethod
    def run_query(cls,
                query, 
                start=0, 
                limit=500, 
                sort="date_publ desc", 
                default_operator="OR",
                sources=["US-PGPUB", "USPAT", "USOCR"],
                expand_plurals=True,
                british_equivalents=True,
                ):
        url = "https://ppubs.uspto.gov/dirsearch-public/searches/searchWithBeFamily"
        data = {
            "start":start,
            "pageCount":limit,
            "sort": sort,
            "docFamilyFiltering": "familyIdFiltering",
            "searchType":1,
            "familyIdEnglishOnly":True,
            "familyIdFirstPreferred":"US-PGPUB",
            "familyIdSecondPreferred":"USPAT",
            "familyIdThirdPreferred":"FPRS",
            "showDocPerFamilyPref":"showEnglish",
            "queryId":0,
            "tagDocSearch":False,
            "query":{
                "caseId":1,
                "hl_snippets":"2",
                "op":default_operator,
                "q": query,
                "queryName":query,
                "highlights":"0",
                "qt":"brs",
                "spellCheck":False,
                "viewName":"tile",
                "plurals":expand_plurals,
                "britishEquivalents":british_equivalents,
                "databaseFilters":[],
                "searchType":1,
                "ignorePersist":True,
                "userEnteredQuery":query
            }
        }
        for s in force_list(sources):
            data['query']['databaseFilters'].append(
                {"databaseName": s, "countryCodes":[]}
            )
        query_response = session.post(url, json=data)
        result = query_response.json()
        if result['error'] is not None:
            raise UsptoException(f"Error #{result['error']['errorCode']}\n{result['error']['errorMessage']}")
        return result

    @classmethod
    def get_document(cls, guid):
        url = f"https://ppubs.uspto.gov/dirsearch-public/patents/{guid}/highlight"
        params = {
            "queryId": 1,
            "source": pat['type'],
            "includeSections": True,
            "uniqueId": None,
        }
        response = session.get(url, params=params)
        return response.json()