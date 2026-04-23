import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

import requests



DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
DEFAULT_API_URL = "http://127.0.0.1:8000/words"


def _extract_json_block(text: str) -> Optional[str]:
    text = text.strip()
    if not text:
        return None

    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    return match.group(0)


def _ollama_predict(model_name: str, prompt: str, timeout: int = 60) -> str:
    if not model_name:
        raise ValueError("Ollama model name is required. Set OLLAMA_MODEL or pass --model.")

    url = "http://localhost:11434/api/generate"
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(url, json=data, timeout=timeout)
    response.raise_for_status()

    result = response.json()
    return result.get("response", "").strip()


def _parse_ollama_response(output: str) -> Dict[str, str]:
    json_text = _extract_json_block(output)
    if not json_text:
        raise ValueError(f"Cannot parse JSON from Ollama output: {output}")

    parsed = json.loads(json_text)
    return {
        "meaning": str(parsed.get("meaning", "")).strip(),
        "example": str(parsed.get("example", "")).strip(),
        "translation": str(parsed.get("translation", "")).strip(),
    }


def _build_prompt(word: str, level: str, meaning: str, example: str, examples: List[str]) -> str:
    extra_examples = "\n".join(f"- {item}" for item in examples if item)
    if not extra_examples:
        extra_examples = "- none"

    prompt = f"""
You are an English vocabulary enrichment assistant.
Input:
- word: {word}
- level: {level or 'unknown'}
- source meaning: {meaning or 'none'}
- source example: {example or 'none'}
- additional examples:
{extra_examples}

Return only JSON with these keys:
{{
  "meaning": "short English definition of the word",
  "example": "one short English sentence using the word",
  "translation": "Russian translation of the word"
}}

Do not add extra keys, comments, or explanation. Do not wrap the JSON in markdown.
"""
    return prompt


def parse_dictionary(entries: Any) -> List[Dict[str, Any]]:
    if not isinstance(entries, list):
        raise ValueError("Input JSON must be a list of dictionary entries.")

    parsed: List[Dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue

        value = item.get("value")
        if not isinstance(value, dict):
            continue

        word = value.get("word")
        if not isinstance(word, str) or not word.strip():
            continue

        level = value.get("level") or value.get("type") or "unknown"
        if not isinstance(level, str):
            level = str(level)

        meaning = value.get("type") if isinstance(value.get("type"), str) else ""

        examples = []
        raw_examples = value.get("examples")
        if isinstance(raw_examples, list):
            for ex in raw_examples:
                if isinstance(ex, str) and ex.strip():
                    examples.append(ex.strip())

        example = examples[0] if examples else ""

        parsed.append(
            {
                "word": word.strip(),
                "level": level.strip(),
                "meaning": meaning.strip(),
                "example": example,
                "examples": examples,
            }
        )

    return parsed


def enrich_entry(entry: Dict[str, Any], model_name: str) -> Dict[str, str]:
    prompt = _build_prompt(
        word=entry["word"],
        level=entry.get("level", "unknown"),
        meaning=entry.get("meaning", ""),
        example=entry.get("example", ""),
        examples=entry.get("examples", []),
    )

    output = _ollama_predict(model_name, prompt)
    enriched = _parse_ollama_response(output)

    return {
        "word": entry["word"],
        "level": entry.get("level", "unknown"),
        "meaning": enriched["meaning"],
        "example": enriched["example"],
        "translation": enriched["translation"],
    }


def post_word(endpoint: str, payload: Dict[str, str]) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Oxford-style JSON, enrich with Ollama, and POST each word to FastAPI create_word endpoint."
    )
    parser.add_argument("json_file", help="Path to the JSON dictionary file.")
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_API_URL,
        help="FastAPI create_word endpoint URL.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Local Ollama model name. Can also be set via OLLAMA_MODEL env var.",
    )
    args = parser.parse_args()

    model_name = args.model or DEFAULT_OLLAMA_MODEL
    if not model_name:
        print("Error: Ollama model name is required. Set --model or OLLAMA_MODEL.", file=sys.stderr)
        return 1

    try:
        with open(args.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"Failed to load JSON file: {exc}", file=sys.stderr)
        return 1

    entries = parse_dictionary(data)
    if not entries:
        print("No valid entries parsed from JSON.", file=sys.stderr)
        return 1

    success = 0
    for index, entry in enumerate(entries, start=1):
        try:
            enriched = enrich_entry(entry, model_name)
            response = post_word(args.endpoint, enriched)
            print(f"[{index}/{len(entries)}] {enriched['word']} -> {response}")
            success += 1
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(errors="ignore") if exc.fp else ""
            print(f"[{index}/{len(entries)}] HTTP error {exc.code}: {error_body}", file=sys.stderr)
        except Exception as exc:
            print(f"[{index}/{len(entries)}] failed: {exc}", file=sys.stderr)

    print(f"Imported {success} of {len(entries)} entries.")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
