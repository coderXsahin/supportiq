import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SYNONYMS = {
    "unavailable": "down",
    "unreachable": "down",
    "failure": "failed",
    "failed": "failure",
    "unable": "cannot",
    "connection": "connect",
    "connecting": "connect",
    "connectivity": "connect",
    "issues": "issue",
    "problems": "problem",
    "servers": "server",
    "databases": "database",
    "services": "service",
    "users": "user"
}


IMPORTANT_TERMS = {
    "database",
    "server",
    "network",
    "vpn",
    "login",
    "password",
    "application",
    "api",
    "security",
    "email",
    "printer",
    "storage",
    "connection",
    "connect",
    "down",
    "failure",
    "failed",
    "error",
    "timeout"
}


def normalize_text(text: str) -> str:
    """
    Normalize ticket text and map common IT terms.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    words = text.split()

    normalized_words = [
        SYNONYMS.get(word, word)
        for word in words
    ]

    return " ".join(normalized_words)


def calculate_tfidf_similarity(
    text1: str,
    text2: str
) -> float:
    """
    Calculate TF-IDF cosine similarity.
    """

    if not text1 or not text2:
        return 0.0

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2)
    )

    vectors = vectorizer.fit_transform(
        [text1, text2]
    )

    return float(
        cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]
    )


def calculate_keyword_similarity(
    text1: str,
    text2: str
) -> float:
    """
    Calculate similarity based on important IT terms.
    """

    words1 = set(text1.split())
    words2 = set(text2.split())

    terms1 = words1.intersection(IMPORTANT_TERMS)
    terms2 = words2.intersection(IMPORTANT_TERMS)

    if not terms1 or not terms2:
        return 0.0

    intersection = terms1.intersection(terms2)
    union = terms1.union(terms2)

    return len(intersection) / len(union)


def calculate_similarity(
    text1: str,
    text2: str
) -> float:
    """
    Calculate hybrid duplicate similarity.

    Combines:
    - TF-IDF similarity
    - Important IT keyword similarity
    """

    normalized_text1 = normalize_text(text1)
    normalized_text2 = normalize_text(text2)

    if not normalized_text1 or not normalized_text2:
        return 0.0

    tfidf_score = calculate_tfidf_similarity(
        normalized_text1,
        normalized_text2
    )

    keyword_score = calculate_keyword_similarity(
        normalized_text1,
        normalized_text2
    )

    hybrid_score = (
        0.6 * tfidf_score
        + 0.4 * keyword_score
    )

    return round(hybrid_score, 4)


def find_best_duplicate(
    new_ticket_text: str,
    existing_tickets,
    threshold: float = 0.30
):
    """
    Find the most similar existing ticket.

    Returns:
        {
            "ticket_id": int | None,
            "similarity": float,
            "is_duplicate": bool
        }
    """

    best_ticket_id = None
    best_similarity = 0.0

    for ticket in existing_tickets:

        existing_text = (
            f"{ticket.title}. "
            f"{ticket.description}"
        )

        similarity = calculate_similarity(
            new_ticket_text,
            existing_text
        )

        if similarity > best_similarity:

            best_similarity = similarity
            best_ticket_id = ticket.id

    return {
        "ticket_id": best_ticket_id
        if best_similarity >= threshold
        else None,

        "similarity": best_similarity,

        "is_duplicate": best_similarity >= threshold
    }


def is_duplicate(
    new_ticket_text: str,
    existing_ticket_text: str,
    threshold: float = 0.30
) -> bool:
    """
    Determine whether two tickets are sufficiently similar
    to be considered duplicates.
    """

    similarity = calculate_similarity(
        new_ticket_text,
        existing_ticket_text
    )

    return similarity >= threshold