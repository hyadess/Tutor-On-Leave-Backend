from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Annotated
import dataStruct.models as models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from database import db_dependency
from chroma_db import Chroma, data, embedding_model
from routes import conversation,profile, auth,quiz,suggestion,lecture,test

app = FastAPI()
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#create the databases.....................
models.Base.metadata.create_all(bind=engine)
#db = Chroma.from_documents(data,embedding_model,persist_directory="./chroma_db")

app.include_router(auth.router)
app.include_router(conversation.router)
app.include_router(test.router)
app.include_router(quiz.router)
app.include_router(suggestion.router)
app.include_router(lecture.router)
app.include_router(profile.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    


