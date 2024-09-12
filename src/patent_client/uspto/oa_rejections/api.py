# https://developer.uspto.gov/api-catalog/uspto-office-action-rejection-api
from .schema import OfficeActionCitationPageSchema
from .schema import OfficeActionFulltextPageSchema
from .schema import OfficeActionRejectionPageSchema
from .session import session


class OfficeActionApi:
    @classmethod
    async def get_rejection_fields(cls):
        response = await session.get("https://developer.uspto.gov/ds-api/oa_rejections/v2/fields")
        return response.json()

    @classmethod
    async def get_rejection_records(cls, criteria=None, start=0, rows=100):
        if not criteria:
            criteria = "*:*"
        response = await session.post(
            "https://developer.uspto.gov/ds-api/oa_rejections/v2/records",
            data={"criteria": criteria, "start": start, "rows": rows},
        )
        return OfficeActionRejectionPageSchema().load(response.json())

    @classmethod
    async def get_fulltext_fields(cls):
        response = await session.get("https://developer.uspto.gov/ds-api/oa_actions/v1/fields")
        return response.json()

    @classmethod
    async def get_fulltext_records(cls, criteria=None, start=0, rows=100):
        if not criteria:
            criteria = "*:*"
        response = await session.post(
            "https://developer.uspto.gov/ds-api/oa_actions/v1/records",
            data={"criteria": criteria, "start": start, "rows": rows},
        )
        return OfficeActionFulltextPageSchema().load(response.json())

    @classmethod
    async def get_citation_fields(cls):
        response = await session.get("https://developer.uspto.gov/ds-api/oa_citations/v2/fields")
        return response.json()

    @classmethod
    async def get_citation_records(cls, criteria=None, start=0, rows=100):
        if not criteria:
            criteria = "*:*"
        response = await session.post(
            "https://developer.uspto.gov/ds-api/oa_citations/v2/records",
            data={"criteria": criteria, "start": start, "rows": rows},
        )
        return OfficeActionCitationPageSchema().load(response.json())
