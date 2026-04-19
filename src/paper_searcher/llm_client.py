import json
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    usage: dict


class LLMClient:
    def __init__(self, api_url: str, api_key: str, model: str,
                 temperature: float = 0.3, max_workers: int = 8,
                 retries: int = 3, timeout: int = 120):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_workers = max_workers
        self.retries = retries
        self.timeout = timeout

    def call(self, prompt: str, system: str | None = None) -> LLMResponse | None:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        for attempt in range(self.retries + 1):
            try:
                resp = requests.post(self.api_url, headers=headers,
                                     json=payload, timeout=self.timeout)
                if resp.status_code != 200:
                    if attempt < self.retries:
                        time.sleep(3 * (attempt + 1))
                        continue
                    return None

                data = resp.json()
                usage = data.get("usage", {})
                content = data["choices"][0]["message"]["content"]
                return LLMResponse(content=content, usage=usage)

            except (requests.exceptions.RequestException, KeyError, IndexError):
                if attempt < self.retries:
                    time.sleep(3 * (attempt + 1))
                    continue
                return None

        return None

    def call_batch(self, prompts: list[str], system: str | None = None) -> list[LLMResponse | None]:
        results = [None] * len(prompts)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.call, p, system): i
                for i, p in enumerate(prompts)
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception:
                    pass
        return results

    @staticmethod
    def extract_json(text: str):
        cleaned = text.replace("```json", "").replace("```", "").strip()
        match = re.search(r"[\[{].*[}\]]", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(cleaned)
