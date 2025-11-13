"""
Word Processing Service
Handles tokenization, lemmatization, and word extraction using spaCy
"""
from typing import List, Dict, Set, Optional
from collections import Counter
import logging
import re

# spaCy imports
try:
    import spacy
    from spacy.language import Language
except ImportError:
    spacy = None
    Language = None


logger = logging.getLogger(__name__)


# Global spaCy model cache (load once, reuse)
_nlp_model: Optional[Language] = None


class WordProcessingError(Exception):
    """Raised when word processing fails"""
    pass


def load_spacy_model(model_name: str = "en_core_web_sm") -> Language:
    """
    Load spaCy model with caching

    Args:
        model_name: spaCy model name (default: en_core_web_sm)

    Returns:
        Loaded spaCy Language model

    Raises:
        WordProcessingError: If model loading fails
    """
    global _nlp_model

    if spacy is None:
        raise WordProcessingError(
            "spaCy library not installed. Run: pip install spacy && python -m spacy download en_core_web_sm"
        )

    # Return cached model if already loaded
    if _nlp_model is not None:
        return _nlp_model

    try:
        logger.info(f"Loading spaCy model: {model_name}")
        _nlp_model = spacy.load(model_name)
        logger.info(f"spaCy model loaded successfully: {model_name}")
        return _nlp_model
    except OSError as e:
        raise WordProcessingError(
            f"spaCy model '{model_name}' not found. "
            f"Download it with: python -m spacy download {model_name}"
        ) from e
    except Exception as e:
        raise WordProcessingError(f"Failed to load spaCy model: {str(e)}") from e


def extract_words_from_text(
    text: str,
    min_length: int = 3,
    filter_stopwords: bool = True,
    filter_punctuation: bool = True,
    filter_numbers: bool = True,
    lemmatize: bool = True
) -> List[str]:
    """
    Extract and process words from text using spaCy

    Args:
        text: Input text to process
        min_length: Minimum word length (default: 3)
        filter_stopwords: Remove common stopwords (default: True)
        filter_punctuation: Remove punctuation (default: True)
        filter_numbers: Remove numeric tokens (default: True)
        lemmatize: Convert to lemmatized form (default: True)

    Returns:
        List of processed words

    Raises:
        WordProcessingError: If processing fails
    """
    if not text or not text.strip():
        return []

    try:
        nlp = load_spacy_model()

        # Process text with spaCy
        doc = nlp(text)

        words = []
        for token in doc:
            # Skip if stopword and filtering enabled
            if filter_stopwords and token.is_stop:
                continue

            # Skip if punctuation and filtering enabled
            if filter_punctuation and token.is_punct:
                continue

            # Skip if number and filtering enabled
            if filter_numbers and (token.is_digit or token.like_num):
                continue

            # Skip if whitespace
            if token.is_space:
                continue

            # Get word form (lemmatized or original)
            word = token.lemma_.lower() if lemmatize else token.text.lower()

            # Filter by length
            if len(word) < min_length:
                continue

            # Filter out words with only non-alphabetic characters
            if not re.search(r'[a-z]', word):
                continue

            words.append(word)

        return words

    except Exception as e:
        raise WordProcessingError(f"Failed to process text: {str(e)}") from e


def extract_unique_words(
    text: str,
    min_length: int = 3,
    filter_stopwords: bool = True
) -> Set[str]:
    """
    Extract unique words from text

    Args:
        text: Input text to process
        min_length: Minimum word length (default: 3)
        filter_stopwords: Remove common stopwords (default: True)

    Returns:
        Set of unique processed words

    Raises:
        WordProcessingError: If processing fails
    """
    words = extract_words_from_text(
        text,
        min_length=min_length,
        filter_stopwords=filter_stopwords
    )
    return set(words)


def calculate_word_frequency(text: str, min_length: int = 3) -> Dict[str, int]:
    """
    Calculate frequency of each word in text

    Args:
        text: Input text to analyze
        min_length: Minimum word length (default: 3)

    Returns:
        Dictionary mapping word to frequency count

    Raises:
        WordProcessingError: If processing fails
    """
    words = extract_words_from_text(text, min_length=min_length)
    return dict(Counter(words))


def get_word_statistics(text: str) -> Dict[str, int]:
    """
    Get basic word statistics from text

    Args:
        text: Input text to analyze

    Returns:
        Dictionary with statistics:
        - total_words: Total word count
        - unique_words: Unique word count
        - avg_word_length: Average word length

    Raises:
        WordProcessingError: If processing fails
    """
    try:
        nlp = load_spacy_model()
        doc = nlp(text)

        # Count all tokens that are actual words
        total_words = sum(
            1 for token in doc
            if not token.is_punct and not token.is_space and not token.is_digit
        )

        # Get unique lemmatized words
        unique_words = extract_unique_words(text)

        # Calculate average word length
        word_lengths = [
            len(token.text) for token in doc
            if not token.is_punct and not token.is_space
        ]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0

        return {
            "total_words": total_words,
            "unique_words": len(unique_words),
            "avg_word_length": round(avg_word_length, 2)
        }

    except Exception as e:
        raise WordProcessingError(f"Failed to calculate statistics: {str(e)}") from e


def get_pos_distribution(text: str) -> Dict[str, int]:
    """
    Get part-of-speech distribution in text

    Args:
        text: Input text to analyze

    Returns:
        Dictionary mapping POS tags to counts
        Common tags: NOUN, VERB, ADJ, ADV, PROPN, etc.

    Raises:
        WordProcessingError: If processing fails
    """
    try:
        nlp = load_spacy_model()
        doc = nlp(text)

        pos_counts = Counter(
            token.pos_ for token in doc
            if not token.is_punct and not token.is_space
        )

        return dict(pos_counts)

    except Exception as e:
        raise WordProcessingError(f"Failed to analyze POS: {str(e)}") from e


def filter_by_pos(
    text: str,
    pos_tags: List[str],
    lemmatize: bool = True
) -> List[str]:
    """
    Extract words with specific part-of-speech tags

    Args:
        text: Input text to process
        pos_tags: List of POS tags to keep (e.g., ['NOUN', 'VERB'])
        lemmatize: Convert to lemmatized form (default: True)

    Returns:
        List of words matching POS tags

    Raises:
        WordProcessingError: If processing fails

    Example:
        # Extract only nouns and verbs
        words = filter_by_pos(text, ['NOUN', 'VERB'])
    """
    try:
        nlp = load_spacy_model()
        doc = nlp(text)

        words = []
        for token in doc:
            if token.pos_ in pos_tags and not token.is_stop:
                word = token.lemma_.lower() if lemmatize else token.text.lower()
                if len(word) >= 3 and re.search(r'[a-z]', word):
                    words.append(word)

        return words

    except Exception as e:
        raise WordProcessingError(f"Failed to filter by POS: {str(e)}") from e


def normalize_word(word: str) -> str:
    """
    Normalize a single word for lookup

    Args:
        word: Word to normalize

    Returns:
        Normalized word (lowercase, lemmatized if possible)
    """
    word = word.lower().strip()

    # Try to lemmatize single word if spaCy is available
    try:
        nlp = load_spacy_model()
        doc = nlp(word)
        if len(doc) > 0:
            return doc[0].lemma_.lower()
    except Exception:
        pass

    return word


def batch_normalize_words(words: List[str]) -> List[str]:
    """
    Normalize multiple words efficiently

    Args:
        words: List of words to normalize

    Returns:
        List of normalized words
    """
    try:
        nlp = load_spacy_model()

        # Process all words in one batch for efficiency
        text = " ".join(words)
        doc = nlp(text)

        return [token.lemma_.lower() for token in doc]

    except Exception:
        # Fallback to simple lowercase
        return [word.lower().strip() for word in words]
