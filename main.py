from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401  -> ثبت مدل‌ها روی Base
from app.routers import users, plans, study, exams, leaderboard, support, subscription

Base.metadata.create_all(bind=engine)

app = FastAPI(title="نورتیکا | Noortika")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(users.router)
app.include_router(plans.router)
app.include_router(study.router)
app.include_router(exams.router)
app.include_router(leaderboard.router)
app.include_router(support.router)
app.include_router(subscription.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/plan")
def plan_page(request: Request):
    return templates.TemplateResponse("plan.html", {"request": request})


@app.get("/exam")
def exam_page(request: Request):
    return templates.TemplateResponse("exam.html", {"request": request})


@app.get("/leaderboard")
def leaderboard_page(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})


@app.get("/pricing")
def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})


@app.get("/support")
def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})
