import os
import random
from app.curriculum import get_subjects

QUESTION_TEMPLATES = [
    "کدام گزینه در ارتباط با «{topic}» در درس {subject} صحیح است؟",
    "مفهوم «{topic}» در درس {subject} به کدام مورد اشاره دارد؟",
    "در بررسی «{topic}» ({subject})، کدام گزینه نادرست است؟",
    "کدام یک از موارد زیر جزو نکات کلیدی «{topic}» در {subject} محسوب می‌شود؟",
]

CORRECT_PATTERNS = [
    "بیانی دقیق و منطبق با تعریف اصلی «{topic}»",
    "کاربرد صحیح مفهوم «{topic}» در حل مسئله",
    "ارتباط درست «{topic}» با سایر مباحث درس {subject}",
]

DISTRACTOR_PATTERNS = [
    "بیانی نادرست و متناقض با تعریف «{topic}»",
    "مفهومی نامرتبط با «{topic}»",
    "برداشت اشتباه رایج درباره «{topic}»",
    "تعریفی مربوط به مبحث دیگری از درس {subject}",
]


def _fallback_topics(subject_name):
    return ["مفاهیم پایه", "نکات تستی مهم", "کاربردهای درس", "جمع‌بندی فصل"]


def _generate_rule_based_quiz(subject, lesson, grade, question_count):
    topics = None
    for f in ["دهم", "یازدهم", "دوازدهم"]:
        for field_subjects in get_subjects(f, "ریاضی فیزیک") + get_subjects(f, "علوم تجربی") + get_subjects(f, "علوم انسانی"):
            if field_subjects["name"] == subject or subject in field_subjects["name"]:
                topics = field_subjects.get("topics")
                break
        if topics:
            break
    if not topics:
        topics = _fallback_topics(subject)

    questions = []
    for i in range(question_count):
        topic = topics[i % len(topics)]
        template = random.choice(QUESTION_TEMPLATES)
        question_text = template.format(topic=topic, subject=subject)

        correct_text = random.choice(CORRECT_PATTERNS).format(topic=topic, subject=subject)
        distractors = random.sample(DISTRACTOR_PATTERNS, 3)
        options_texts = [correct_text] + [d.format(topic=topic, subject=subject) for d in distractors]

        correct_index = 0
        indices = list(range(4))
        random.shuffle(indices)
        shuffled_options = [None] * 4
        new_correct_index = 0
        for pos, orig_idx in enumerate(indices):
            shuffled_options[pos] = options_texts[orig_idx]
            if orig_idx == correct_index:
                new_correct_index = pos

        questions.append({
            "id": i + 1,
            "question": question_text,
            "options": shuffled_options,
            "correct_index": new_correct_index,
            "topic": topic,
        })

    return {
        "subject": subject,
        "lesson": lesson or subject,
        "grade": grade,
        "question_count": question_count,
        "engine": "rule_based",
        "questions": questions,
    }


def _try_real_ai_quiz(subject, lesson, grade, question_count, fallback):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return fallback
    try:
        import anthropic
        import json as _json
        client = anthropic.Anthropic(api_key=api_key)
        prompt = (
            f"شما طراح سوالات کنکور ایران هستید. برای درس «{subject}» پایه {grade} "
            f"({lesson or subject})، دقیقاً {question_count} سوال تستی چهارگزینه‌ای در سطح کنکور سراسری طراحی کن. "
            "خروجی را فقط به صورت JSON خالص (بدون هیچ متن اضافه یا Markdown) با این ساختار بده:\n"
            '[{"question": "متن سوال", "options": ["گزینه۱","گزینه۲","گزینه۳","گزینه۴"], "correct_index": 0}]'
        )
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = _json.loads(text)
        questions = []
        for i, q in enumerate(parsed[:question_count]):
            questions.append({
                "id": i + 1,
                "question": q["question"],
                "options": q["options"],
                "correct_index": q["correct_index"],
                "topic": lesson or subject,
            })
        if not questions:
            return fallback
        return {
            "subject": subject, "lesson": lesson or subject, "grade": grade,
            "question_count": len(questions), "engine": "anthropic_ai", "questions": questions,
        }
    except Exception:
        return fallback


def generate_quiz(subject, lesson, grade, question_count=10):
    question_count = max(1, min(question_count, 30))
    base = _generate_rule_based_quiz(subject, lesson, grade, question_count)
    return _try_real_ai_quiz(subject, lesson, grade, question_count, base)
