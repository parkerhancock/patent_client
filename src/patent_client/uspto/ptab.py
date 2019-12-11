import math
import inflection

from patent_client.util.manager import Manager
from patent_client.util.model import Model
from patent_client.util.related import one_to_one, one_to_many
from patent_client import session


proceeding_filters = [
    "accordedFilingDate",
    "appellantApplicationNumberText",
    "appellantCounselName",
    "appellantGrantDate",
    "appellantGroupArtUnitNumber",
    "appellantInventorName",
    "appellantPartyName",
    "appellantPatentNumber",
    "appellantPatentOwnerName",
    "appellantPublicationDate",
    "appellantPublicationNumber",
    "appellantTechnologyCenterNumber",
    "decisionDate",
    "docketNoticeMailDate",
    "documents",
    "institutionDecisionDate",
    "lastModifiedDate",
    "lastModifiedUserId",
    "petitionerApplicationNumberText",
    "petitionerCounselName",
    "petitionerGrantDate",
    "petitionerGroupArtUnitNumber",
    "petitionerInventorName",
    "petitionerPartyName",
    "petitionerPatentNumber",
    "petitionerPatentOwnerName",
    "petitionerTechnologyCetnerNumber",
    "proceedingFilingDate",
    "proceedingLastModifiedDate",
    "proceedingNumber",
    "proceedingStatusCategory",
    "proceedingTypeCategory",
    "respondentApplicationNumberText",
    "respondentCounselName",
    "respondentGrantDate",
    "respondentGroupArtUnitNumber",
    "respondentInventorName",
    "respondentPartyName",
    "respondentPatentNumber",
    "respondentPatentOwnerName",
    "respondentTechnologyCenterNumber",
    "subproceedingTypeCategory",
    "thirdPartyName",
]

document_filters = [
    "appellantApplicationNumberText",
    "appellantCounselName",
    "appellantGrantDate",
    "appellantGroupArtUnitNumber",
    "appellantInventorName",
    "appellantPartyName",
    "appellantPatentNumber",
    "appellantPatentOwnerName",
    "appellantPublicationDate",
    "appellantPublicationNumber",
    "appellantTechnologyCenterNumber",
    "documentCategory",
    "documentFilingDate",
    "documentIdentifier",
    "documentName",
    "documentNumber",
    "documentSize",
    "documentTitleText",
    "documentTypeName",
    "filingPartyCategory",
    "lastModifiedDate",
    "lastModifiedUserId",
    "mediaTypeCategory",
    "petitionerApplicationNumberText",
    "petitionerCounselName",
    "petitionerGrantDate",
    "petitionerGroupArtUnitNumber",
    "petitionerInventorName",
    "petitionerPartyName",
    "petitionerPatentNumber",
    "petitionerPatentOwnerName",
    "petitionerTechnologyCenterNumber",
    "proceedingNumber",
    "proceedingTypeCategory",
    "respondentApplicationNumberText",
    "respondentCounselName",
    "respondentGrantDate",
    "respondentGroupArtUnitNumber",
    "respondentInventorName",
    "respondentPartyName",
    "respondentPatentNumber",
    "respondentPatentOwnerName",
    "respondentTechnologyCenterNumber",
    "subproceedingTypeCategory",
    "thirdPartyName",
]


class PtabManager(Manager):
    page_size = 25
    instance_class = None

    def __iter__(self):
        total = self._len()
        offset = self.config["offset"]
        limit = self.config["limit"]
        if limit:
            max_item = total if total - offset < limit else offset + limit
        else:
            max_item = total
        item_range = (offset, max_item)
        page_range = (
            int(offset / self.page_size),
            math.ceil(max_item / self.page_size),
        )
        counter = page_range[0] * self.page_size

        for p in range(*page_range):
            for item in self.get_page(p):
                if item_range[0] <= counter < item_range[1]:
                    yield globals()[self.instance_class](item)
                counter += 1
                if counter >= max_item:
                    return StopIteration

    def get_page(self, page_no):
        query = self.query()
        query["recordStartNumber"] = page_no * self.page_size
        response = session.get(self.query_url, params=query)
        return response.json()["results"]

    def __len__(self):
        length = self._len() - self.config["offset"]
        if self.config["limit"]:
            return length if length < self.config["limit"] else self.config["limit"]
        else:
            return length

    def _len(self):
        response = session.get(self.query_url, params=self.query())
        return response.json()["recordTotalQuantity"]

    def query(self):
        query = dict()
        for k, v in self.config["filter"].items():
            query[inflection.camelize(k, uppercase_first_letter=False)] = " ".join(v)
        query["recordTotalQuantity"] = self.page_size
        query["sortOrderCategory"] = " ".join(
            inflection.camelize(o, uppercase_first_letter=False)
            for o in self.config["order_by"]
        )
        return query


class PtabProceedingManager(PtabManager):
    query_url = "https://developer.uspto.gov/ptab-api/proceedings"
    primary_key = "proceeding_number"
    instance_class = "PtabProceeding"


class PtabProceeding(Model):
    objects = PtabProceedingManager()
    attrs = [
        inflection.underscore(i)
        for i in (
            "proceedingNumber proceedingStatusCategory proceedingTypeCategory "
            + "subproceedingTypeCategory respondentApplicationNumberText respondentPatentNumber "
            + "petitionerPartyName respondentPartyName petitionerCounselName respondentCounselName "
            + "respondentPatentOwnerName respondentInventorName respondentGrantDate "
            + "respondentTechnologyCenterNumber proceedingFilingDate accordedFilingDate "
            + "institutionDecisionDate decisionDate"
        ).split()
    ]
    documents = one_to_many(
        "patent_client.PtabDocument", proceeding_number="proceeding_number"
    )
    decisions = one_to_many(
        "patent_client.PtabDecision", proceeding_number="proceeding_number"
    )


class PtabDocumentManager(PtabManager):
    query_url = "https://developer.uspto.gov/ptab-api/documents"
    primary_key = "document_identifier"
    instance_class = "PtabDocument"


class PtabDocument(Model):
    objects = PtabDocumentManager()
    attrs = [
        inflection.underscore(i)
        for i in [
            "documentIdentifier",
            "documentCategory",
            "documentTypeName",
            "documentNumber",
            "documentName",
            "documentFilingDate",
            "documentTitleText",
            "proceedingNumber",
            "proceedingTypeCategory",
        ]
    ]
    proceeding = one_to_one(
        "patent_client.PtabProceeding", proceeding_number="proceeding_number"
    )

    @property
    def download_url(self):
        return f"{self.objects.query_url}/{self.document_identifier}/download"


class PtabDecisionManager(PtabManager):
    query_url = "https://developer.uspto.gov/ptab-api/decisions"
    primary_key = "identifier"
    instance_class = "PtabDecision"


class PtabDecision(Model):
    objects = PtabDecisionManager()
    proceeding = one_to_one(
        "patent_client.PtabProceeding", proceeding_number="proceeding_number"
    )
    attrs = [
        inflection.underscore(i)
        for i in [
            "appellantApplicationNumberText",
            "appellantCounselName",
            "appellantGrantDate",
            "appellantGroupArtUnitNumber",
            "appellantInventorName",
            "appellantPartyName",
            "appellantPatentNumber",
            "appellantPatentOwnerName",
            "appellantPublicationDate",
            "appellantPublicationNumber",
            "appellantTechnologyCenterNumber",
            "boardRulings",
            "decisionDate",
            "decisionTypeCategory",
            "documentIdentifier",
            "documentName",
            "identifier",
            "issueType",
            "lastModifiedDate",
            "lastModifiedUserId",
            "objectUuId",
            "ocrSearchText",
            "petitionerApplicationNumberText",
            "petitionerCounselName",
            "petitionerGrantDate",
            "petitionerGroupArtUnitNumber",
            "petitionerInventorName",
            "petitionerPartyName",
            "petitionerPatentNumber",
            "petitionerPatentOwnerName",
            "petitionerTechnologyCenterNumber",
            "proceedingNumber",
            "proceedingTypeCategory",
            "respondentApplicationNumberText",
            "respondentCounselName",
            "respondentGrantDate",
            "respondentGroupArtUnitNumber",
            "respondentInventorName",
            "respondentPartyName",
            "respondentPatentNumber",
            "respondentPatentOwnerName",
            "respondentTechnologyCenterNumber",
            "subdecisionTypeCategory",
            "subproceedingTypeCategory",
            "thirdPartyName",
        ]
    ]
