from yankee.base.schema import ListCollection

from .model import Assignment
from .schema import AssignmentPageSchema
from .session import session


allowed_filters = [
    "PCTNumber",
    "OwnerName",
    "CorrespondentName",
    "PriorOwnerName",
    "ApplicationNumber",
    "PatentNumber",
    "PublicationNumber",
    "IntlRegistrationNumber",
    "ReelFrame",
]

allowed_sorts = ["ExecutionDate+desc", "ExecutionDate+asc"]


def validate_input(input, input_name, allowed_values):
    if input not in allowed_values:
        raise ValueError(f"{input_name} must be one of {allowed_values}")


class AssignmentApi:
    @classmethod
    async def alookup(
        self, query: str, filter: str, rows=8, start=0, sort="ExecutionDate+desc"
    ) -> ListCollection[Assignment]:
        # Because of their limited utility, we omit fields, highlight, and facet
        url = "https://assignment-api.uspto.gov/patent/lookup"
        validate_input(filter, "filter", allowed_filters)
        validate_input(sort, "sort", allowed_sorts)
        response = await session.get(
            url,
            params={
                "filter": filter,
                "query": query,
                "rows": rows,
                "start": start,
                "sort": sort,
                "facet": "false",
            },
            headers={"Accept": "application/xml"},
        )
        response.raise_for_status()
        return AssignmentPageSchema().load(response.text)
