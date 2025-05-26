import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, Mock, patch
import aiohttp
from edgar_client import EdgarClient

@pytest_asyncio.fixture
async def edgar_client():
    """Create an EdgarClient instance for testing"""
    client = EdgarClient(user_agent="Test Agent test@example.com")
    async with client as c:
        yield c

@pytest.mark.asyncio
class TestEdgarClient:
    
    async def test_init(self):
        """Test EdgarClient initialization"""
        client = EdgarClient()
        assert client.user_agent == "Edgar MCP Tool contact@example.com"
        assert client.session is None
        
    async def test_context_manager(self):
        """Test EdgarClient context manager"""
        client = EdgarClient()
        async with client as c:
            assert c.session is not None
            assert isinstance(c.session, aiohttp.ClientSession)
            
    async def test_format_cik(self):
        """Test CIK formatting"""
        client = EdgarClient()
        assert client.format_cik("123") == "0000000123"
        assert client.format_cik(123) == "0000000123"
        assert client.format_cik("0000000123") == "0000000123"
        
    @patch('aiohttp.ClientSession.get')
    async def test_make_request_success(self, mock_get, edgar_client):
        """Test successful API request"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"test": "data"})
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        result = await edgar_client._make_request("http://test.com")
        assert result == {"test": "data"}
        
    @patch('aiohttp.ClientSession.get')
    async def test_make_request_error(self, mock_get, edgar_client):
        """Test API request error handling"""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.raise_for_status = Mock(side_effect=aiohttp.ClientResponseError(
            request_info=Mock(), history=(), status=404))
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        with pytest.raises(aiohttp.ClientResponseError):
            await edgar_client._make_request("http://test.com")
            
    @patch.object(EdgarClient, '_make_request')
    async def test_get_company_submissions(self, mock_request, edgar_client):
        """Test get_company_submissions method"""
        mock_data = {
            "name": "Test Company",
            "filings": {"recent": {"form": ["10-K", "10-Q"]}}
        }
        mock_request.return_value = mock_data
        
        result = await edgar_client.get_company_submissions("123")
        assert result == mock_data
        mock_request.assert_called_once_with(
            "https://data.sec.gov/submissions/CIK0000000123.json"
        )
        
    @patch.object(EdgarClient, '_make_request')
    async def test_get_company_facts(self, mock_request, edgar_client):
        """Test get_company_facts method"""
        mock_data = {
            "entityName": "Test Company",
            "facts": {"us-gaap": {"Assets": {"description": "Total Assets"}}}
        }
        mock_request.return_value = mock_data
        
        result = await edgar_client.get_company_facts("123")
        assert result == mock_data
        mock_request.assert_called_once_with(
            "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000123.json"
        )
        
    @patch.object(EdgarClient, '_make_request')
    async def test_get_company_concept(self, mock_request, edgar_client):
        """Test get_company_concept method"""
        mock_data = {
            "entityName": "Test Company",
            "units": {"USD": [{"val": 1000000, "end": "2023-12-31"}]}
        }
        mock_request.return_value = mock_data
        
        result = await edgar_client.get_company_concept("123", "us-gaap", "Assets")
        assert result == mock_data
        mock_request.assert_called_once_with(
            "https://data.sec.gov/api/xbrl/companyconcept/CIK0000000123/us-gaap/Assets.json"
        )
        
    @patch.object(EdgarClient, '_make_request')
    async def test_search_companies(self, mock_request, edgar_client):
        """Test search_companies method"""
        mock_data = {
            "data": [
                [320193, "Apple Inc.", "AAPL", "Nasdaq"]
            ]
        }
        mock_request.return_value = mock_data
        
        result = await edgar_client.search_companies("Apple")
        
        assert "hits" in result
        assert "hits" in result["hits"]
        assert len(result["hits"]["hits"]) == 1
        
        company = result["hits"]["hits"][0]["_source"]
        assert company["entity"] == "Apple Inc."
        assert company["cik"] == "0000320193"
        assert company["tickers"] == ["AAPL"]
        
        mock_request.assert_called_once_with(
            "https://www.sec.gov/files/company_tickers_exchange.json"
        )
        
    @patch('aiohttp.ClientSession.get')
    async def test_download_filing(self, mock_get, edgar_client):
        """Test download_filing method"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=b"test filing content")
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        result = await edgar_client.download_filing("1321655", "0000123456-23-000001")
        assert result == b"test filing content"
        
        # Verify the correct URL was called
        expected_url = "https://www.sec.gov/Archives/edgar/data/0001321655/000012345623000001/0000123456-23-000001.txt"
        mock_get.assert_called_once_with(expected_url)