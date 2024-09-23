import streamlit as st
import os
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_openai.chat_models import ChatOpenAI
from configs.configs import *

class Gui():
    def __init__(self, PATH_INPUT_FILES, utils):
        self.utils = utils
        self.PATH_INPUT_FILES = PATH_INPUT_FILES

    def create_talk_chain(self):
        # Importar documentos e criar vetor
        self.utils.import_documents()  # Lê e converte o Excel para CSV automaticamente
        self.utils.import_csv_files()  # Importar CSV já convertido
        self.utils.split_documents()   # Dividir documentos
        vector_store = self.utils.create_vector_store()

        if vector_store is None:
            st.error("Erro ao criar vector store. Verifique se os documentos foram carregados corretamente.")
            return

        chat = ChatOpenAI(model=get_config('model_name'))
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key='chat_history',
            output_key='answer'
        )

        retriever = vector_store.as_retriever(
            search_type=get_config('retrieval_search_type'),
            search_kwargs=get_config('retrieval_kwargs')
        )

        prompt = PromptTemplate.from_template(get_config('prompt'))
        chat_chain = ConversationalRetrievalChain.from_llm(
            llm=chat,
            memory=memory,
            retriever=retriever,
            return_source_documents=True,
            verbose=True,
            combine_docs_chain_kwargs={'prompt': prompt}
        )
        st.session_state['chain'] = chat_chain

    def sidebar(self):
        button_label = "Inicializar RealBOT" if 'chain' not in st.session_state else "Atualizar RealBOT"

        if st.button(button_label, use_container_width=True):
            # Verificar se o arquivo Excel já foi convertido corretamente
            if not os.path.exists(self.utils.csv_file):
                st.error(f"Arquivo CSV não encontrado. Verifique se o arquivo Excel foi convertido corretamente.")
            else:
                st.success('Inicializando o RealBOT...')
                self.create_talk_chain()

                # Em vez de `st.experimental_rerun()`, controlamos via `session_state`
                st.session_state['chain_initialized'] = True  # Marca a inicialização no estado

    def chat_window(self):
        st.header('🤖 REALBOT - Assistente de Regras 🤖', divider=True)
        
        if 'chain' not in st.session_state:
            st.error('Inicialize o RealBOT para começar.')
            st.stop()

        chain = st.session_state['chain']
        self.memory = chain.memory

        messages = self.memory.load_memory_variables({})['chat_history']

        container = st.container()

        for message in messages:
            chat = container.chat_message(message.type)
            chat.markdown(message.content)

        new_message = st.chat_input('Digite sua dúvida... e converse com o RealBOT')

        if new_message and new_message.strip():
            chat = container.chat_message('human')
            chat.markdown(new_message)

            try:
                response = chain.invoke({'question': new_message})
                chat = container.chat_message('ai')
                chat.markdown(response['answer'])
            except Exception as e:
                st.error(f"Erro ao processar a pergunta: {e}")

            # Em vez de `st.experimental_rerun()`, controlamos a atualização de interface manualmente
            st.session_state['new_message'] = new_message


