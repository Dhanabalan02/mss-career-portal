import os
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.routes.hr_route import get_current_admin_id

router = APIRouter(prefix="/metadata", tags=["Metadata"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "mss-career-portal")

class SkillCreate(BaseModel):
    skill_name: str
    category: str = "Custom"

class EducationCreate(BaseModel):
    name: str

@router.post("/skills")
def add_skill(
    skill_in: SkillCreate,
    admin_id: int = Depends(get_current_admin_id)
):
    filepath = os.path.join(FRONTEND_DIR, "skills.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="skills.json not found")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read skills.json: {e}")

    skills = data.get("skills", [])
    
    skill_name_lower = skill_in.skill_name.strip().lower()
    for s in skills:
        if s.get("skill_name", "").strip().lower() == skill_name_lower:
            raise HTTPException(status_code=400, detail="Skill already exists in the library")

    max_id = max([s.get("id", 0) for s in skills]) if skills else 0
    new_id = max_id + 1

    new_skill = {
        "id": new_id,
        "category": skill_in.category,
        "skill_name": skill_in.skill_name
    }
    skills.append(new_skill)
    data["skills"] = skills

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write skills.json: {e}")

    return {"detail": "Skill added successfully", "skill": new_skill}


@router.post("/education")
def add_education(
    edu_in: EducationCreate,
    admin_id: int = Depends(get_current_admin_id)
):
    filepath = os.path.join(FRONTEND_DIR, "education.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="education.json not found")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read education.json: {e}")

    education_list = data.get("education", [])
    
    name_lower = edu_in.name.strip().lower()
    for e in education_list:
        if e.get("name", "").strip().lower() == name_lower:
            raise HTTPException(status_code=400, detail="Education qualification already exists in the library")

    max_id = max([e.get("id", 0) for e in education_list]) if education_list else 0
    new_id = max_id + 1

    new_edu = {
        "id": new_id,
        "name": edu_in.name
    }
    education_list.append(new_edu)
    data["education"] = education_list

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write education.json: {e}")

    return {"detail": "Education added successfully", "education": new_edu}
