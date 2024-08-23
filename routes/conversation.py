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


router = APIRouter(prefix="/conversation",tags=["conversation"])

@router.post("/create")
async def create_conversation(conversation: requestModels.createConversationRequest, db: db_dependency):
    user = db.query(models.Users).filter(models.Users.id == conversation.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conversation = models.Conversations(name=conversation.name, 
                                           description='', 
                                           user_id=conversation.user_id, 
                                           isFree=conversation.isFree, 
                                           isAdvanced=conversation.isAdvanced, 
                                           isTeacher=conversation.isTeacher,
                                           created_at=datetime.now(),
                                           updated_at=datetime.now())
    
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation
    
@router.post("/{conversation_id}/addTurn")
async def add_turn(turn: requestModels.createTurnRequest, conversation_id: int, db: db_dependency):
    conversation = db.query(models.Conversations).filter(models.Conversations.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # at first create the turn 
    db_turn = models.Turns(sender=turn.sender, conversation_id=conversation_id,created_at=datetime.now())
    db.add(db_turn)
    db.commit()
    db.refresh(db_turn)
    # then create the messages
    for message in turn.messages:
        db_message = models.Messages(message_type=message.message_type, message=message.message, turn_id=db_turn.id,created_at=datetime.now())
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
    
    return db_turn

@router.get("/{conversation_id}/getTurns")
async def get_turns(conversation_id: int, db: db_dependency):
    conversation = db.query(models.Conversations).filter(models.Conversations.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    turns = db.query(models.Turns).filter(models.Turns.conversation_id == conversation_id).all()
    return turns

@router.get("/getMessages/{turn_id}")
async def get_messages(turn_id: int, db: db_dependency):
    turn = db.query(models.Turns).filter(models.Turns.id == turn_id).first()
    if turn is None:
        raise HTTPException(status_code=404, detail="Turn not found")
    messages = db.query(models.Messages).filter(models.Messages.turn_id == turn_id).all()
    return messages


@router.get("/{conversation_id}/show")
async def show_conversation(conversation_id: int, db: db_dependency):
    conversation = db.query(models.Conversations).filter(models.Conversations.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    turns = db.query(models.Turns).filter(models.Turns.conversation_id == conversation_id).all()
    conversation_dict = {"conversation": conversation, "turns": []}
    for turn in turns:
        messages = db.query(models.Messages).filter(models.Messages.turn_id == turn.id).all()
        turn_dict = {"turn": turn, "messages": messages}
        conversation_dict["turns"].append(turn_dict)
    return conversation_dict



@router.get("/{user_id}/get_normal")
async def get_my_conversations(user_id:int,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # get all conversations of the user sorted decendingly by the updating date and only conversations where isteacher is false
    conversations = db.query(models.Conversations).filter(models.Conversations.user_id == user_id, models.Conversations.isTeacher == False).order_by(models.Conversations.updated_at.desc()).all()
    return conversations

@router.get("/{user_id}/get_teacher")
async def get_my_teacher_conversations(user_id:int,db:db_dependency):
    user=db.query(models.Users).filter(models.Users.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # get all conversations of the user sorted decendingly by the updating date and only conversations where isteacher is true
    conversations = db.query(models.Conversations).filter(models.Conversations.user_id == user_id, models.Conversations.isTeacher == True).order_by(models.Conversations.updated_at.desc()).all()
    return conversations



# delete conversation
@router.delete("/{conversation_id}/delete")
async def delete_conversation(conversation_id: int, db: db_dependency):
    conversation = db.query(models.Conversations).filter(models.Conversations.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation deleted successfully"}


# highlight conversation
@router.put("/{conversation_id}/highlight")
async def highlight_conversation(conversation_id: int, db: db_dependency):
    conversation = db.query(models.Conversations).filter(models.Conversations.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.isHighlighted:
        conversation.isHighlighted = False
    else:
        conversation.isHighlighted = True
    db.commit()
    db.refresh(conversation)
    return conversation