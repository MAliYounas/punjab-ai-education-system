import json
import httpx
from ..config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    HAS_LLM,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
)

SYSTEM = (
    "You are the curriculum engine of the Punjab Education Intelligence Platform. "
    "You may ONLY use the provided curriculum excerpts. "
    "If the excerpts do not contain the answer, say that the approved curriculum does not cover it. "
    "Every factual claim must stay faithful to the source. "
    "Return compact JSON when asked. Age-appropriate for Grades 1–10. "
    "Do not invent SLOs, page numbers, or facts that are not grounded."
)


def llm_available() -> bool:
    return HAS_LLM


def complete(prompt: str, context: str, json_mode: bool = False) -> str | None:
    if not HAS_LLM:
        return None
    user = f"CURRICULUM EXCERPTS:\n{context}\n\nTASK:\n{prompt}"
    if OPENAI_API_KEY:
        return _openai(user, json_mode)
    if GEMINI_API_KEY:
        return _gemini(user)
    return None


def _openai(user: str, json_mode: bool) -> str | None:
    payload = {
        "model": OPENAI_MODEL,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    try:
        r = httpx.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return None


def _gemini(user: str) -> str | None:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.2},
    }
    try:
        r = httpx.post(url, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None


def parse_json(text: str | None):
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                return None
    return None
