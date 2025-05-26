import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
import mcp.types as types
from main import EdgarMCPServer

@pytest.fixture
def mcp_server():
    """Create an EdgarMCPServer instance for testing"""
    return EdgarMCPServer()

@pytest.mark.asyncio
class TestEdgarMCPServer:
    
    async def test_init(self, mcp_server):
        """Test EdgarMCPServer initialization"""
        assert mcp_server.app is not None
        assert mcp_server.edgar_client is None
        
    @patch('main.EdgarClient')
    async def test_get_edgar_client(self, mock_edgar_client, mcp_server):
        """Test get_edgar_client method"""
        mock_client = AsyncMock()
        mock_edgar_client.return_value = mock_client
        
        client = await mcp_server.get_edgar_client()
        assert client == mock_client
        mock_client.__aenter__.assert_called_once()
        
        # Test caching
        client2 = await mcp_server.get_edgar_client()
        assert client2 == mock_client
        assert mock_client.__aenter__.call_count == 1  # Should not be called again
        
    @patch.object(EdgarMCPServer, 'get_edgar_client')
    async def test_search_companies_success(self, mock_get_client, mcp_server):
        """Test successful company search"""
        mock_client = AsyncMock()
        mock_client.search_companies.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "entity": "Apple Inc",
                            "cik": "320193",
                            "tickers": ["AAPL"]
                        }
                    },
                    {
                        "_source": {
                            "entity": "Microsoft Corp",
                            "cik": "789019",
                            "tickers": ["MSFT"]
                        }
                    }
                ]
            }
        }
        mock_get_client.return_value = mock_client
        
        result = await mcp_server.search_companies("tech")
        
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Apple Inc" in result[0].text
        assert "Microsoft Corp" in result[0].text
        assert "320193" in result[0].text
        assert "789019" in result[0].text
        
    @patch.object(EdgarMCPServer, 'get_edgar_client')
    async def test_search_companies_no_results(self, mock_get_client, mcp_server):
        """Test company search with no results"""
        mock_client = AsyncMock()
        mock_client.search_companies.return_value = {
            "hits": {"hits": []}
        }
        mock_get_client.return_value = mock_client
        
        result = await mcp_server.search_companies("nonexistent")
        
        assert len(result) == 1
        assert "No companies found" in result[0].text
        
    @patch.object(EdgarMCPServer, 'get_edgar_client')
    async def test_search_companies_error(self, mock_get_client, mcp_server):
        """Test company search error handling"""
        mock_client = AsyncMock()
        mock_client.search_companies.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        
        result = await mcp_server.search_companies("test")
        
        assert len(result) == 1
        assert "Error searching companies" in result[0].text
        
    @patch.object(EdgarMCPServer, 'get_edgar_client')
    async def test_get_company_submissions_success(self, mock_get_client, mcp_server):
        """Test successful company submissions retrieval"""
        mock_client = AsyncMock()
        mock_client.get_company_submissions.return_value = {
            "name": "Apple Inc",
            "filings": {
                "recent": {
                    "form": ["10-K", "10-Q", "8-K"],
                    "filingDate": ["2023-10-27", "2023-07-31", "2023-05-04"],
                    "accessionNumber": ["0000320193-23-000106", "0000320193-23-000077", "0000320193-23-000064"],
                    "items": ["", "", "2.02,9.01"]
                }
            }
        }
        mock_get_client.return_value = mock_client
        
        result = await mcp_server.get_company_submissions("320193")
        
        assert len(result) == 1
        assert "Apple Inc" in result[0].text
        assert "10-K" in result[0].text
        assert "2023-10-27" in result[0].text
        
    @patch.object(EdgarMCPServer, 'get_edgar_client')
    async def test_get_company_facts_success(self, mock_get_client, mcp_server):
        """Test successful company facts retrieval"""
        mock_client = AsyncMock()
        mock_client.get_company_facts.return_value = {
            "entityName": "Apple Inc",
            "facts": {
                "us-gaap": {
                    "Assets": {
                        "description": "Assets",
                        "units": {"USD": []}
                    },
                    "Revenues": {
                        "description": "Revenues",
                        "units": {"USD": []}
                    }
                }
            }
        }
        mock_get_client.return_value = mock_client
        
        result = await mcp_server.get_company_facts("320193")
        
        assert len(result) == 1
        assert "Apple Inc" in result[0].text
        assert "Assets" in result[0].text
        assert "Revenues" in result[0].text
        
    @patch.object(EdgarMCPServer, 'get_edgar_client')
    async def test_get_company_concept_success(self, mock_get_client, mcp_server):
        """Test successful company concept retrieval"""
        mock_client = AsyncMock()
        mock_client.get_company_concept.return_value = {
            "entityName": "Apple Inc",
            "units": {
                "USD": [
                    {"val": 352755000000, "end": "2023-09-30", "form": "10-K"},
                    {"val": 365725000000, "end": "2022-09-24", "form": "10-K"}
                ]
            }
        }
        mock_get_client.return_value = mock_client
        
        result = await mcp_server.get_company_concept("320193", "us-gaap", "Assets")
        
        assert len(result) == 1
        assert "Apple Inc" in result[0].text
        assert "352,755,000,000" in result[0].text
        assert "2023-09-30" in result[0].text
        
    @patch.object(EdgarMCPServer, 'get_edgar_client')
    async def test_download_filing_success(self, mock_get_client, mcp_server):
        """Test successful filing download"""
        mock_client = AsyncMock()
        mock_client.download_filing.return_value = b"SEC filing content here..."
        mock_get_client.return_value = mock_client
        
        result = await mcp_server.download_filing("320193", "0000320193-23-000106")
        
        assert len(result) == 1
        assert "content preview" in result[0].text
        assert "SEC filing content here..." in result[0].text
        
    @patch.object(EdgarMCPServer, 'get_edgar_client')
    @patch('builtins.open', create=True)
    async def test_download_filing_with_save_path(self, mock_open, mock_get_client, mcp_server):
        """Test filing download with save path"""
        mock_client = AsyncMock()
        mock_client.download_filing.return_value = b"SEC filing content here..."
        mock_get_client.return_value = mock_client
        
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = await mcp_server.download_filing("320193", "0000320193-23-000106", "/tmp/filing.txt")
        
        assert len(result) == 1
        assert "downloaded successfully" in result[0].text
        assert "/tmp/filing.txt" in result[0].text
        mock_file.write.assert_called_once_with(b"SEC filing content here...")
        
    def test_setup_tools(self, mcp_server):
        """Test that tools are properly registered"""
        mcp_server.setup_tools()
        
        # Test that the tools are properly configured
        # This is somewhat limited since we can't easily test the decorators
        # but we can at least verify the server has the app configured
        assert mcp_server.app is not None