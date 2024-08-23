from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import dataStruct.models as models
import dataStruct.requestModels as requestModels
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from database import db_dependency


router = APIRouter(prefix="/lecture",tags=["lecture"])





#show a lecture with lecture answers and question untill the precious question of the current question
# the current question is the question that the user is currently answering so only the question will be delivered
# the whole lecture is delivered as list of messages.

@router.get("/{lecture_id}/show")
async def show_lecture(lecture_id: int, db: db_dependency):
    lecture = db.query(models.Lectures).filter(models.Lectures.id == lecture_id).first()
    if lecture is None:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    lecture_questions = db.query(models.LectureQuestions).filter(models.LectureQuestions.lecture_id == lecture_id).all()
    # only return previous questions of current question
    #lecture_questions = [q for q in lecture_questions if q.serial_no <= lecture.current_question]
    return {"lecture": lecture, "questions": lecture_questions}


# starr a lecture
@router.post("/{lecture_id}/toggleStarred")
async def starred_lecture(lecture_id: int, db: db_dependency):
    lecture = db.query(models.Lectures).filter(models.Lectures.id == lecture_id).first()
    if lecture is None:
        raise HTTPException(status_code=404, detail="Lecture not found")
    if lecture.isStarred:
        lecture.isStarred=False
    else:
        lecture.isStarred=True
    db.commit()
    db.refresh(lecture)
    return lecture


# get my lectures
@router.get("/{user_id}/get_all")
async def get_my_lectures(user_id:int,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    lectures=db.query(models.Lectures).filter(models.Lectures.owner_id==user_id).all()
    return lectures


# delete lecture
@router.delete("/{lecture_id}/delete")
async def delete_lecture(lecture_id: int, db: db_dependency):
    lecture = db.query(models.Lectures).filter(models.Lectures.id == lecture_id).first()
    if lecture is None:
        raise HTTPException(status_code=404, detail="Lecture not found")
    db.delete(lecture)
    db.commit()
    return {"message":"Lecture deleted successfully"}




    





