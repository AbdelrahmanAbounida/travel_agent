"""
Load data from url
"""
from typing import List
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from langchain.document_loaders import UnstructuredURLLoader
from playwright.sync_api import sync_playwright
from unstructured.partition.html import partition_html
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

class URLStorage:

    def __init__(self,OPENAI_API_KEY:str) -> None:
        self.OPENAI_API_KEY = OPENAI_API_KEY

    def get_urls_sitemap(self,url:str) -> List[str]:
        """return all links in a given url using sitemap.xml"""
        sitemap_url = url+"sitemap.xml"
        response = requests.get(sitemap_url)

        if response.status_code == 200:
            sitemap_content = response.text
            try:
                root = ET.fromstring(sitemap_content)
                pages = []
                for element in root.iter():
                    if 'loc' in element.tag:
                        pages.append(element.text)
                return pages
            except Exception as e:
                print("************************************")
                print("Failed to get xmlsitemap conetnt")
                # print(f"Error: {e}")
                print("Lets try regular scraping")
                print("************************************")
        return [""]

    def get_webpage_urls(self,URLS:List[str]) -> List[str]:
        """return all urls in a page using sitemap or regular webscraping"""

        all_pages = []
        for url in URLS:
            # Method1: get urls using website sitemap
            all_urls = self.get_urls_sitemap(url)

            # Method2 : using regular web scraping
            if len(all_urls) <= 1:
                reqs = requests.get(url)
                soup = BeautifulSoup(reqs.text, 'html.parser')
                all_urls = []

                for link in soup.find_all('a'):
                    all_urls.append(f"{url}{link.get('href')}")

            all_pages += all_urls

        return all_pages

    def load_urls_data(self,urls:List[str]) -> List[Document]:
        """Load text from url"""
        loader = UnstructuredURLLoader(urls=urls)
        return loader.load()

    def manual_scraping(self,urls) -> List[str]:
        """Test Method to try playright"""

        docs = list()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for url in urls:
                try:
                    page = browser.new_page()
                    page.goto(url)

                    page_source = page.content()

                    print(page_source)
                    elements = partition_html(text=page_source)
                    text = "\n\n".join([str(el) for el in elements])
                    docs.append(text)

                except Exception as e:
                    if True:
                        print(
                            f"Error fetching or processing {url}, exception: {e}"
                        )
                    else:
                        raise e
            browser.close()
        return docs

    def store_to_pinecone(self,data,index_name):
        # 1- Split the documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(data)

        # 2- Creating Embedding Model
        embeddings = OpenAIEmbeddings(openai_api_key=self.OPENAI_API_KEY)

        # 3- Create the vectorestore to use as the index

        db = Pinecone.from_documents(docs, embeddings,index_name=index_name)
        print("Document has been stored to pinecone successfully")
        return db