from pathlib import Path

import pytest

from .api import AssignmentApi


@pytest.mark.asyncio
async def test_alookup():
    query = "test_query"
    filter = "OwnerName"
    sort = "ExecutionDate+desc"
    rows = 5
    start = 0
    assignments = await AssignmentApi.lookup(
        query=query, filter=filter, rows=rows, start=start, sort=sort
    )
    assert assignments is not None, "Expected to get a response"
    assert (
        len(assignments) <= rows
    ), "Expected number of assignments to be less than or equal to requested rows"


@pytest.mark.asyncio
async def test_download_pdf(tmp_path: Path):
    reel = "12345"
    frame = "67890"
    path = await AssignmentApi.download_pdf(reel=reel, frame=frame, path=tmp_path)
    assert path.exists(), "Expected the PDF file to exist"
    assert path.is_file(), "Expected the path to be a file"
    assert path.suffix == ".pdf", "Expected the file to be a PDF"
