from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

import openai
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal, get_db, db_dependency
from dataStruct.models import Conversations, Turns, Messages,Quizes,QuizQuestions,QuizOptions,Users,Suggestions,LectureQuestions,Lectures
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from chroma_db import get_chroma_db,Chroma
import os
import json
from dataStruct.requestModels import queryRequest,createTurnRequest,Message,createQuizRequest,createSuggestionRequest,createLectureRequest, checkAnswerRequest
from dotenv import load_dotenv
load_dotenv()



SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/test", tags=["test"])


# background tasks.................................................................


# at first, update the conversation................................................

def addToConversation(turn: createTurnRequest,db:db_dependency):
    conversation=db.query(Conversations).filter(Conversations.id==turn.conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # at first create the turn
    db_turn = Turns(sender=turn.sender, conversation_id=turn.conversation_id,created_at=datetime.now())
    db.add(db_turn)
    db.commit()
    db.refresh(db_turn)
    # then add the messages in db
    for i in turn.messages:
        db_message = Messages(message_type=i.message_type, message=i.message, turn_id=db_turn.id,created_at=datetime.now())
        db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_turn


def databaseAdding(conversation_id:int,userQuery:str,messages:list[Message],db:db_dependency):

    userTurn=createTurnRequest(sender="user",conversation_id=conversation_id,messages=[Message(message_type="text",message=userQuery)])
    addToConversation(userTurn,db)
    
    botTern=createTurnRequest(sender="system",conversation_id=conversation_id,messages=messages)
    addToConversation(botTern,db)

    print("conversation added to db")
    
# .......................................................................................

#then, summerize the conversation.....................................................



def summerize_conversation(conversation_id:int, messages:list[str],db:db_dependency):
    # text = " ".join(messages)
    # parser = PlaintextParser.from_string(text, Tokenizer("english"))
    # summarizer = LsaSummarizer()
    # summary = summarizer(parser.document, 6)
    # text=''
    # for sentence in summary:
    #     text+=str(sentence)
    # print(text)

    max_line=6
    summary=[]
    if len(messages)<=max_line:
        max_line=len(messages)
        summary.extend(messages)
    else:
        summary.extend(messages[-max_line:])

    text=" ".join(summary)
    db_convo=db.query(Conversations).filter(Conversations.id==conversation_id).first()
    db_convo.description=text
    db_convo.updated_at=datetime.now()
    db.commit()
    db.refresh(db_convo)
    print("conversation summerized")




def read_conversation(conversation_id:int,db:db_dependency):
    #want all the text messages form both user and system as a simple array
    conversation=db.query(Conversations).filter(Conversations.id==conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    turns = db.query(Turns).filter(Turns.conversation_id == conversation_id).all()
    messages=[]
    for turn in turns:
        #only retrieve message type of text and only add the message in the list
        dbMessages=db.query(Messages).filter(Messages.turn_id==turn.id).all()
        for i in dbMessages:
            if i.message_type=="text":
                messages.append(i.message)
    summerize_conversation(conversation_id,messages,db)


        
# .........................................................................................................................................


def generate_openai_response(prompt: str, question: str,conversation_id:int,db:db_dependency):
    openai.api_key = OPENAI_API_KEY
    db_convo=db.query(Conversations).filter(Conversations.id==conversation_id).first()
    messages = [
        {"role": "system", "content": "the following lines contains last couple previous conversations:\n"+db_convo.description+"\n\n"+"now,"+prompt},
        {"role": "user", "content": question},
    ]
    
    chat_completion = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    reply = chat_completion.choices[0].message.content
    return reply


@router.post("/query", status_code=status.HTTP_200_OK)
async def code(query: queryRequest,db:db_dependency,background_tasks: BackgroundTasks):
    chroma_db = get_chroma_db()
    docs = chroma_db.similarity_search(query.question)
    
    reply=generate_openai_response(query.prompt,query.question,query.conversation_id,db)
    messages = [
        Message(message_type="text",message=reply),
        Message(message_type="code",message=docs[0].metadata["code"])
    ]
    background_tasks.add_task(databaseAdding,conversation_id=query.conversation_id,userQuery=query.question,messages=messages,db=db)
    background_tasks.add_task(read_conversation,conversation_id=query.conversation_id,db=db)
    return {"messages": messages}



#for quiz------------------------------------------------------------------------------------------------------


def generate_quiz_prompt(topic: str) -> str:
    return (
        "Generate a quiz with the following details:\n"
        f"- Number of questions: {10}\n"
        f"- Quiz Topic: {topic}\n\n"
        "Each question should have 4 options with one or multiple correct answers. If there is multiple correct answer, set multiple_choice to true.\n"
        "Questions should be unique, concise, aligned with the topic, and challenging. If you give repetitive, obvious and easy questions, you will be penalized 500 dollars.\n"
        "Provide the questions and options in the following JSON format:\n"
        "{\n"
        '  "questions": [\n'
        '    {\n'
        '      "text": "Question 1",\n'
        '      "multiple_choice": false,\n'
        '      "options": [\n'
        '        {"text": "Option A", "is_right": false},\n'
        '        {"text": "Option B", "is_right": true},\n'
        '        {"text": "Option C", "is_right": false},\n'
        '        {"text": "Option D", "is_right": false}\n'
        '      ]\n'
        '    },\n'
        '    {\n'
        '      "text": "Question 2",\n'
        '      "multiple_choice": true,\n'
        '      "options": [\n'
        '        {"text": "Option A", "is_right": false},\n'
        '        {"text": "Option B", "is_right": true},\n'
        '        {"text": "Option C", "is_right": false},\n'
        '        {"text": "Option D", "is_right": true}\n'
        '      ]\n'
        '    },\n'
        '    ...\n'
        '  ]\n'
        "}"
    )



def generate_quiz_response(prompt:str):
    openai.api_key = OPENAI_API_KEY
    messages = [
        {"role": "user", "content": prompt},
    ]
    
    chat_completion = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    reply = chat_completion.choices[0].message.content
    # print(reply)
    return reply


@router.post("/quiz", status_code=status.HTTP_200_OK)
async def build_quiz(request: createQuizRequest, db: db_dependency):
    user=db.query(Users).filter(Users.id==request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    

    prompt=generate_quiz_prompt(request.topic)
    response=generate_quiz_response(prompt)
    quiz_data=json.loads(response)
    db_quiz=Quizes(topic=request.topic,score=0,state=2,owner_id=request.user_id, created_at=datetime.now(), updated_at=datetime.now())
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    for question in quiz_data["questions"]:
        db_ques=QuizQuestions(text=question['text'],
                              quiz_id=db_quiz.id,
                              multiple_choice=question['multiple_choice'])
        db.add(db_ques)
        db.commit()
        db.refresh(db_ques)
        for option in question['options']:
            db_option= QuizOptions(text=option['text'],
                                    ques_id=db_ques.id,
                                    is_right=option['is_right'])
            db.add(db_option)
    db.commit()
   
    return {"message": "quiz created successfully","quiz_id":db_quiz.id}



#for suggestion------------------------------------------------------------------------------------------------


def generate_suggestions_prompt(topic: str) -> str:
    return (
        "Generate a list of 5 suggestions from codeforces, leetcode, codechef or similar coding platforms for the following topic:\n"
        f"- Topic: {topic}\n\n"
        "Each suggestion should include the problem name as placeholder text, a relevant link to that suggestion on that coding platform, and the coding platform as source. "
        "Suggestions should be related to topic. there should be variety of difficulty levels and types of problems. If you provide irrelevant, repetitive, or low-quality suggestions, you will be penalized 500 dollars.\n"
        "Provide the suggestions in the following JSON format:\n"
        "{\n"
        '  "suggestions": [\n'
        '    {\n'
        '      "placeholder": "Suggestion 1",\n'
        '      "link": "http://example.com/suggestion1",\n'
        '      "source": "Source 1"\n'
        '    },\n'
        '    {\n'
        '      "placeholder": "Suggestion 2",\n'
        '      "link": "http://example.com/suggestion2",\n'
        '      "source": "Source 2"\n'
        '    },\n'
        '    ...\n'
        '  ]\n'
        "}"
    )


def generate_suggestion_response(prompt:str):
    openai.api_key = OPENAI_API_KEY
    messages = [
        {"role": "user", "content": prompt},
    ]
    
    chat_completion = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    reply = chat_completion.choices[0].message.content
    # print(reply)
    return reply


@router.post("/suggestion", status_code=status.HTTP_200_OK)
async def build_suggestion(request: createSuggestionRequest, db: db_dependency):
    user=db.query(Users).filter(Users.id==request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    prompt=generate_suggestions_prompt(request.topic)
    response=generate_suggestion_response(prompt)
    suggestion_data=json.loads(response)
    suggestions=[]
    for suggestion in suggestion_data["suggestions"]:
        db_suggestion=Suggestions(placeholder=suggestion['placeholder'],
                                   link=suggestion['link'],
                                   source=suggestion['source'],
                                   state=1,
                                   owner_id=request.user_id,
                                   created_at=datetime.now())
        db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)
        suggestions.append({"id":db_suggestion.id,
                            "placeholder":db_suggestion.placeholder,
                            "link":db_suggestion.link,
                            "source":db_suggestion.source,
                            "state":db_suggestion.state,
                            "owner_id":db_suggestion.owner_id,
                            "created_at":db_suggestion.created_at
                            })

    return {"message": "suggestions created successfully","suggestions":suggestions}



#for lecture------------------------------------------------------------------------------------------------


def generate_lecture_prompt(topic: str) -> str:
    return (
        "Generate a lecture on the following topic:\n"
        f"- Topic: {topic}\n\n"
        "The lecture should contain 10 to 15 questions. Each question should be relevant to the topic. "
        "Make sure that the questions are unique, concise, and challenging. If you provide repetitive, obvious, and easy questions, you will be penalized 500 dollars.\n"
        "If the topic is very specific, the questions should be specific within the boundary of the topic. If the topic is broad, the questions should be diverse.\n"
        "questions should be such that can be answered in small sentences. If the questions are too long or broad, the user will not be able to answer them.\n"
        "Provide the lecture and questions in the following JSON format:\n"
        "{\n"
        '  "lecture": {\n'
        f'    "topic": "{topic}",\n'
        '    "questions": [\n'
        '      {\n'
        '        "text": "Question 1"\n'
        '      },\n'
        '      {\n'
        '        "text": "Question 2"\n'
        '      },\n'
        '      ...\n'
        '    ]\n'
        "  }\n"
        "}"
    )


def generate_lecture_response(prompt:str):
    openai.api_key = OPENAI_API_KEY
    messages = [
        {"role": "user", "content": prompt},
    ]
    
    chat_completion = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    reply = chat_completion.choices[0].message.content
    # print(reply)
    return reply


@router.post("/lecture", status_code=status.HTTP_200_OK)
async def build_lecture(request: createLectureRequest, db: db_dependency):
    user=db.query(Users).filter(Users.id==request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    prompt=generate_lecture_prompt(request.topic)
    response=generate_lecture_response(prompt)
    lecture_data=json.loads(response)

    lecture_info = lecture_data['lecture']
    topic = lecture_info['topic']
    questions = lecture_info['questions']

    #at first, create the teacher convo

    teacher_convo=Conversations(name="lecture",
                                description="",
                                isFree=True,
                                isAdvanced=True,
                                isTeacher=True,
                                user_id=request.user_id,
                                created_at=datetime.now(),
                                updated_at=datetime.now())
    db.add(teacher_convo)
    db.commit()
    db.refresh(teacher_convo)

    #then, create the lecture

    db_lec=Lectures(topic=request.topic,
                    isStarred=False,
                    total_questions=len(questions),
                    current_question=1,
                    teacher_convo_id=teacher_convo.id,
                    owner_id=request.user_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now())

    db.add(db_lec)
    db.commit()
    db.refresh(db_lec)

    #then, add the questions to lecture

 
    for idx, question in enumerate(questions):
        db_question=LectureQuestions(text=question['text'],
                                    answer="",
                                    lecture_id=db_lec.id,
                                    serial_no=idx+1)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)


    return {"message": "lecture created successfully","lecture_id":db_lec.id}





#for checking answer of lecture------------------------------------------------------------------------------------------------


def generate_answer_check_prompt(question: str, answer: str) -> str:
    return (
        f"Determine if the provided answer to the question is correct.\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n\n"
        "Please respond with 'true' if the answer is correct and 'false' if the answer is incorrect."
    )


def check_answer_response(prompt:str):
    openai.api_key = OPENAI_API_KEY
    messages = [
        {"role": "user", "content": prompt},
    ]
    
    chat_completion = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    reply = chat_completion.choices[0].message.content
    # print(reply)
    return reply


@router.post("/checkAnswer")
async def check_answer(checkAnswerRequest: checkAnswerRequest, db: db_dependency):
    lecture = db.query(Lectures).filter(Lectures.id == checkAnswerRequest.lecture_id).first()
    if lecture is None:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    question = db.query(LectureQuestions).filter(LectureQuestions.lecture_id == checkAnswerRequest.lecture_id).filter(LectureQuestions.serial_no == lecture.current_question).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    prompt=generate_answer_check_prompt(question.text, checkAnswerRequest.answer)
    response=check_answer_response(prompt)
    print(response)

    if  response=="true" or response=="True":
        lecture.current_question += 1
        question.answer=checkAnswerRequest.answer
        db.commit()
        return {"response": "it seems like the answer is correct","status": "correct"}
    elif response=="false" or response=="False":
        return {"response": "it seems like the answer is incorrect.please ask the professor","status": "incorrect"}
        












