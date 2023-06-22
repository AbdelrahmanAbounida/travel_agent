from langchain.text_splitter import CharacterTextSplitter # splitting text into chunks
from langchain.embeddings.openai import OpenAIEmbeddings # embedding text chunks
from langchain.vectorstores import Pinecone # Vector Store
from langchain.document_loaders import PyPDFLoader, UnstructuredPDFLoader, PDFMinerLoader, PyMuPDFLoader # loading Text from PDF
from langchain.schema import Document
from typing import List
import os
import sys


class PDFStorage:

    def __init__(self,OPENAI_API_KEY:str,PINECONE_INDEX_NAME:str):
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.PINECONE_INDEX_NAME = PINECONE_INDEX_NAME

    def load_doc_data(self,file_name=None):
        """load text from pdf document"""
        if not file_name:
            raise TypeError("File Error shouldn't be None")
        else:
            doc_path = f"{file_name}" # {self.dir_path}

        if not os.path.exists(doc_path):
            print("File doesn't exist. Make sure the file is in the same directory")
            sys.exit()

        # We gonna try all langchain pdf loaders to handle different use cases
        try:
            loader = PyPDFLoader(doc_path)
            data = loader.load()

        except:
            try:
                loader = UnstructuredPDFLoader(doc_path)
                data = loader.load()
                print("Data loaded successfully")
            except:
                    try:
                        loader = PDFMinerLoader(doc_path)
                        data = loader.load()
                    except:
                            try:
                                loader = PyMuPDFLoader(doc_path)
                                data = loader.load()
                            except:
                                data= []
                                raise ("Failed to load the given pdf file.")
        return data


    def store_to_pinecone(self,data:List[Document],city:str):
        # 1- Split the documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(data)
        texts = [doc.page_content for doc in docs]
        # 2- Creating Embedding Model
        embeddings = OpenAIEmbeddings(openai_api_key=self.OPENAI_API_KEY)

        # 3- Create the vectorestore to use as the index
        db = Pinecone.from_texts(texts,embeddings,index_name=self.PINECONE_INDEX_NAME,namespace=city,metadatas=[{"source":"pdf"}])
        print("Document has been stored to pinecone successfully")
        
        return db
