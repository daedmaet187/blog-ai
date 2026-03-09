import re
from collections.abc import Iterable

from ..schemas import ModerationDecision, ModerationReasonCode, ModerationResult

DEFAULT_BLOCKED_WORDS = {
    "damn",
    "shit",
    "fuck",
}
MAX_LINKS = 3
MAX_MEDIA = 4

_LINK_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
_MEDIA_RE = re.compile(r"!\[[^\]]*\]\([^\)]+\)|<img\b[^>]*>", re.IGNORECASE)
_WORD_RE = re.compile(r"\b[a-zA-Z']+\b")
_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    return _WHITESPACE_RE.sub(" ", lowered)


def evaluate_content(
    content: str,
    existing_contents: Iterable[str],
    blocked_words: set[str] | None = None,
) -> ModerationResult:
    rules_blocked_words = {w.lower() for w in (blocked_words or DEFAULT_BLOCKED_WORDS)}
    reasons: list[ModerationReasonCode] = []

    words = {w.lower() for w in _WORD_RE.findall(content)}
    if rules_blocked_words.intersection(words):
        reasons.append(ModerationReasonCode.BLOCKED_WORD)

    link_count = len(_LINK_RE.findall(content))
    if link_count > MAX_LINKS:
        reasons.append(ModerationReasonCode.TOO_MANY_LINKS)

    normalized = _normalize_text(content)
    for existing_content in existing_contents:
        if normalized and normalized == _normalize_text(existing_content):
            reasons.append(ModerationReasonCode.DUPLICATE_CONTENT)
            break

    media_count = len(_MEDIA_RE.findall(content))
    if media_count > MAX_MEDIA:
        reasons.append(ModerationReasonCode.TOO_MANY_MEDIA)

    decision = ModerationDecision.FLAG if reasons else ModerationDecision.PASS
    return ModerationResult(decision=decision, reasons=reasons)
