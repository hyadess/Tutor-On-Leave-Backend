from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import List, Annotated
import dataStruct.models as models
import dataStruct.requestModels as requestModels
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from database import db_dependency



router = APIRouter(prefix="/quiz",tags=["quiz"])


@router.get("/{quiz_id}/show")
async def show_quiz(quiz_id: int, db: db_dependency):
    quiz = db.query(models.Quizes).filter(models.Quizes.id == quiz_id).first()
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    questions = db.query(models.QuizQuestions).filter(models.QuizQuestions.quiz_id == quiz_id).all()
    quiz_dict = {"Quiz": quiz, "Questions": []}
    for question in questions:
        options = db.query(models.QuizOptions).filter(models.QuizOptions.ques_id == question.id).all()
        question_dict = {"Question": question, "Options": options}
        quiz_dict["Questions"].append(question_dict)
    return quiz_dict

# get operation.......................................................................................................................

@router.get("/{user_id}/get_all")
async def get_my_quizes(user_id:int,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    quizes=db.query(models.Quizes).filter(models.Quizes.owner_id==user_id).all()
    return quizes


#update operations.................................................................................


@router.post("/highlight")
async def highlight_quiz(request:requestModels.updateQuizRequest,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_quiz=db.query(models.Quizes).filter(models.Quizes.id==request.quiz_id).first()
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    if db_quiz.state==1:
        db_quiz.state=3
    elif db_quiz.state==2:
        db_quiz.state=4
    elif db_quiz.state==3:
        db_quiz.state=1
    elif db_quiz.state==4:
        db_quiz.state=2
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


@router.post("/attempt")
async def attempt_quiz(request:requestModels.updateQuizScore,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_quiz=db.query(models.Quizes).filter(models.Quizes.id==request.quiz_id).first()
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    

    if db_quiz.state==2:
        db_quiz.state=1
    elif db_quiz.state==4:
        db_quiz.state=3
    db_quiz.score=request.score
    db_quiz.updated_at=datetime.now()
    db.commit()
    db.refresh(db_quiz)
    return db_quiz




