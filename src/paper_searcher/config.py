import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG = _PROJECT_ROOT / "config" / "default.yaml"


@dataclass
class ArxivConfig:
    categories: list[str] = field(default_factory=lambda: ["cs.AI"])
    max_results_per_query: int = 500


@dataclass
class LLMConfig:
    api_url: str = "https://api.cursorai.art/v1/chat/completions"
    api_key: str = ""
    model: str = "gpt-5.4"
    temperature: float = 0.3
    max_workers: int = 8
    retries: int = 3
    timeout: int = 120
    batch_size: int = 5


@dataclass
class StorageConfig:
    data_dir: str = "data"

    @property
    def data_path(self) -> Path:
        p = Path(self.data_dir)
        if not p.is_absolute():
            p = _PROJECT_ROOT / p
        return p


@dataclass
class AppConfig:
    arxiv: ArxivConfig = field(default_factory=ArxivConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


def load_config(config_path: str | Path | None = None) -> AppConfig:
    path = Path(config_path) if config_path else _DEFAULT_CONFIG
    raw = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

    cfg = AppConfig(
        arxiv=ArxivConfig(**raw.get("arxiv", {})),
        llm=LLMConfig(**raw.get("llm", {})),
        storage=StorageConfig(**raw.get("storage", {})),
    )

    # 环境变量覆盖
    env_map = {
        "PAPER_SEARCHER_LLM_API_KEY": ("llm", "api_key"),
        "PAPER_SEARCHER_LLM_API_URL": ("llm", "api_url"),
        "PAPER_SEARCHER_LLM_MODEL": ("llm", "model"),
        "PAPER_SEARCHER_DATA_DIR": ("storage", "data_dir"),
    }
    for env_var, (section, key) in env_map.items():
        val = os.environ.get(env_var)
        if val:
            setattr(getattr(cfg, section), key, val)

    return cfg
