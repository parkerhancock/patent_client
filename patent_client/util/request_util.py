import math


def get_start_and_row_count(limit=None, offset=0, page_size=50):
    """Many API's have a start and row count parameter. This function
    converts an offset and limit into a iterator of start and row count
    tuples. If limit is None, then the iterator will be infinite.
    Otherwise, the iterator will be finite and the last row count may
    be less than the page size."""
    offset = offset or 0
    if not limit:
        page_no = 0
        while True:
            yield (page_no * page_size + offset, page_size)
            page_no += 1
    else:
        num_full_pages = math.floor(limit / page_size)
        last_page_size = limit % page_size
        for i in range(num_full_pages):
            yield (i * page_size + offset, page_size)
        if last_page_size:
            yield (num_full_pages * page_size + offset, last_page_size)
