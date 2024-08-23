from pydantic import BaseModel

# here we define the data models that will be used in the API

class UserRequest(BaseModel):
    username: str
    password: str
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class logoutRequest(BaseModel):
    username: str

class createConversationRequest(BaseModel):
    name: str
    isFree: bool
    isAdvanced: bool
    isTeacher: bool
    user_id: int


class Message(BaseModel):
    message_type: str
    message: str

class createTurnRequest(BaseModel):
    sender: str
    conversation_id: int
    messages: list[Message]


class queryRequest(BaseModel):
    conversation_id: int
    question: str
    prompt: str

#--------------------------------------------------------------------for quiz------------------------------------------------


class createQuizRequest(BaseModel):
    user_id: int
    topic: str
    isAdvanced: bool
    total_questions: int



class updateQuizScore(BaseModel):
    user_id:int
    quiz_id:int
    score:int

class updateQuizRequest(BaseModel):
    user_id:int
    quiz_id:int


#--------------------------------------------------------------------for suggestion------------------------------------------------


class createSuggestionRequest(BaseModel):
    user_id:int
    topic:str
    type:str #blog, youtube, code


class updateSuggestionRequest(BaseModel):
    user_id:int
    suggestion_id:int


#--------------------------------------------------------------------for lecture------------------------------------------------

class createLectureRequest(BaseModel):
    user_id:int
    topic:str
    isAdvanced:bool


class checkAnswerRequest(BaseModel):
    user_id:int
    lecture_id:int
    answer:str