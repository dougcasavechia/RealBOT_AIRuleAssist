import pandas as pd
import streamlit as st
import os

from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Utils():

    def __init__(self, PATH_INPUT_FILES):
        # Caminho fixo do Excel
        self.PATH_INPUT_FILES = PATH_INPUT_FILES
        self.excel_file = os.path.join(self.PATH_INPUT_FILES, 'Regras Realbox.xlsx')
        self.csv_file = os.path.join(self.PATH_INPUT_FILES, 'Regras Realbox.csv')
        self.MODEL_NAME = 'gpt-3.5-turbo-0125'
        self.documents = []

    def import_documents(self):
        # Verificar se o arquivo Excel existe
        if not os.path.exists(self.excel_file):
            st.error(f"Arquivo Excel {self.excel_file} não encontrado.")
            return

        # Ler o Excel e converter para CSV
        try:
            df = pd.read_excel(self.excel_file)
            df.to_csv(self.csv_file, index=False, encoding='utf-8')
            st.success(f"Arquivo Excel convertido para CSV com sucesso: {self.csv_file}")
        except Exception as e:
            st.error(f"Erro ao ler ou converter o arquivo Excel: {e}")
            return

    def import_csv_files(self):
        self.documents = []
        if os.path.exists(self.csv_file):
            loader = CSVLoader(file_path=self.csv_file)
            file_documents = loader.load()
            self.documents.extend(file_documents)
        else:
            st.error(f"Arquivo CSV {self.csv_file} não encontrado.")

        return self.documents
    
    def split_documents(self):
        if not self.documents:
            st.error("Nenhum documento disponível para divisão.")
            return

        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2500,
            chunk_overlap=250,
            separators=["\n\n", ".", " ", ""]
        )
        self.documents = recursive_splitter.split_documents(self.documents)

        for i, doc in enumerate(self.documents):
            doc.metadata['source'] = doc.metadata['source'].split('/')[-1]
            doc.metadata['doc_id'] = i

        return self.documents
    
    def create_vector_store(self):
        if not self.documents:
            st.error("Nenhum documento encontrado para criar o vetor.")
            return None

        try:
            embedding_model = OpenAIEmbeddings()
            self.vector_store = FAISS.from_documents(
                documents=self.documents,
                embedding=embedding_model
            )
            st.success("Vector store criado com sucesso!")
            return self.vector_store  # Retornar o vetor criado
        except Exception as e:
            st.error(f"Erro ao criar vector store: {e}")
            return None


