from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import dataStruct.models as models
import dataStruct.requestModels as requestModels
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from database import db_dependency


router = APIRouter(prefix="/suggestion",tags=["suggestion"])


# get operation.......................................................................................................................

@router.get("/{user_id}/get_all")
async def get_my_suggestions(user_id:int,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    suggestions=db.query(models.Suggestions).filter(models.Suggestions.owner_id==user_id).all()
    return suggestions

# update operations...................................................................................................................

@router.post("/highlight")
async def highlight_suggestion(request:requestModels.updateSuggestionRequest,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_suggestion=db.query(models.Suggestions).filter(models.Suggestions.id==request.suggestion_id).first()
    if db_suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # highlight if not
    if db_suggestion.state==1:
        db_suggestion.state=2
    elif db_suggestion.state==3:
        db_suggestion.state=4

    # unhighlight if highlighted
    elif db_suggestion.state==2:
        db_suggestion.state=1
    elif db_suggestion.state==4:
        db_suggestion.state=3
    
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


@router.post("/visit")
async def visit_suggestion(request:requestModels.updateSuggestionRequest,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_suggestion=db.query(models.Suggestions).filter(models.Suggestions.id==request.suggestion_id).first()
    if db_suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    

    if db_suggestion.state==1:
        db_suggestion.state=3
    elif db_suggestion.state==2:
        db_suggestion.state=4
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


@router.post("/delete")
async def delete_suggestion(request:requestModels.updateSuggestionRequest,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_suggestion=db.query(models.Suggestions).filter(models.Suggestions.id==request.suggestion_id).first()
    if db_suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    db.delete(db_suggestion)
    db.commit()
    return {"message":"suggestion deleted"}





    


