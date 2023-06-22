from utils.agents.PineconeAgent import PineconeAgent
from langchain.schema import Document
from typing import List, Any, Dict
from pinecone.exceptions import PineconeProtocolError
from dotenv import load_dotenv
import streamlit as st
import os 
import sys

load_dotenv()

# *********************************
# Load environmental variables
# *********************************

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")


# *********************************
# utils
# *********************************
def reinit_pinecone() -> PineconeAgent:
    pinecone_agent = PineconeAgent(OPENAI_API_KEY=OPENAI_API_KEY,
                               PINECONE_API_KEY=PINECONE_API_KEY,
                               PINECONE_ENV=PINECONE_ENV,
                               PINECONE_INDEX_NAME='test-index') # PINECONE_INDEX_NAME

    pinecone_agent.init_pinecone()

    return pinecone_agent

def get_answers_from_context(context:Dict[str,List]) -> List[str]:

    if not context:
        print("Context is none")
        raise KeyError("Context shouldn't be none")
    
    answers = []

    print(f"This is context: {type(context)}")

    for answer in context['matches']:
        print(f"Answer: {answer}")
        answers.append(answer['metadata']['text'])
    
    return answers

pinecone_agent = reinit_pinecone()

st.header("Test Pinecone Query")

# *********************************
# Initialize Pinecone
# *********************************

city = st.text_input("insert the city name, to which this data belongs to. ex: Valencia")
source = st.text_input("insert the data source type pdf, url, csv, or keep it empty for all")
question = st.text_input("Enter your question. ex: list some hotels in valencia!")


if st.button('Get Answer'):
    
    if not city:
        st.error("City should't be none")
        sys.exit()

    if not question:
        st.error("Question should't be none")
        sys.exit()

    with st.spinner("Getting answer from pinecone"):
        try:
            pinecone_agent.get_context(question=question,source=source,city=city)
        except PineconeProtocolError:
            try:
                pinecone_agent.init_pinecone()
                context = pinecone_agent.get_context(question=question,source=source,city=city)
                answers = get_answers_from_context(context=context)
                print(answers)
                st.write("Answer")
                st.write(answers)
                
            except Exception as e:
                pinecone_agent = reinit_pinecone()
                pinecone_agent.init_pinecone()
                context = pinecone_agent.get_context(question=question,source=source,city=city)
                answers = get_answers_from_context(context=context)
                print(answers)
                st.write("Answer")
                st.write(answers)
        except Exception as e:
            print(type(e))
            print(e)
            st.error("Failed to get answer from pinecone")


