import re
from collections import Counter
from ..knowledge import KNOWLEDGE_BASE

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "is", "it",
    "this", "that", "my", "when", "after", "from", "but", "be", "are", "was", "were"
}


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9_-]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    ]


def retrieve(query: str, limit: int = 3) -> list[dict]:
    query_counts = Counter(_tokens(query))
    ranked: list[tuple[float, dict]] = []

    for article in KNOWLEDGE_BASE:
        haystack = " ".join(article["tags"]) + " " + article["title"] + " " + article["body"]
        article_counts = Counter(_tokens(haystack))
        overlap = sum(min(count, article_counts[token]) for token, count in query_counts.items())
        tag_bonus = sum(2 for tag in article["tags"] if tag in query.lower())
        score = overlap + tag_bonus
        ranked.append((float(score), article))

    ranked.sort(key=lambda item: item[0], reverse=True)
    max_score = ranked[0][0] if ranked else 1.0

    results = []
    for score, article in ranked[:limit]:
        normalized = 0.0 if max_score == 0 else round(score / max_score, 2)
        results.append({**article, "score": normalized})
    return results
