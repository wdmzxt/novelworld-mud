from typing import Any


def get_text(value: Any, lang: str) -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("zh") or value.get("en") or "")
    if value is None:
        return ""
    return str(value)


def match_entity_by_name(input_text: str, entities: dict[str, dict[str, Any]], lang: str) -> str | None:
    normalized_input = _normalize_match_text(input_text)
    if not normalized_input:
        return None

    for entity_id, entity in entities.items():
        name = entity.get("name", "")
        candidates = [get_text(name, lang)]
        if isinstance(name, dict):
            candidates.extend(str(text) for text in name.values())
        candidates.append(entity_id)

        for candidate in candidates:
            if _normalize_match_text(candidate) == normalized_input:
                return entity_id

    return None


def normalize_language(input_text: str) -> str:
    value = input_text.strip().lower()
    if value in {"2", "en", "english"}:
        return "en"
    if value in {"1", "zh", "中文", "chinese"}:
        return "zh"
    return "zh"


def _normalize_match_text(value: str) -> str:
    return " ".join(value.strip().casefold().split())
