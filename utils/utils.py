import pandas as pd
import streamlit as st
import os
from langchain_community.document_loaders.csv_loader import CSVLoader

class Utils():

    def __init__(self, PATH_INPUT_FILES):
        self.PATH_INPUT_FILES = PATH_INPUT_FILES
        self.excel_file = os.path.join(self.PATH_INPUT_FILES, 'Regras Realbox.xlsx')
        self.csv_file = os.path.join(self.PATH_INPUT_FILES, 'Regras Realbox.csv')

    def import_documents(self):
        # Verificar se o arquivo Excel existe
        if not os.path.exists(self.excel_file):
            st.error(f"Arquivo Excel {self.excel_file} não encontrado.")
            return None
        
        try:
            # Converter o arquivo Excel para CSV
            df = pd.read_excel(self.excel_file)
            df.to_csv(self.csv_file, index=False, encoding='utf-8')
            st.success(f"Arquivo Excel convertido para CSV com sucesso: {self.csv_file}")
            
            # Agora carregamos o CSV com o CSVLoader do Langchain
            loader = CSVLoader(file_path=self.csv_file, encoding='utf-8')
            documents = loader.load()
            st.success(f"Arquivo CSV carregado com sucesso!")
            return documents  # Retorna os documentos carregados
        except Exception as e:
            st.error(f"Erro ao converter e carregar o CSV: {e}")
            return None
