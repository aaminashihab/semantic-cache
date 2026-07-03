import pytest
from unittest.mock import MagicMock
from semantic_cache.providers.gemini import GeminiProvider

def test_gemini_provider_generate(mocker):
    # Mock genai client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Generated response"
    mock_client.models.generate_content.return_value = mock_response
    
    mocker.patch('google.genai.Client', return_value=mock_client)
    
    provider = GeminiProvider(model="gemini-test")
    response = provider.generate("Test prompt")
    
    assert response == "Generated response"
    mock_client.models.generate_content.assert_called_once()
    
def test_gemini_provider_count_tokens(mocker):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.total_tokens = 5
    mock_client.models.count_tokens.return_value = mock_response
    
    mocker.patch('google.genai.Client', return_value=mock_client)
    
    provider = GeminiProvider(model="gemini-test")
    tokens = provider.count_tokens("Test text")
    
    assert tokens == 5
    mock_client.models.count_tokens.assert_called_once()
