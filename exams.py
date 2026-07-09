from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.ai_quiz import generate_quiz

router = APIRouter(prefix="/api/exams", tags=["exams"])


@router.post("/generate")
def create_quiz(payload: schemas.QuizRequest):
    quiz = generate_quiz(payload.subject, payload.lesson, payload.grade, payload.question_count)
    return {"quiz": quiz}


@router.post("/submit")
def submit_quiz(payload: schemas.QuizSubmit, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد.")

    if len(payload.answers) != len(payload.correct_answers):
        raise HTTPException(status_code=400, detail="داده‌های پاسخ نامعتبر است.")

    correct = sum(
        1 for a, c in zip(payload.answers, payload.correct_answers) if a == c
    )
    total = len(payload.correct_answers)
    score_percent = round((correct / total) * 100, 1) if total else 0.0

    result = models.ExamResult(
        user_id=payload.user_id,
        subject=payload.subject,
        lesson=payload.lesson,
        question_count=total,
        correct_count=correct,
        score_percent=score_percent,
    )
    db.add(result)
    db.commit()

    return {
        "correct_count": correct,
        "total": total,
        "score_percent": score_percent,
        "message": "کارنامه آزمون شما ثبت شد.",
    }
