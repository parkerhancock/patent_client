import typing as tp

from .api import ODPApi
from .model import (
    Assignment,
    BdssResponseBag,
    BdssResponseProductBag,
    DocumentBag,
    EventData,
    ForeignPriority,
    PatentDataResponse,
    PatentFileWrapperDataBagItem,
)
from .search import Search, BulkDataSearch


class PatentFileWrapperManager(Search):
    """
    Manager for USPTO ODP Patent File Wrapper data.
    
    Provides a unified interface for:
    1. Direct access to API endpoints via get_* methods
    2. Search interface directly on the manager
    
    """
    
    def __init__(self, api_key: tp.Optional[str] = None):
        self._api = ODPApi(api_key=api_key)
        super().__init__(self)
    
    async def get_application_data(self, application_id: str) -> PatentFileWrapperDataBagItem:
        """Get detailed patent application data by application ID."""
        return await self._api.patent_search.get_application_data(application_id)
    
    async def get_application_biblio_data(self, application_id: str) -> PatentFileWrapperDataBagItem:
        """Get basic bibliographic data for a patent application."""
        return await self._api.patent_search.get_application_biblio_data(application_id)
    
    async def get_patent_term_adjustment_data(self, application_id: str) -> PatentFileWrapperDataBagItem:
        """Get patent term adjustment data for an application."""
        return await self._api.patent_search.get_patent_term_adjustment_data(application_id)
    
    async def get_assignments(self, application_id: str) -> tp.List[Assignment]:
        """Get assignment history for a patent application."""
        return await self._api.patent_search.get_assignments(application_id)
    
    async def get_attorney_data(self, application_id: str) -> PatentFileWrapperDataBagItem:
        """Get attorney information for a patent application."""
        return await self._api.patent_search.get_attorney_data(application_id)
    
    async def get_continuity_data(self, application_id: str) -> PatentDataResponse:
        """Get continuity data for a patent application."""
        return await self._api.patent_search.get_continuity_data(application_id)
    
    async def get_foreign_priority_data(self, application_id: str) -> tp.List[ForeignPriority]:
        """Get foreign priority data for a patent application."""
        return await self._api.patent_search.get_foreign_priority_data(application_id)
    
    async def get_transactions(self, application_id: str) -> tp.List[EventData]:
        """Get transaction history for a patent application."""
        return await self._api.patent_search.get_transactions(application_id)
    
    async def get_documents(self, application_id: str) -> DocumentBag:
        """Get document information for a patent application."""
        return await self._api.patent_search.get_documents(application_id)


class BulkDataManager(BulkDataSearch):
    """
    Manager for USPTO ODP Bulk Data endpoints.
    
    Provides a unified interface for:
    1. Direct access to bulk data products via get_product
    2. Search interface for finding bulk data products
    
    """
    
    def __init__(self, api_key: tp.Optional[str] = None):
        self._api = ODPApi(api_key=api_key)
        super().__init__(self)
    
    async def get_product(
        self,
        product_identifier: str,
        *,
        file_data_from_date: tp.Optional[str] = None,
        file_data_to_date: tp.Optional[str] = None,
        offset: tp.Optional[int] = None,
        limit: tp.Optional[int] = None,
        include_files: bool = True,
        latest: bool = False,
    ) -> BdssResponseProductBag:
        """
        Get information about a specific bulk data product.
        
        Args:
            product_identifier: The unique identifier for the product (e.g. 'PTFWPRE')
            file_data_from_date: Filter files by data start date (YYYY-MM-DD)
            file_data_to_date: Filter files by data end date (YYYY-MM-DD)
            offset: Number of results to skip
            limit: Maximum number of results to return
            include_files: Whether to include file details in the response
            latest: Whether to only return the latest version of files
            
        Returns:
            Details about the requested bulk data product
        """
        return await self._api.bulk_data.get_product(
            product_identifier=product_identifier,
            file_data_from_date=file_data_from_date,
            file_data_to_date=file_data_to_date,
            offset=offset,
            limit=limit,
            include_files=include_files,
            latest=latest,
        )
