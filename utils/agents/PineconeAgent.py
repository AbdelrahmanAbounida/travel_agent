"""
Load content from
"""
from langchain.embeddings import OpenAIEmbeddings
from uuid import uuid4
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from typing import List , Dict


class PineconeAgent:
    def __init__(self,OPENAI_API_KEY:str,PINECONE_API_KEY:str,PINECONE_ENV:str,PINECONE_INDEX_NAME:str):
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.PINECONE_API_KEY = PINECONE_API_KEY
        self.PINECONE_ENV = PINECONE_ENV
        self.PINECONE_INDEX_NAME = PINECONE_INDEX_NAME
        
        openai.api_key = OPENAI_API_KEY


    def init_pinecone(self):
        pinecone.init(api_key=self.PINECONE_API_KEY, environment=self.PINECONE_ENV)

    def delete_index(self):
        pinecone.delete_index(self.PINECONE_INDEX_NAME)

    def create_pinecone_index(self,dimension:int=1536):

        if not self.PINECONE_INDEX_NAME in pinecone.list_indexes():
            pinecone.create_index(self.PINECONE_INDEX_NAME,dimension=dimension,metric="cosine")
            print(f"{self.PINECONE_INDEX_NAME} has been created")
            return
        else:
            print(f"{self.PINECONE_INDEX_NAME} already exists")

    def get_context(self,question:str,source:str,city:str="Valencia") -> Dict[str,List]:

        try:
            index = pinecone.Index(self.PINECONE_INDEX_NAME)
        except Exception as e:
            print("Failed to connect to pinecone")
            raise NameError("Failed to connect to pinecone")

        if source:
            metadata = {"source":source}
        else:
            metadata = {}

        embedded_question = openai.Embedding.create(
            model="text-embedding-ada-002", input=question)['data'][0]['embedding']

        query_result = index.query(vector=embedded_question,
                                namespace=city,
                                filter=metadata,
                                top_k=5,
                                include_metadata=True)
        
        return query_result

    def store_data_to_pinecone(self,data:List[Document],city:str,source:str):
        
        print(self.PINECONE_INDEX_NAME)
        print("Start storing")
        index = pinecone.Index(self.PINECONE_INDEX_NAME)
        model_name = 'text-embedding-ada-002'
        embeddings = OpenAIEmbeddings(
                            model=model_name,
                            openai_api_key=self.OPENAI_API_KEY
                            )
        
        batch_limit = 100
        texts = []
        metadatas = []

        print(data)
        for j,content in enumerate(data):

            if 'been able to serve the page you asked' in content.page_content or 'Page Not Found' in content.page_content:
                continue
            
            # 1- update meta data for this chunk of text
            record_metadatas = {
                "chunk": j,
                "text": content.page_content,
                'source': source
            } 
            metadatas.append(record_metadatas)

            # 2- append this chunk to a list to create vector
            texts.append(content.page_content)

            if len(texts) >= batch_limit:
                ids = [str(uuid4()) for _ in range(len(texts))]
                embeds = embeddings.embed_documents(texts)
                index.upsert(vectors=zip(ids, embeds, metadatas),namespace=city)
                texts = []
                metadatas = []


        if len(texts):
            ids = [str(uuid4()) for _ in range(len(texts))]
            embeds = embeddings.embed_documents(texts)
            index.upsert(vectors=zip(ids, embeds, metadatas),namespace=city)

        print("Data has been stored successfully to pinecone")