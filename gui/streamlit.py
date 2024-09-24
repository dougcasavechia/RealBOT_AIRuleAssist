import streamlit as st
from langchain.chains.question_answering import load_qa_chain
from langchain_openai.chat_models import ChatOpenAI

class Gui():
    def __init__(self, PATH_INPUT_FILES, utils):
        self.utils = utils
        self.PATH_INPUT_FILES = PATH_INPUT_FILES

    def create_talk_chain(self):
        # Carregar os documentos a partir do CSV (após conversão do Excel)
        documents = self.utils.import_documents()
        if not documents:
            return

        # Configurar o modelo de chat da OpenAI
        chat = ChatOpenAI(model='gpt-3.5-turbo-0125')

        # Configurar a cadeia de perguntas e respostas (QA chain)
        chain = load_qa_chain(llm=chat, chain_type='stuff', verbose=True)

        # Armazenar a cadeia e os documentos no session_state
        st.session_state['chain'] = chain
        st.session_state['documents'] = documents  # Armazena os documentos carregados

    def sidebar(self):
        button_label = "Inicializar RealBOT" if 'chain' not in st.session_state else "Atualizar RealBOT"

        if st.button(button_label, use_container_width=True):
            # Inicializar a cadeia de perguntas e respostas (QA chain)
            self.create_talk_chain()

            if 'chain' in st.session_state:
                st.session_state['chain_initialized'] = True

    def chat_window(self):
        st.header('🤖 REALBOT - Assistente de Regras 🤖', divider=True)

        if 'chain_initialized' not in st.session_state:
            st.error('Inicialize o RealBOT para começar.')
            st.stop()

        # Inicializar o histórico de mensagens se ainda não existir
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []  # Armazenar as mensagens na sessão

        container = st.container()

        # Exibir o histórico de mensagens do chat
        for message in st.session_state['messages']:
            if message['role'] == 'human':
                container.chat_message('human').markdown(message['content'])
            else:
                container.chat_message('ai').markdown(message['content'])

        # Entrada de nova mensagem
        new_message = st.chat_input('Digite sua dúvida... e converse com o RealBOT')

        if new_message and new_message.strip():
            # Adicionar a mensagem do usuário ao histórico
            st.session_state['messages'].append({'role': 'human', 'content': new_message})
            container.chat_message('human').markdown(new_message)

            try:
                # Executar a cadeia de perguntas e respostas com base na nova pergunta
                chain = st.session_state['chain']
                documents = st.session_state['documents']
                
                # Executar a cadeia passando os documentos e a pergunta
                response = chain.run(input_documents=documents, question=new_message)

                # Adicionar a resposta do bot ao histórico
                st.session_state['messages'].append({'role': 'ai', 'content': response})
                container.chat_message('ai').markdown(response)

            except Exception as e:
                st.error(f"Erro ao processar a pergunta: {e}")
                st.session_state['messages'].append({'role': 'ai', 'content': f"Erro: {e}"})

        st.session_state['new_message'] = new_message

