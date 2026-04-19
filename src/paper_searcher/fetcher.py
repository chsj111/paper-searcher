import arxiv
from datetime import date, timedelta


def fetch_papers(categories: list[str], target_date: date | None = None,
                 max_results: int = 500) -> list[dict]:
    day = target_date or date.today()
    start = day.strftime("%Y%m%d0000")
    end = day.strftime("%Y%m%d2359")

    cat_query = " OR ".join(f"cat:{c}" for c in categories)
    query = f"({cat_query}) AND submittedDate:[{start} TO {end}]"

    client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=3)
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    papers = []
    for result in client.results(search):
        papers.append({
            "id": result.entry_id,
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "abstract": result.summary,
            "primary_category": result.primary_category,
            "categories": result.categories,
            "published": result.published.isoformat(),
            "updated": result.updated.isoformat(),
            "pdf_url": result.pdf_url,
            "arxiv_url": result.entry_id,
        })

    return papers


def fetch_recent_papers(categories: list[str], days: int = 1,
                        max_results: int = 500) -> dict[date, list[dict]]:
    results = {}
    today = date.today()
    for i in range(days):
        day = today - timedelta(days=i)
        results[day] = fetch_papers(categories, day, max_results)
    return results
