# llm.py
"""
Ollama API client for Markdown校閲ツール.
Sends prompt and returns revised text.
"""
import requests
from typing import Optional

def call_ollama(prompt: str, model: str, url: str, temperature: float = 0.2, timeout: int = 60) -> Optional[str]:
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get('response')
    except Exception as e:
        print(f"[Ollama API error] {e}")
        return None
