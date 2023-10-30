import math
import typing as tp

from hishel._controller import Controller
from hishel._controller import get_age
from hishel._utils import BaseClock
from httpcore import Request
from httpcore import Response


def get_start_and_row_count(limit=None, offset=0, page_size=50):
    """Many API's have a start and row count parameter. This function
    converts an offset and limit into a iterator of start and row count
    tuples. If limit is None, then the iterator will be infinite.
    Otherwise, the iterator will be finite and the last row count may
    be less than the page size."""
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


class SimpleController(Controller):
    def __init__(
        self,
        cacheable_methods: tp.Optional[tp.List[str]] = None,
        cacheable_status_codes: tp.Optional[tp.List[int]] = None,
        allow_heuristics: bool = False,
        clock: tp.Optional[BaseClock] = None,
        allow_stale: bool = False,
        always_revalidate: bool = False,
        max_age: tp.Optional[int] = None,
    ):
        super().__init__(
            cacheable_methods, cacheable_status_codes, allow_heuristics, clock, allow_stale, always_revalidate
        )
        self._max_age = max_age

    def construct_response_from_cache(
        self, request: Request, response: Response, original_request: Request
    ) -> Response | Request | None:
        # Use of responses with status codes 301 and 308 is always
        # legal as long as they don't adhere to any caching rules.
        if response.status in (301, 308):
            return response
        age = get_age(response, self._clock)
        is_fresh = age < self._max_age
        if is_fresh:
            return response
        else:
            # Otherwise, make a conditional request
            self._make_request_conditional(request=request, response=response)
            return request
