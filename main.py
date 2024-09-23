from pathlib import Path
from gui.streamlit import Gui
from utils.utils import Utils
import streamlit as st
import os

PATH_INPUT_FILES = os.path.join(os.path.dirname(__file__), 'input')

def main():
    # Instanciar a classe Utils e Gui
    utils_instance = Utils(PATH_INPUT_FILES)
    gui_instance = Gui(PATH_INPUT_FILES, utils_instance)

    # Sidebar contendo a inicialização do bot
    with st.sidebar:
        gui_instance.sidebar()
    
    # Chamar a janela principal do chat fora do bloco 'with st.sidebar'
    gui_instance.chat_window()

if __name__ == '__main__':
    main()
