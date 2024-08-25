from sqlalchemy import Column, Integer, String, ForeignKey,Boolean, DateTime
from database import Base

# here we will write the tables of database....................

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# --------------------------------------------------------------------------------------------------------

class Conversations(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    isFree = Column(Boolean)
    isAdvanced = Column(Boolean)
    isTeacher = Column(Boolean)
    isHighlighted = Column(Boolean) 
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
 

class Turns(Base):
    __tablename__ = 'turns'
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    created_at = Column(DateTime)


class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    message_type = Column(String)
    message = Column(String)
    turn_id = Column(Integer, ForeignKey('turns.id'))
    created_at = Column(DateTime)

# --------------------------------------------------------------------------------------------------------


class Quizes(Base):
    __tablename__ = 'quizes'
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String)
    score=Column(Integer)
    total_questions = Column(Integer)
    isAdvanced = Column(Boolean)
    state =Column(Integer)   # 1= attempted, 2= unattempted, 3= attempted and highlighted, 4= unattempted and highlighted
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)



class QuizQuestions(Base):
    __tablename__ = 'quiz_questions'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    quiz_id = Column(Integer, ForeignKey('quizes.id'))
    multiple_choice= Column(Boolean)


class QuizOptions(Base):
    __tablename__ = 'quiz_options'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    ques_id = Column(Integer, ForeignKey('quiz_questions.id'))
    is_right=Column(Boolean)


# --------------------------------------------------------------------------------------------------------


class Suggestions(Base):
    __tablename__ = 'suggestions'
    id = Column(Integer, primary_key=True, index=True)
    placeholder = Column(String)
    link = Column(String)
    source = Column(String)
    state =Column(Integer)   # 1= normal, 2= important, 3= visited, 4= important and visited
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    



# --------------------------------------------------------------------------------------------------------



class Lectures(Base):
    __tablename__ = 'lectures'
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String)
    isStarred = Column(Boolean)
    isAdvanced = Column(Boolean)
    total_questions = Column(Integer)
    current_question = Column(Integer)
    teacher_convo_id = Column(Integer, ForeignKey('conversations.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)



class LectureQuestions(Base):
    __tablename__ = 'lecture_questions'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    answer = Column(String)
    serial_no = Column(Integer)
    lecture_id = Column(Integer, ForeignKey('lectures.id'))

