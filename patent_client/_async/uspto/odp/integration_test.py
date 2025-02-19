import pytest

from . import PatentFileWrapper, BulkData


class TestPatentFileWrapper:
    """Integration tests for USPTO ODP Patent File Wrapper functionality."""
    
    @pytest.fixture
    def default_search(self):
        return PatentFileWrapper.objects.fields("applicationNumberText").paginate(limit=5)
    
    @pytest.mark.asyncio
    async def test_search_interface(self, default_search):
        """Test the search interface of the PatentFileWrapper model."""
        # Basic search with limit
        search = default_search.query(
            "applicationMetaData.applicationTypeLabelName:Utility"
        )
        results = await search.execute()
        assert results["count"] > 0
        assert len(results["patentFileWrapperDataBag"]) <= 5
        
        # Search with filters
        results = await default_search.filter(
            "applicationMetaData.applicationStatusDescriptionText", "Patented Case"
        ).execute()
        assert results["count"] > 0
        assert len(results["patentFileWrapperDataBag"]) <= 5
        
        # Search with sorting
        results = await default_search.sort("-applicationMetaData.filingDate").execute()
        assert results["count"] > 0
        assert len(results["patentFileWrapperDataBag"]) <= 5
    
    @pytest.mark.asyncio
    async def test_direct_api_access(self):
        """Test direct API access methods of the PatentFileWrapper model."""
        # Use a known application number for testing
        application_id = "15123456"
        
        # Test get_application_data
        app_data = await PatentFileWrapper.objects.get_application_data(application_id)
        assert app_data.application_number_text is not None
        
        # Test get_application_biblio_data
        biblio_data = await PatentFileWrapper.objects.get_application_biblio_data(application_id)
        assert biblio_data.application_number_text is not None
        
        # Test get_assignments
        assignments = await PatentFileWrapper.objects.get_assignments(application_id)
        assert isinstance(assignments, list)
        
        # Test get_attorney_data
        attorney_data = await PatentFileWrapper.objects.get_attorney_data(application_id)
        assert attorney_data.record_attorney is not None
        
        # Test get_continuity_data
        continuity_data = await PatentFileWrapper.objects.get_continuity_data(application_id)
        assert continuity_data.patent_file_wrapper_data_bag is not None
    
    @pytest.mark.asyncio
    async def test_search_iteration(self, default_search):
        """Test async iteration over search results."""
        search = default_search.paginate(limit=10)  # Reduced from 50 to 10
        
        count = 0
        async for item in search:
            assert isinstance(item, dict)
            count += 1
        
        assert 0 < count <= 10
    
    @pytest.mark.asyncio
    async def test_search_facets(self, default_search):
        """Test search facets functionality."""
        # Add date range to limit results while still getting meaningful facets
        results = await default_search.range(
            field="applicationMetaData.filingDate",
            from_value="2023-01-01",
            to_value="2023-12-31"  # Expanded date range for more results
        ).facets(
            "applicationMetaData.applicationTypeLabelName",
            "applicationMetaData.applicationStatusCode"
        ).paginate(limit=5).execute()
        
        assert "facets" in results
        assert results["facets"] is not None
    
    @pytest.mark.asyncio
    async def test_search_fields(self):
        """Test field selection in search results."""
        results = await PatentFileWrapper.objects.query(
            "applicationMetaData.applicationTypeLabelName:Utility"
        ).fields(
            "applicationNumberText",
            "applicationMetaData.filingDate",
            "applicationMetaData.applicationStatusDescriptionText"
        ).paginate(limit=5).execute()
        
        assert results["count"] > 0
        assert len(results["patentFileWrapperDataBag"]) <= 5
        first_result = results["patentFileWrapperDataBag"][0]
        assert "applicationNumberText" in first_result
    
    @pytest.mark.asyncio
    async def test_search_range_filter(self):
        """Test range filter in search."""
        # Narrow date range for testing
        results = await PatentFileWrapper.objects.query(
            "applicationMetaData.applicationTypeLabelName:Utility"
        ).range(
            field="applicationMetaData.filingDate",
            from_value="2023-01-01",
            to_value="2023-01-31"
        ).paginate(limit=5).execute()
        
        assert results["count"] > 0
        assert len(results["patentFileWrapperDataBag"]) <= 5
    
    @pytest.mark.asyncio
    async def test_get_documents(self):
        """Test document retrieval."""
        application_id = "15123456"
        documents = await PatentFileWrapper.objects.get_documents(application_id)
        assert documents.document_bag is not None
    
    @pytest.mark.asyncio
    async def test_get_transactions(self):
        """Test transaction history retrieval."""
        application_id = "15123456"
        transactions = await PatentFileWrapper.objects.get_transactions(application_id)
        assert isinstance(transactions, list)


class TestBulkData:
    """Integration tests for USPTO ODP Bulk Data functionality."""
    
    @pytest.fixture
    def default_search(self):
        return BulkData.objects.paginate(limit=5).options(include_files=False, facets=False)
    
    @pytest.mark.asyncio
    async def test_search_basic(self, default_search):
        """Test basic search functionality of the BulkData manager."""
        results = await default_search.query(
            product_title="Patent File Wrapper"
        ).execute()
        
        assert results.count > 0
        assert len(results.bulk_data_product_bag) > 0
    
    @pytest.mark.asyncio
    async def test_search_with_string_filters(self, default_search):
        """Test bulk data search with string filters."""
        results = await default_search.query(
            product_title="Patent",
        ).execute()
        
        assert results.count > 0
        assert len(results.bulk_data_product_bag) > 0
        
        results = await default_search.query(
            labels="PATENT",
        ).execute()
        assert results.count > 0
        assert len(results.bulk_data_product_bag) > 0
        
        results = await default_search.query(
            categories="Patent file wrapper",
        ).execute()
        assert results.count > 0
        assert len(results.bulk_data_product_bag) > 0
    
    @pytest.mark.asyncio
    async def test_search_with_list_filters(self, default_search):
        """Test bulk data search with list filters."""
        results = await default_search.query(
            labels=["PATENT", "TRADEMARK"],
            file_types=["JSON", "XML"]
        ).execute()
        
        assert results.count > 0
        assert len(results.bulk_data_product_bag) > 0
    
    @pytest.mark.asyncio
    async def test_search_with_options(self, default_search):
        """Test bulk data search with various options."""
        results = await default_search.query(
            product_title="Patent"
        ).options(
            include_files=True,
            latest=True,
            facets=True
        ).execute()
        
        assert results.count > 0
        assert len(results.bulk_data_product_bag) > 0
        assert hasattr(results, "facets")
    
    @pytest.mark.asyncio
    async def test_search_pagination(self, default_search):
        """Test bulk data search pagination."""
        # Get first page
        first_page = await default_search.query(
            product_title="Patent"
        ).paginate(
            offset=0,
            limit=2
        ).execute()
        
        # Get second page
        second_page = await default_search.query(
            product_title="Patent"
        ).paginate(
            offset=2,
            limit=2
        ).execute()
        
        assert first_page.count > 0
        assert len(first_page.bulk_data_product_bag) == 2
        assert len(second_page.bulk_data_product_bag) == 2
        
        # Ensure pages are different
        first_ids = [p.root.product_identifier for p in first_page.bulk_data_product_bag]
        second_ids = [p.root.product_identifier for p in second_page.bulk_data_product_bag]
        assert first_ids != second_ids
    
    @pytest.mark.asyncio
    async def test_get_product(self):
        """Test getting a specific bulk data product."""
        product = await BulkData.objects.get_product(
            "PTFWPRE",
            include_files=True,
            latest=True
        )
        
        assert product.count > 0
        assert len(product.bulk_data_product_bag) > 0
        assert product.bulk_data_product_bag[0].root.product_identifier == "PTFWPRE" 