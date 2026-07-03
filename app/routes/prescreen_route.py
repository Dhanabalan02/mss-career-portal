from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.crud.prescreen_crud import (
    get_all_prescreen_questions,
    create_prescreen_question,
    update_prescreen_question,
    delete_prescreen_question
)
from app.routes.hr_route import get_current_admin_id

router = APIRouter(prefix="/prescreening", tags=["Prescreening Library"])

class PrescreenQuestionCreate(BaseModel):
    questions: str

class PrescreenQuestionResponse(BaseModel):
    id: int
    questions: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[PrescreenQuestionResponse])
def get_library_questions(db: Session = Depends(get_db)):
    """Fetch all pre-screening questions from the library."""
    questions = get_all_prescreen_questions(db)
    return questions

@router.post("/", response_model=PrescreenQuestionResponse)
def add_library_question(
    question_in: PrescreenQuestionCreate,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    """Add a new pre-screening question to the library."""
    if not question_in.questions.strip():
        raise HTTPException(status_code=400, detail="Question text cannot be empty.")
    return create_prescreen_question(db, question_in.questions, admin_id)

@router.put("/{question_id}", response_model=PrescreenQuestionResponse)
def edit_library_question(
    question_id: int,
    question_in: PrescreenQuestionCreate,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    """Update an existing pre-screening question."""
    if not question_in.questions.strip():
        raise HTTPException(status_code=400, detail="Question text cannot be empty.")
    question = update_prescreen_question(db, question_id, question_in.questions, admin_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.delete("/{question_id}")
def remove_library_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    """Delete a pre-screening question from the library."""
    success = delete_prescreen_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"detail": "Question deleted successfully"}
