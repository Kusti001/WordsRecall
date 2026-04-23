import asyncio
import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

from ..schemas.Word import WordAdd

DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "")


def _extract_json_block(text: str) -> Optional[str]:
    text = text.strip()
    if not text:
        return None

    # Попытка сразу распарсить текст как JSON.
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Извлекаем первый JSON-объект из текста.
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    return match.group(0)


def _ollama_predict(model_name: str, prompt: str, timeout: int = 60) -> str:
    if not model_name:
        raise ValueError("Model name is required for Ollama enrichment. Set OLLAMA_MODEL or pass model_name explicitly.")

    command = ["ollama", "predict", model_name, prompt]

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if process.returncode != 0:
        raise RuntimeError(
            f"Ollama returned exit code {process.returncode}: {process.stderr.strip() or process.stdout.strip()}"
        )

    return process.stdout.strip()


def _parse_ollama_response(output: str) -> Dict[str, str]:
    json_text = _extract_json_block(output)
    if not json_text:
        raise ValueError(f"Не удалось разобрать JSON из ответа Ollama: {output}")

    parsed = json.loads(json_text)
    return {
        "meaning": str(parsed.get("meaning", "")).strip(),
        "example": str(parsed.get("example", "")).strip(),
        "translation": str(parsed.get("translation", "")).strip(),
    }


def _build_enrichment_prompt(word: str, level: Optional[str], meaning: Optional[str], example: Optional[str], extra: Dict[str, Any]) -> str:
    examples = extra.get("examples") or []
    examples_text = "\n".join(f"- {item}" for item in examples if isinstance(item, str))

    prompt = f"""
Ты — помощник по изучению английских слов.
На входе:
- слово: {word}
- уровень: {level or 'неизвестен'}
- исходное значение: {meaning or 'нет данных'}
- пример: {example or 'нет данных'}
- дополнительные примеры:
{examples_text}

Ответь только JSON в формате:
{{
  "meaning": "short English definition of the word",
  "example": "one short English sentence using the word",
  "translation": "русский перевод слова"
}}

Если слово уже понятно, постарайся дать точный английский definition, английский example и русский translation.
Не добавляй комментариев, не помечай ответ как JSON, просто верни объект.
"""
    return prompt


def parse_oxford_json_dictionary(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []

    for item in entries:
        value = item.get("value")
        if not isinstance(value, dict):
            continue

        word_text = value.get("word")
        if not word_text or not isinstance(word_text, str):
            continue

        level = value.get("level") or value.get("type")
        if isinstance(level, str):
            level = level
        else:
            level = "unknown"

        examples = value.get("examples")
        example = None
        if isinstance(examples, list):
            for maybe_example in examples:
                if isinstance(maybe_example, str):
                    example = maybe_example
                    break

        parsed.append(
            {
                "word": word_text.strip(),
                "level": str(level).strip() if level else "unknown",
                "meaning": value.get("type") if isinstance(value.get("type"), str) else None,
                "example": example,
                "translation": "",
                "extra": {
                    "href": value.get("href"),
                    "phonetics": value.get("phonetics"),
                    "type": value.get("type"),
                    "examples": examples if isinstance(examples, list) else [],
                },
            }
        )

    return parsed


def _enrich_entry(entry: Dict[str, Any], model_name: str) -> WordAdd:
    prompt = _build_enrichment_prompt(
        word=entry["word"],
        level=entry.get("level"),
        meaning=entry.get("meaning"),
        example=entry.get("example"),
        extra=entry.get("extra", {}),
    )

    output = _ollama_predict(model_name, prompt)
    enriched = _parse_ollama_response(output)

    return WordAdd(
        word=entry["word"],
        level=str(entry.get("level") or "unknown"),
        meaning=enriched["meaning"] or str(entry.get("meaning") or ""),
        example=enriched["example"] or str(entry.get("example") or ""),
        translation=enriched["translation"],
    )


async def enrich_dictionary_entries(entries: List[Dict[str, Any]], model_name: Optional[str] = None) -> List[WordAdd]:
    model_name = model_name or DEFAULT_OLLAMA_MODEL
    if not model_name:
        raise ValueError(
            "Не указан локальный модель Ollama. Установите переменную OLLAMA_MODEL или передайте model_name явно."
        )

    parsed = parse_oxford_json_dictionary(entries)
    tasks = [asyncio.to_thread(_enrich_entry, item, model_name) for item in parsed]
    return await asyncio.gather(*tasks)


async def enrich_word_text(word_text: str, model_name: Optional[str] = None) -> WordAdd:
    model_name = model_name or DEFAULT_OLLAMA_MODEL
    if not model_name:
        raise ValueError(
            "Не указан локальный модель Ollama. Установите переменную OLLAMA_MODEL или передайте model_name явно."
        )

    prompt = _build_enrichment_prompt(
        word=word_text,
        level=None,
        meaning=None,
        example=None,
        extra={},
    )

    output = await asyncio.to_thread(_ollama_predict, model_name, prompt)
    enriched = _parse_ollama_response(output)

    return WordAdd(
        word=word_text,
        level="unknown",
        meaning=enriched["meaning"],
        example=enriched["example"],
        translation=enriched["translation"],
    )
