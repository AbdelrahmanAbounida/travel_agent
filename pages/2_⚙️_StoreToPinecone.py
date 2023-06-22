import streamlit as st 
from streamlit_option_menu import option_menu
from utils.store.CSVStorage import CSVStorage
from utils.store.PDFStorage import PDFStorage
from utils.store.URLStorage import URLStorage
from utils.agents.PineconeAgent import PineconeAgent
from langchain.schema import Document
from typing import List, Any
from dotenv import load_dotenv
import tempfile
import os 
import sys

load_dotenv()


# *********************************
# Load environmental variables
# *********************************

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")
PINECONE_INDEX_NAME = "destination-index" #os.environ.get("PINECONE_INDEX_NAME")

# *********************************
# Initialize Pinecone
# *********************************

def reinit_pinecone() -> PineconeAgent:
    pinecone_agent = PineconeAgent(OPENAI_API_KEY=OPENAI_API_KEY,
                               PINECONE_API_KEY=PINECONE_API_KEY,
                               PINECONE_ENV=PINECONE_ENV,
                               PINECONE_INDEX_NAME=PINECONE_INDEX_NAME) # PINECONE_INDEX_NAME

    pinecone_agent.init_pinecone()

    return pinecone_agent


pinecone_agent = reinit_pinecone()

# *********************************
# Loaders
# *********************************
pdf_loader = PDFStorage(
                        OPENAI_API_KEY=OPENAI_API_KEY,
                        PINECONE_INDEX_NAME = PINECONE_INDEX_NAME
                       )

csv_loader = CSVStorage(
                        PINECONE_INDEX_NAME=PINECONE_INDEX_NAME, 
                        OPENAI_API_KEY=OPENAI_API_KEY
                        )

url_loader = URLStorage(OPENAI_API_KEY=OPENAI_API_KEY)


def load_file_data(uploaded_file:Any,file_type:str) -> List[Document]:

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    if not os.path.exists(tmp_file_path):
        raise LookupError("Failed to laod this file")
    
    if file_type == 'pdf':
        data = pdf_loader.load_doc_data(file_name=tmp_file_path)

    elif file_type == 'csv':
        data = csv_loader.load_doc_data(file_name=tmp_file_path)
    else:
        raise TypeError("This file type is not supported.Please only upload csv or PDF")

    return data


st.header("Store PDF/ URLs / CSV Content")
options = option_menu('',["CSV", "PDF", 'URLS'], icons=['filetype-csv','file-pdf','link'],orientation="horizontal")


####################
## City
####################
city = st.text_input("insert the city name, to which this data belongs to")

####################
## CSV
####################

if options == "CSV":
    csv_file = st.file_uploader("Upload a CSV")
    data = []

    if st.button('Store') :

        if not csv_file:
            st.error("Please make sure to upload the csv first")
            sys.exit()

        if not city:
            st.error("Please Make sure that you set the city name")
            sys.exit()

        else:
            with st.spinner("Loading csv content...."):
                # 1,2- Storing and Loading text from csv
                try:
                    data = load_file_data(uploaded_file=csv_file,file_type="csv")
                    st.success("CSV Content has been loaded successfully. Storing data in pinecone....")
                except:
                    st.error("Failed to load text from this csv")


            with st.spinner("Storing to pinecone...."):
                try:
                    # 3- Storing to pinecone
                    pinecone_agent.store_data_to_pinecone(data=data,city=city,source='csv')
                    st.success(f"CSV Content has been stored to Pinecone. under {city} namespace")
                except Exception as e:
                    print(e)
                    st.error("Failed to store data to pinecone")

####################
## PDF
####################

if options == "PDF":
    pdf_file = st.file_uploader("Upload an PDF")
    data = []

    if st.button('Store'):
        if not city:
            st.error("Please Make sure that you set the city name")
            sys.exit()
        else:
            if pdf_file:
                with st.spinner("Loading text from pdf...."):
                    # 1,2- Loading and storing text from pdf
                    try:
                        data = load_file_data(uploaded_file=pdf_file,file_type="pdf")
                        st.success("Text Loaded successfully from from this pdf. Storing data in pinecone....")
                    except Exception as e:
                        print(e)
                        st.error("Failed to load text from this pdf")

                with st.spinner("Storing to pinecone...."):
                    try:
                        # 3- Storing to pinecone
                        pinecone_agent.store_data_to_pinecone(data=data,city=city,source='pdf')
                        st.success("Data has been stored to Pinecone.")
                    except Exception as e:
                        print(e)
                        st.error("Failed to store data to pinecone")
            else:
                st.error("Please make sure to upload the PDF first")
                sys.exit() 

####################
## URL
####################
if options == "URLS":
    urls = st.text_input("insert a list of urls seperated by comma , ")

    if st.button('Store') :
        if not urls:
            st.error("Please Make sure to set urls seperared by comma before storing data")
        if not city:
            st.error("Please Make sure that you set the city name")
        else:
            with st.spinner("Loading urls' content...."):
                try:
                    list_urls = urls.split(',')
                    all_urls = url_loader.get_webpage_urls(list_urls)
                    data = url_loader.load_urls_data(all_urls) 
                    st.success("Text Loaded successfully from from urls. Storing data in pinecone....")

                    st.write("Scrapped Data")
                    st.write(data)

                except Exception as e:
                    print(e)
                    st.error("Failed to load text from urls")
            
            with st.spinner("Storing to pinecone...."):
                try:
                    # 3- Storing to pinecone
                    pinecone_agent.store_data_to_pinecone(data=data,city=city,source='url')
                    st.success("Data has been stored to Pinecone.")
                except Exception as e:
                    try:
                        pinecone_agent = reinit_pinecone()
                        pinecone_agent.store_data_to_pinecone(data=data,city=city,source='url')
                        st.success("Data has been stored to Pinecone.")
                    except Exception as e:
                        print(e)
                        st.error("Failed to store data to pinecone")

            
            



        
    