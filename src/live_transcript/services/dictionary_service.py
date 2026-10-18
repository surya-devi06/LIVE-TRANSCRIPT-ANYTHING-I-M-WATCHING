"""Dictionary lookup service using free online dictionary API with offline/fallback handling."""

from dataclasses import dataclass
import json
from typing import Optional
import urllib.parse
import urllib.request

from live_transcript.utils.logging_setup import get_logger

logger = get_logger("services.dictionary")


@dataclass
class DictionaryResult:
    """Result of looking up a word in the dictionary."""
    word: str
    meaning: str
    phonetic: str = ""
    part_of_speech: str = ""
    example: str = ""
    found: bool = False
    error_message: Optional[str] = None


class DictionaryService:
    """Service to look up word meanings, phonetics, and examples without requiring paid API keys."""

    API_URL_TEMPLATE = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    OFFLINE_LEXICON = {
        "intelligence": {
            "meaning": "The ability to acquire, understand, and apply knowledge, reasoning, and skills.",
            "part_of_speech": "noun",
            "phonetic": "/ɪnˈtɛlɪdʒəns/",
            "example": "Artificial intelligence enables machines to learn from experience.",
        },
        "artificial": {
            "meaning": "Made or produced by human beings rather than occurring naturally.",
            "part_of_speech": "adjective",
            "phonetic": "/ˌɑːtɪˈfɪʃl/",
            "example": "Artificial intelligence creates synthetic cognitive abilities.",
        },
        "transcription": {
            "meaning": "A written or printed representation of spoken words or audio speech.",
            "part_of_speech": "noun",
            "phonetic": "/trænˈskrɪpʃn/",
            "example": "The live transcription displays spoken words in real time.",
        },
        "recognition": {
            "meaning": "The identification of a thing or person from previous knowledge or pattern matching.",
            "part_of_speech": "noun",
            "phonetic": "/ˌrɛkəɡˈnɪʃn/",
            "example": "Automated speech recognition translates audio waves into text.",
        },
        "computer": {
            "meaning": "An electronic device for storing and processing data according to instructions.",
            "part_of_speech": "noun",
            "phonetic": "/kəmˈpjuːtə/",
            "example": "The computer captured desktop audio from system playback.",
        },
        "algorithm": {
            "meaning": "A process or set of rules to be followed in calculations or problem-solving operations.",
            "part_of_speech": "noun",
            "phonetic": "/ˈælɡərɪðəm/",
            "example": "The Whisper decoding algorithm converts acoustic features into tokens.",
        },
        "pipeline": {
            "meaning": "A sequence of data processing stages where the output of each stage is the input of the next.",
            "part_of_speech": "noun",
            "phonetic": "/ˈpaɪplaɪn/",
            "example": "The transcription pipeline connects audio capture, chunking, and speech inference.",
        },
        "latency": {
            "meaning": "The delay before a transfer of data begins following an instruction or audio arrival.",
            "part_of_speech": "noun",
            "phonetic": "/ˈleɪtnsi/",
            "example": "Chunk windowing was optimized to minimize transcription latency.",
        },
    }

    def __init__(self, timeout: float = 3.5) -> None:
        self.timeout = timeout

    def lookup(self, word_or_phrase: str) -> DictionaryResult:
        """Look up word or phrase definition.
        
        Uses the free public dictionary API with an integrated offline lexicon fallback.
        If unavailable or not found, returns a structured result allowing user to enter or edit meaning manually.
        """
        clean_word = word_or_phrase.strip().strip(".,!?:;\"'()[]{}")
        if not clean_word:
            return DictionaryResult(
                word="",
                meaning="",
                found=False,
                error_message="Please enter a valid word or phrase.",
            )

        # For single words, attempt online dictionary lookup
        url = self.API_URL_TEMPLATE.format(word=urllib.parse.quote(clean_word.lower()))
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "LiveTranscriptApp/0.1.0"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                status = getattr(response, "status", 200)
                if status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return self._parse_api_response(clean_word, data)
        except urllib.error.HTTPError as http_err:
            if http_err.code == 404:
                # Check offline lexicon before giving up
                offline_match = self.OFFLINE_LEXICON.get(clean_word.lower())
                if offline_match:
                    return DictionaryResult(
                        word=clean_word,
                        meaning=offline_match["meaning"],
                        phonetic=offline_match.get("phonetic", ""),
                        part_of_speech=offline_match.get("part_of_speech", ""),
                        example=offline_match.get("example", ""),
                        found=True,
                    )
                logger.info("Word '%s' not found in online dictionary (404).", clean_word)
                return DictionaryResult(
                    word=clean_word,
                    meaning="",
                    found=False,
                    error_message=f"No definition found for '{clean_word}'. You can enter a custom meaning below.",
                )
            else:
                logger.warning("HTTP error looking up '%s': %s", clean_word, http_err)
        except Exception as exc:
            logger.info("Online dictionary lookup skipped/failed for '%s' (%s). Checking offline fallback.", clean_word, exc)

        # Check offline lexicon fallback
        offline_match = self.OFFLINE_LEXICON.get(clean_word.lower())
        if offline_match:
            return DictionaryResult(
                word=clean_word,
                meaning=offline_match["meaning"],
                phonetic=offline_match.get("phonetic", ""),
                part_of_speech=offline_match.get("part_of_speech", ""),
                example=offline_match.get("example", ""),
                found=True,
            )

        return DictionaryResult(
            word=clean_word,
            meaning="",
            found=False,
            error_message="Online dictionary not reached (offline). You can type the meaning manually.",
        )

    def _parse_api_response(self, word: str, data: list) -> DictionaryResult:
        """Parse JSON response from Dictionary API."""
        if not isinstance(data, list) or len(data) == 0:
            return DictionaryResult(word=word, meaning="", found=False)

        entry = data[0]
        phonetic = entry.get("phonetic", "")
        if not phonetic:
            phonetics_list = entry.get("phonetics", [])
            for p in phonetics_list:
                if p.get("text"):
                    phonetic = p.get("text")
                    break

        meanings_list = entry.get("meanings", [])
        combined_meanings = []
        part_of_speech = ""
        first_example = ""

        for m in meanings_list:
            pos = m.get("partOfSpeech", "")
            if not part_of_speech and pos:
                part_of_speech = pos

            defs = m.get("definitions", [])
            for d in defs[:2]:  # Keep top definitions per part of speech
                def_text = d.get("definition", "").strip()
                if def_text:
                    if pos:
                        combined_meanings.append(f"({pos}) {def_text}")
                    else:
                        combined_meanings.append(def_text)

                if not first_example and d.get("example"):
                    first_example = d.get("example").strip()

        meaning_text = "\n".join(combined_meanings) if combined_meanings else "No detailed definition provided."

        return DictionaryResult(
            word=word,
            meaning=meaning_text,
            phonetic=phonetic,
            part_of_speech=part_of_speech,
            example=first_example,
            found=True,
        )
