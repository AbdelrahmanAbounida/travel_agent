from langchain.document_loaders.csv_loader import CSVLoader
from langchain.schema import Document
from typing import List
import torch
from sentence_transformers import SentenceTransformer

class CSVStorage:
    def __init__(self,PINECONE_INDEX_NAME:str,OPENAI_API_KEY:str):
        self.PINECONE_INDEX_NAME = "test-index"# PINECONE_INDEX_NAME
        self.OPENAI_API_KEY = OPENAI_API_KEY

    
    def load_doc_data(self,file_name:str) -> List[Document]:
        loader = CSVLoader(file_path=file_name, 
                       encoding="utf-8", 
                       csv_args={'delimiter': ','})
        data = loader.load()
        return data

    def _preprocess_table_to_text(self,tables:list):

        # set device to GPU if available
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # load the table embedding model from huggingface models hub
        retriever = SentenceTransformer("deepset/all-mpnet-base-v2-table", device=device)

        # we will use this function to destructure the tabular data and keep it ready to get vectorized and stored into pinecone
        processed = []
        for table in tables:
            # convert the table to csv and
            processed_table = "\n".join([table.to_csv(index=False)])
            # add the processed table to processed list
            processed.append(processed_table)
        return '/n'.join(processed)



