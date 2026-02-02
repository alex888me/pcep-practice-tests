from pathlib import Path
from typing import Any, List

import yaml
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "test_objects.yaml"

app = FastAPI()

templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


def load_questions() -> List[dict[str, Any]]:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or []


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    questions = load_questions()
    question = questions[0] if questions else {}
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "question": question,
            "question_index": 0,
        },
    )


@app.post("/check", response_class=HTMLResponse)
async def check_answer(
    request: Request,
    question_index: int = Form(...),
    selected: list[int] = Form(...),
) -> HTMLResponse:
    questions = load_questions()
    question = questions[question_index]
    answers = question.get("answers", [])
    is_correct = sorted(selected) == sorted(answers)

    correct_labels = [question["options"][idx] for idx in answers]

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "is_correct": is_correct,
            "correct_labels": correct_labels,
            "question_index": question_index,
        },
    )


@app.get("/next", response_class=HTMLResponse)
async def next_question(request: Request, index: int) -> HTMLResponse:
    questions = load_questions()
    if not questions:
        question = {}
        question_index = 0
    else:
        question_index = (index + 1) % len(questions)
        question = questions[question_index]

    return templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "question": question,
            "question_index": question_index,
        },
    )


@app.get("/previous", response_class=HTMLResponse)
async def previous_question(request: Request, index: int) -> HTMLResponse:
    questions = load_questions()
    if not questions:
        question = {}
        question_index = 0
    else:
        question_index = (index - 1) % len(questions)
        question = questions[question_index]

    return templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "question": question,
            "question_index": question_index,
        },
    )
