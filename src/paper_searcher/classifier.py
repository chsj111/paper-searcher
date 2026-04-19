from collections import Counter


def classify_papers(papers: list[dict]) -> dict:
    by_category = {}
    all_categories = Counter()

    for p in papers:
        cat = p.get("primary_category", "unknown")
        by_category.setdefault(cat, []).append(p)
        for c in p.get("categories", []):
            all_categories[c] += 1

    stats = {
        "total": len(papers),
        "by_primary_category": {
            cat: {"count": len(ps), "paper_ids": [p["id"] for p in ps]}
            for cat, ps in sorted(by_category.items())
        },
        "category_distribution": dict(all_categories.most_common()),
    }

    return stats
