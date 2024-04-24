conversions = {
    "appl_id": "application_number",
    "inventor": "inventor_name",
}


def peds_to_ptab(query: dict) -> dict:
    for k, v in conversions.items():
        if k in query:
            query[v] = query.pop(k)
    return query
