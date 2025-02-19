import typing as tp
from copy import deepcopy

from .api import ODPApi
from .model import (
    BdssResponseBag,
    Filter,
    Order,
    PatentSearchRequest,
    Range,
    Sort,
    Pagination,
    PatentFileWrapperDataBagItem
)


class BulkDataSearch:
    """
    A high-level API for searching USPTO ODP Bulk Data products.
    
    This class provides a search interface tailored for bulk data products with support
    for text search, filtering by product attributes, and options for file inclusion.
    """

    def __init__(self, manager):
        """
        Initialize the bulk data search interface.
        
        Args:
            manager: The manager instance this search interface is attached to
        """
        self.manager = manager
        self._api = ODPApi()
        self._search_params = {
            "offset": 0,
            "limit": 10,
            "facets": False,
            "include_files": True,
            "latest": False,
        }

    def _clone(self) -> "BulkDataSearch":
        """Create a copy of the current search interface."""
        new = BulkDataSearch(self.manager)
        new._api = self._api
        new._search_params = deepcopy(self._search_params)
        return new

    def _process_list_param(self, value: tp.Union[str, tp.List[str]]) -> str:
        """Convert a string or list parameter to a comma-separated string."""
        if isinstance(value, list):
            return ",".join(value)
        return value

    def query(
        self,
        q: tp.Optional[str] = None,
        *,
        product_title: tp.Optional[str] = None,
        product_description: tp.Optional[str] = None,
        product_short_name: tp.Optional[str] = None,
        labels: tp.Optional[tp.Union[str, tp.List[str]]] = None,
        categories: tp.Optional[tp.Union[str, tp.List[str]]] = None,
        datasets: tp.Optional[tp.Union[str, tp.List[str]]] = None,
        file_types: tp.Optional[tp.Union[str, tp.List[str]]] = None,
    ) -> "BulkDataSearch":
        """
        Add search parameters to the query.

        Args:
            q: General text search across all fields
            product_title: Filter by product title
            product_description: Filter by product description
            product_short_name: Filter by product short name
            labels: Filter by product labels (e.g. "PATENT" or ["PATENT", "TRADEMARK"])
            categories: Filter by product categories
            datasets: Filter by dataset names
            file_types: Filter by file types

        Returns:
            A new BulkDataSearch instance with the search parameters applied.
        """
        s = self._clone()
        if q is not None:
            s._search_params["q"] = q
        if product_title is not None:
            s._search_params["product_title"] = product_title
        if product_description is not None:
            s._search_params["product_description"] = product_description
        if product_short_name is not None:
            s._search_params["product_short_name"] = product_short_name
        if labels is not None:
            s._search_params["labels"] = self._process_list_param(labels)
        if categories is not None:
            s._search_params["categories"] = self._process_list_param(categories)
        if datasets is not None:
            s._search_params["datasets"] = self._process_list_param(datasets)
        if file_types is not None:
            s._search_params["file_types"] = self._process_list_param(file_types)
        return s

    def options(
        self,
        *,
        include_files: tp.Optional[bool] = None,
        latest: tp.Optional[bool] = None,
        facets: tp.Optional[bool] = None,
    ) -> "BulkDataSearch":
        """
        Set search options.

        Args:
            include_files: Whether to include file details in the response
            latest: Whether to only return the latest version of files
            facets: Whether to include facets in the response

        Returns:
            A new BulkDataSearch instance with the options applied.
        """
        s = self._clone()
        if include_files is not None:
            s._search_params["include_files"] = include_files
        if latest is not None:
            s._search_params["latest"] = latest
        if facets is not None:
            s._search_params["facets"] = facets
        return s

    def paginate(self, offset: int = 0, limit: int = 10) -> "BulkDataSearch":
        """
        Set pagination parameters.

        Args:
            offset: Number of results to skip
            limit: Maximum number of results to return

        Returns:
            A new BulkDataSearch instance with the pagination applied.
        """
        s = self._clone()
        s._search_params["offset"] = offset
        s._search_params["limit"] = limit
        return s

    async def execute(self) -> BdssResponseBag:
        """
        Execute the search and return the results.

        Returns:
            The search response containing bulk data products matching the search criteria.
        """
        return await self._api.bulk_data.get_search(**self._search_params)


class Search:
    """
    A high-level API for searching USPTO ODP data using an Elasticsearch DSL-like interface.
    
    This class is designed to be used as a search attribute on model managers that support search.
    
    """

    # Maximum results per page allowed by the API
    MAX_PAGE_SIZE = 25

    def __init__(self, manager):
        """
        Initialize the search interface.
        
        Args:
            manager: The manager instance this search interface is attached to
        """
        self.manager = manager
        self._api = ODPApi()
        self._search_request = PatentSearchRequest()
        self._response = None
        self._total_count = None
        self._has_explicit_pagination = False

    def _clone(self) -> "Search":
        """Create a copy of the current search interface."""
        new = Search(self.manager)
        new._api = self._api
        new._search_request = deepcopy(self._search_request)
        new._has_explicit_pagination = self._has_explicit_pagination
        return new

    def query(self, query_string: str) -> "Search":
        """
        Add a query string to the search.

        Args:
            query_string: The query string in Elasticsearch query string syntax.
                For example: "applicationMetaData.applicationTypeLabelName:Utility"

        Returns:
            A new Search instance with the query applied.
        """
        s = self._clone()
        s._search_request.q = query_string
        return s

    def filter(self, name: str, value: tp.Union[str, tp.List[str]]) -> "Search":
        """
        Add a filter to the search.

        Args:
            name: The field name to filter on
            value: The value or list of values to filter for

        Returns:
            A new Search instance with the filter applied.
        """
        s = self._clone()
        if not s._search_request.filters:
            s._search_request.filters = []
        
        # Convert single value to list
        if isinstance(value, str):
            value = [value]
            
        s._search_request.filters.append(Filter(name=name, value=value))
        return s

    def range(
        self, 
        field: str, 
        from_value: tp.Optional[str] = None, 
        to_value: tp.Optional[str] = None
    ) -> "Search":
        """
        Add a range filter to the search.

        Args:
            field: The field to apply the range filter to
            from_value: Start value of the range
            to_value: End value of the range

        Returns:
            A new Search instance with the range filter applied.
        """
        if from_value is None and to_value is None:
            raise ValueError("At least one of from_value or to_value must be provided!")
        
        s = self._clone()
        if not s._search_request.range_filters:
            s._search_request.range_filters = []
            
        s._search_request.range_filters.append(
            Range(
                field=field,
                value_from=from_value,
                value_to=to_value
            )
        )
        return s

    def sort(self, *fields: str) -> "Search":
        """
        Add sorting to the search.

        Args:
            *fields: Field names to sort by. Prefix with '-' for descending order.
                Example: sort('category', '-title')

        Returns:
            A new Search instance with the sort applied.
        """
        s = self._clone()
        if not s._search_request.sort:
            s._search_request.sort = []
            
        for field in fields:
            if field.startswith('-'):
                field_name = field[1:]
                order = Order.desc
            else:
                field_name = field
                order = Order.asc
                
            s._search_request.sort.append(Sort(field=field_name, order=order))
        return s

    def fields(self, *field_names: str) -> "Search":
        """
        Specify which fields to return in the response.

        Args:
            *field_names: Names of fields to include in the response

        Returns:
            A new Search instance with the field selection applied.
        """
        s = self._clone()
        s._search_request.fields = list(field_names)
        return s

    def facets(self, *facet_names: str) -> "Search":
        """
        Add facets to the search.

        Args:
            *facet_names: Names of fields to facet on

        Returns:
            A new Search instance with the facets applied.
        """
        s = self._clone()
        s._search_request.facets = list(facet_names)
        return s

    def paginate(self, offset: int = 0, limit: tp.Optional[int] = None) -> "Search":
        """
        Set pagination parameters.

        Args:
            offset: Number of results to skip
            limit: Maximum number of results to return. If None, will return all results
                  but will make multiple API calls as needed.

        Returns:
            A new Search instance with the pagination applied.
        """
        s = self._clone()
        s._has_explicit_pagination = True
        
        if not s._search_request.pagination:
            s._search_request.pagination = Pagination()
            
        s._search_request.pagination.offset = offset
        if limit is not None:
            s._search_request.pagination.limit = min(limit, self.MAX_PAGE_SIZE)
            
        return s

    async def execute(self) -> tp.Dict:
        """
        Execute the search and return the results.

        If pagination is explicitly set, returns only that page of results.
        If no pagination is set, returns all results by making multiple API calls.

        Returns:
            The search response as a dictionary with all requested results.
        """
        # Initialize an empty response with all results
        full_response = {
            "patentFileWrapperDataBag": [],
            "count": await self.count(),
            "requestIdentifier": None
        }
        
        # Collect all items using the iterator
        async for item in self:
            full_response["patentFileWrapperDataBag"].append(item)
            
        # Store the last request's identifier
        if self._response:
            full_response["requestIdentifier"] = self._response.get("requestIdentifier")
            
        # Store facets if present
        if self._response and "facets" in self._response:
            full_response["facets"] = self._response["facets"]
            
        return full_response

    async def count(self) -> int:
        """
        Get the total number of results for the search.

        Returns:
            The total number of results.
        """
        if self._total_count is None:
            # Make a copy with limit=1 and restricted to application number to just get count
            s = self._clone()
            s = s.paginate(offset=0, limit=1).fields("applicationNumberText")
            response = await s._api.patent_search.post_search(s._search_request)
            self._total_count = response["count"]
        return self._total_count

    def __aiter__(self):
        """
        Async iterator over the search results.

        If pagination is explicitly set, yields only that page of results.
        If no pagination is set, automatically fetches and yields all results.

        Yields:
            Each item in the search results.
        """
        return self._aiter()

    async def _aiter(self):
        """
        Internal async iterator implementation.
        
        Handles both explicit pagination and automatic pagination for full result sets.
        Makes API calls as needed to fetch all requested results.
        """
        # Ensure pagination object exists
        if not self._search_request.pagination:
            self._search_request.pagination = Pagination()
            
        # Get total count for pagination
        total_count = await self.count()
        
        # Determine pagination parameters
        if self._has_explicit_pagination:
            # Use user-specified pagination
            start_offset = self._search_request.pagination.offset
            end_offset = (
                start_offset + self._search_request.pagination.limit 
                if self._search_request.pagination.limit is not None 
                else total_count
            )
        else:
            # No explicit pagination, get all results
            start_offset = 0
            end_offset = total_count
            
        # Fetch results in batches
        current_offset = start_offset
        while current_offset < min(end_offset, total_count):
            # Set pagination for this batch
            self._search_request.pagination.offset = current_offset
            self._search_request.pagination.limit = min(
                self.MAX_PAGE_SIZE,
                end_offset - current_offset
            )
            
            # Get batch
            self._response = await self._api.patent_search.post_search(self._search_request)
            
            # Yield items from this batch
            items = self._response.get("patentFileWrapperDataBag", [])
            for item in items:
                yield item
                
            # Update offset for next batch
            current_offset += len(items)
            
            # Break if we got fewer items than requested (end of results)
            if len(items) < self._search_request.pagination.limit:
                break

    def to_dict(self) -> tp.Dict:
        """
        Convert the search request to a dictionary.

        Returns:
            The search request as a dictionary.
        """
        return self._search_request.model_dump()
