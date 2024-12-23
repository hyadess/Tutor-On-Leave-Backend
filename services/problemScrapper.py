from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import pprint
from langchain_text_splitters import RecursiveCharacterTextSplitter
import dotenv
import os
dotenv.load_dotenv()

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
llm = ChatMistralAI(model="mistral-large-latest", temperature=0,api_key=os.getenv("MISTRAL_API_KEY"))
agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


class Problem(BaseModel):
    problem_name: str = Field(None, description="Name of the problem")
    problem_tags: List[str] = Field(None, description="Tags of the problem")
    problem_difficulty: Optional[int] = Field(None, description="Difficulty of the problem")
    problem_url: str = Field(None, description="full URL of the problem")

class ProblemSet(BaseModel):
    problems: List[Problem]


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert problem extraction algorithm. "
            "Only extract relevant problem information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "leave it empty.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

runnable = prompt | llm.with_structured_output(schema=ProblemSet)



def scrape_codeforces(urls):
    loader = AsyncChromiumLoader(urls,user_agent=agent)
    docs = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(docs, tags_to_extract=["table","tbody","tr","td","a","span"])  # change here
    print("Extracting content with LLM")

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    splits = splitter.split_documents(docs_transformed)
    problems=[]
    for split in splits:
        extracted_content = runnable.invoke({"text": split.page_content})
        problems.extend(extracted_content.problems)

    print(problems)
    return problems



urls = ["https://codeforces.com/problemset/page/1"]
extracted_content = scrape_codeforces(urls)