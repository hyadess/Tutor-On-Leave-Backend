
import numpy as np
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv

OPENAI_API_KEY= os.environ.get("OPENAI_API_KEY")


# Read data from CSV
csv_file_path = 'gifs.csv'
df = pd.read_csv(csv_file_path)

# Assuming the CSV has columns 'page_content' and 'code'
data = [
    Document(
        page_content=row['description'],
        metadata={
            "code": row['gif']
        },
    )
    for index, row in df.iterrows()
]

# Step 1: Create embedding model for the content
embedding_model = OpenAIEmbeddings()
db = Chroma.from_documents(data,embedding_model,persist_directory="./chroma_db")

def get_chroma_db():
    db=Chroma(persist_directory="./chroma_db",embedding_function=embedding_model)
    return db



