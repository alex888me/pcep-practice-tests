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
ANSWERS: dict[int, dict[str, Any]] = {}


def load_questions() -> List[dict[str, Any]]:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or []


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    ANSWERS.clear()
    questions = load_questions()
    question = questions[0] if questions else {}
    is_last = len(questions) <= 1
    is_first = True
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "question": question,
            "question_index": 0,
            "answered": ANSWERS.get(0),
            "is_last": is_last,
            "is_first": is_first,
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
    ANSWERS[question_index] = {
        "selected": selected,
        "is_correct": is_correct,
        "correct_labels": correct_labels,
    }
    is_last = question_index == max(len(questions) - 1, 0)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "is_correct": is_correct,
            "correct_labels": correct_labels,
            "question_index": question_index,
            "oob_next": True,
            "is_last": is_last,
        },
    )


@app.get("/next", response_class=HTMLResponse)
async def next_question(request: Request, index: int) -> HTMLResponse:
    questions = load_questions()
    if not questions:
        question = {}
        question_index = 0
        answered = None
        is_last = True
        is_first = True
    else:
        question_index = (index + 1) % len(questions)
        question = questions[question_index]
        answered = ANSWERS.get(question_index)
        is_last = question_index == len(questions) - 1
        is_first = question_index == 0

    return templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "question": question,
            "question_index": question_index,
            "answered": answered,
            "is_last": is_last,
            "is_first": is_first,
        },
    )


@app.get("/previous", response_class=HTMLResponse)
async def previous_question(request: Request, index: int) -> HTMLResponse:
    questions = load_questions()
    if not questions:
        question = {}
        question_index = 0
        answered = None
        is_last = True
        is_first = True
    else:
        question_index = (index - 1) % len(questions)
        question = questions[question_index]
        answered = ANSWERS.get(question_index)
        is_last = question_index == len(questions) - 1
        is_first = question_index == 0

    return templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "question": question,
            "question_index": question_index,
            "answered": answered,
            "is_last": is_last,
            "is_first": is_first,
        },
    )
