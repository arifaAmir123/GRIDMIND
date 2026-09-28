from fastapi import APIRouter
from pydantic import BaseModel

from ai.analyst import analyze_question


router = APIRouter()


class QuestionRequest(BaseModel):

    question: str


@router.post("/ask")
def ask_gridmind(
    request: QuestionRequest
):

    return analyze_question(
        request.question
    )