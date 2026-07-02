from sqlalchemy.orm import Session
from app.models.prescreening_question_model import PrescreeningQuestion
from typing import List, Optional

def get_all_prescreen_questions(db: Session) -> List[PrescreeningQuestion]:
    """Retrieve all prescreening questions from the library."""
    return db.query(PrescreeningQuestion).order_by(PrescreeningQuestion.id.desc()).all()

def create_prescreen_question(db: Session, question_text: str, admin_id: int) -> PrescreeningQuestion:
    """Create a new prescreening question."""
    new_question = PrescreeningQuestion(
        questions=question_text,
        created_by=admin_id,
        updated_by=admin_id
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

def update_prescreen_question(db: Session, question_id: int, new_text: str, admin_id: int) -> Optional[PrescreeningQuestion]:
    """Update an existing prescreening question."""
    question = db.query(PrescreeningQuestion).filter(PrescreeningQuestion.id == question_id).first()
    if question:
        question.questions = new_text
        question.updated_by = admin_id
        db.commit()
        db.refresh(question)
    return question

def delete_prescreen_question(db: Session, question_id: int) -> bool:
    """Delete a prescreening question."""
    question = db.query(PrescreeningQuestion).filter(PrescreeningQuestion.id == question_id).first()
    if question:
        db.delete(question)
        db.commit()
        return True
    return False
