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
from sqlalchemy import and_
from collections import defaultdict




router = APIRouter(prefix="/profile",tags=["profile"])

@router.get("/{user_id}")
async def get_profile(user_id:int , db:db_dependency):

    user=db.query(models.Users).filter(models.Users.id==user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    #filter all quizes of attemp by user
    db_quizes=db.query(models.Quizes).filter(and_(
                        models.Quizes.owner_id == user_id,
                        models.Quizes.state.in_([1, 3])
                    )).all()
  
    if db_quizes is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    #Quiz count per day
    db_quiz = db.query(models.Quizes).filter(models.Quizes.owner_id == user_id).all()
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quizdate_counts = defaultdict(int)
    for quiz in db_quiz:
        date_only = quiz.created_at.date().isoformat() 
        quizdate_counts[date_only] += 1
    quiz_result = [{"date": date, "count": count} for date, count in quizdate_counts.items()]


    # Suggestion count per day
    db_suggestion = db.query(models.Suggestions).filter(models.Suggestions.owner_id == user_id).all()
    if db_suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    suggestiondate_counts = defaultdict(int)
    for suggestion in db_suggestion:
        date_only = suggestion.created_at.date().isoformat() 
        suggestiondate_counts[date_only] += 1
    suggest_result = [{"date": date, "count": count} for date, count in suggestiondate_counts.items()]

    #Convo count per day
    db_convo = db.query(models.Conversations).filter(models.Conversations.user_id == user_id).all()
    if db_convo is None:
        raise HTTPException(status_code=404, detail="Convo not found")
    convo_counts = defaultdict(int)
    isFree = 0
    isAdvance = 0
    for convo in db_convo:
        date_only = convo.created_at.date().isoformat() 
        if convo.isFree:
            isFree = isFree+1
        else:
            isAdvance = isAdvance+1
        convo_counts[date_only] += 1
    convo_Count= [{"date": date, "count": count } for date, count in convo_counts.items()]
    convo_result = {
        "isFree" : isFree,
        "isAdvance":isAdvance,
        "count" : convo_Count
    }

    #Lecture count per day
    db_lecture = db.query(models.Lectures).filter(models.Lectures.owner_id == user_id).all()
    if db_lecture is None:
        raise HTTPException(status_code=404, detail="Lecture not found")
    lecture_counts = defaultdict(int)
    for lecture in db_lecture:
        date_only = lecture.created_at.date().isoformat() 
        lecture_counts[date_only] += 1
    lecture_result = [{"date": date, "count": count} for date, count in lecture_counts.items()]

    #response
    return {"user": user, "quizzes": db_quizes, "suggestions":suggest_result, "convo":convo_result, "lecture":lecture_result, "quiz": quiz_result}


