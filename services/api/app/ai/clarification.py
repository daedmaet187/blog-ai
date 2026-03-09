from dataclasses import dataclass


@dataclass(frozen=True)
class ClarificationQuestionTemplate:
    key: str
    question: str
    keywords: tuple[str, ...]


QUESTION_TEMPLATES: tuple[ClarificationQuestionTemplate, ...] = (
    ClarificationQuestionTemplate(
        key="goal",
        question="What is the single primary goal of this landing page?",
        keywords=("goal", "convert", "conversion", "lead", "signup", "book"),
    ),
    ClarificationQuestionTemplate(
        key="audience",
        question="Who is the exact target audience for this page?",
        keywords=("audience", "customer", "client", "patients", "saudi", "iraq", "students"),
    ),
    ClarificationQuestionTemplate(
        key="cta",
        question="What should be the main call-to-action button text?",
        keywords=("call to action", "cta", "book now", "start now", "contact", "whatsapp"),
    ),
)


def generate_clarification_questions(*, title: str, brief_en: str, brief_ar: str) -> list[dict[str, str]]:
    text = f"{title} {brief_en} {brief_ar}".lower()
    questions: list[dict[str, str]] = []

    for template in QUESTION_TEMPLATES:
        if not any(keyword in text for keyword in template.keywords):
            questions.append({"key": template.key, "question": template.question})

    return questions


def is_clarification_complete(answered_keys: set[str]) -> bool:
    required_keys = {template.key for template in QUESTION_TEMPLATES}
    return required_keys.issubset(answered_keys)
