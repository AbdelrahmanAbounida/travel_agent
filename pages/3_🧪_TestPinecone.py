from utils.agents.PineconeAgent import PineconeAgent
from langchain.schema import Document
from typing import List, Any, Dict
from pinecone.exceptions import PineconeProtocolError
from dotenv import load_dotenv
import streamlit as st
import os 
import sys
import pinecone

load_dotenv()

# *********************************
# Load environmental variables
# *********************************

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")
PINECONE_INDEX_NAME = 'destination-index' # os.environ.get("PINECONE_INDEX_NAME")


# *********************************
# utils
# *********************************
def reinit_pinecone() -> PineconeAgent:
    pinecone_agent = PineconeAgent(OPENAI_API_KEY=OPENAI_API_KEY,
                               PINECONE_API_KEY=PINECONE_API_KEY,
                               PINECONE_ENV=PINECONE_ENV,
                               PINECONE_INDEX_NAME=PINECONE_INDEX_NAME) # PINECONE_INDEX_NAME

    pinecone_agent.init_pinecone()

    return pinecone_agent

def get_answers_from_context(context:Dict[str,List]) -> List[str]:

    try:
        a = context["matches"]
    except:
        print("Context is none")
        raise KeyError("Context shouldn't be none")        
    
    answers = []


    for answer in context['matches']:
        print(f"Answer: {answer}")
        answers.append(answer['metadata']['text'])
    
    return answers

pinecone_agent = reinit_pinecone()

st.header("Test Pinecone Query")

# *********************************
# Initialize Pinecone
# *********************************
try:
    all_cities = list(pinecone.Index(PINECONE_INDEX_NAME).describe_index_stats()['namespaces'].keys())
except:
    pinecone_agent.init_pinecone()
    all_cities = list(pinecone.Index(PINECONE_INDEX_NAME).describe_index_stats()['namespaces'].keys())


city = st.selectbox(
        'City',
        all_cities) 

source = st.selectbox(
            'Data Source',
            ('PDF','URL','CSV','')
        )

if not source:
    source = ''

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
            context = pinecone_agent.get_context(question=question,source=source,city=city)
            answers = get_answers_from_context(context=context)
            st.write("Answer")
            st.write(answers)
        except PineconeProtocolError:
            try:
                pinecone_agent.init_pinecone()
                context = pinecone_agent.get_context(question=question,source=source,city=city)
                answers = get_answers_from_context(context=context)
                st.write("Answer")
                st.write(answers)
                
            except Exception as e:
                pinecone_agent = reinit_pinecone()
                pinecone_agent.init_pinecone()
                context = pinecone_agent.get_context(question=question,source=source,city=city)
                answers = get_answers_from_context(context=context)
                st.write("Answer")
                st.write(answers)
        except Exception as e:
            print(type(e))
            print(e)
            st.error("Failed to get answer from pinecone")


