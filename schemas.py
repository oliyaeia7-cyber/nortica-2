from pydantic import BaseModel, Field
from typing import List, Optional


class UserCreate(BaseModel):
    full_name: str
    phone: str
    field: str
    grade: str
    target_major: Optional[str] = ""
    target_university: Optional[str] = ""
    daily_hours: float = 2.0


class CustomLesson(BaseModel):
    name: str
    topics: Optional[List[str]] = []


class PlanRequest(BaseModel):
    user_id: int
    plan_type: str = Field(default="week")  # week / month / six_month / year
    custom_lessons: Optional[List[CustomLesson]] = []


class StudyLogCreate(BaseModel):
    user_id: int
    hours: float
    subject: Optional[str] = ""


class QuizRequest(BaseModel):
    user_id: int
    subject: str
    lesson: Optional[str] = ""
    grade: str
    question_count: int = 10


class QuizSubmit(BaseModel):
    user_id: int
    subject: str
    lesson: Optional[str] = ""
    answers: List[int]          # اندیس گزینه انتخابی کاربر برای هر سوال
    correct_answers: List[int]  # اندیس گزینه صحیح (از سمت کلاینت برگردانده می‌شود)


class SupportCreate(BaseModel):
    name: str
    phone: str
    subject: str
    message: str


class SubscribeRequest(BaseModel):
    user_id: int
    plan_id: str
