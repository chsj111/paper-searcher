import json
from pathlib import Path
from datetime import date


class Storage:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def _day_dir(self, day: date | None = None) -> Path:
        d = day or date.today()
        p = self.data_dir / d.isoformat()
        p.mkdir(parents=True, exist_ok=True)
        return p

    def save_papers(self, papers: list[dict], day: date | None = None):
        path = self._day_dir(day) / "papers.json"
        path.write_text(json.dumps(papers, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_papers(self, day: date | None = None) -> list[dict]:
        path = self._day_dir(day) / "papers.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def save_stats(self, stats: dict, day: date | None = None):
        path = self._day_dir(day) / "stats.json"
        path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_stats(self, day: date | None = None) -> dict:
        path = self._day_dir(day) / "stats.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save_report(self, content: str, query: str, day: date | None = None):
        safe_name = query.replace("/", "_").replace("\\", "_")[:50]
        path = self._day_dir(day) / f"report_{safe_name}.md"
        path.write_text(content, encoding="utf-8")

    def load_report(self, query: str, day: date | None = None) -> str | None:
        safe_name = query.replace("/", "_").replace("\\", "_")[:50]
        path = self._day_dir(day) / f"report_{safe_name}.md"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def list_dates(self) -> list[date]:
        if not self.data_dir.exists():
            return []
        dates = []
        for p in sorted(self.data_dir.iterdir(), reverse=True):
            if p.is_dir():
                try:
                    dates.append(date.fromisoformat(p.name))
                except ValueError:
                    pass
        return dates

    def list_reports(self, day: date | None = None) -> list[str]:
        d = self._day_dir(day)
        return [f.stem.removeprefix("report_") for f in d.glob("report_*.md")]
