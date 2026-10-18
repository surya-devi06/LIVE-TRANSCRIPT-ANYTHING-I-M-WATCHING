"""Unit tests for the DictionaryService with API parsing and offline fallbacks."""

import json
from unittest.mock import MagicMock, patch
import pytest

from live_transcript.services.dictionary_service import DictionaryResult, DictionaryService


def test_dictionary_service_offline_known_word():
    """Verify offline fallback provides rich definition for known vocabulary terms."""
    service = DictionaryService()

    with patch("urllib.request.urlopen", side_effect=Exception("No internet")):
        result = service.lookup("intelligence")
        assert result.word.lower() == "intelligence"
        assert result.found is True
        assert "ability" in result.meaning.lower() or "knowledge" in result.meaning.lower()
        assert result.part_of_speech == "noun"


def test_dictionary_service_offline_unknown_word():
    """Verify offline fallback gracefully handles unknown words with reasonable fallback."""
    service = DictionaryService()

    with patch("urllib.request.urlopen", side_effect=Exception("Network down")):
        result = service.lookup("hypermodernity")
        assert result.word.lower() == "hypermodernity"
        assert result.found is False
        assert "offline" in result.error_message.lower()


def test_dictionary_service_api_parsing_success():
    """Verify parsing of valid Free Dictionary API JSON responses."""
    service = DictionaryService()

    fake_api_response = [
        {
            "word": "transcript",
            "phonetic": "/ˈtrænskrɪpt/",
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "A written or printed version of material originally presented in another medium.",
                            "example": "A transcript of the recording was released to the press.",
                        }
                    ],
                }
            ],
        }
    ]

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(fake_api_response).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = service.lookup("transcript")
        assert result.word == "transcript"
        assert result.phonetic == "/ˈtrænskrɪpt/"
        assert result.part_of_speech == "noun"
        assert "written or printed version" in result.meaning
        assert "recording" in result.example
        assert result.found is True
