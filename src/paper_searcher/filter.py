import re


def filter_papers(papers: list[dict], query: str) -> list[dict]:
    keywords = _parse_query(query)
    if not keywords:
        return papers

    results = []
    for p in papers:
        text = f"{p.get('title', '')} {p.get('abstract', '')}".lower()
        if _match(text, keywords):
            results.append(p)
    return results


def _parse_query(query: str) -> list[list[str]]:
    groups = [g.strip() for g in query.split("OR") if g.strip()]
    result = []
    for group in groups:
        terms = [t.strip().lower() for t in group.split("AND") if t.strip()]
        if not terms:
            terms = [w.lower() for w in group.split() if w.strip()]
        result.append(terms)
    return result


def _match(text: str, keyword_groups: list[list[str]]) -> bool:
    for group in keyword_groups:
        if all(term in text for term in group):
            return True
    return False
