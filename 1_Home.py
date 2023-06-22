import streamlit as st
from dotenv import load_dotenv
from streamlit_lottie import st_lottie
from utils.agents.PineconeAgent import PineconeAgent
import os
import openai 
import requests

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")


st.set_page_config(page_title = 'Fashionapp',page_icon='')

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# *********************************
# Initialize Pinecone
# *********************************
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")

pinecone_agent = PineconeAgent(OPENAI_API_KEY=OPENAI_API_KEY,
                               PINECONE_API_KEY=PINECONE_API_KEY,
                               PINECONE_ENV=PINECONE_ENV,
                               PINECONE_INDEX_NAME='text-index') # PINECONE_INDEX_NAME

pinecone_agent.init_pinecone()
pinecone_agent.create_pinecone_index(dimension=1536)


st.header("Welcome to our Itinerary Creator App 🌍")
lottie_url = "https://assets2.lottiefiles.com/packages/lf20_cyin03sq.json"
lottie_json = load_lottieurl(lottie_url)
st_lottie(lottie_json)

sidebar  = st.sidebar