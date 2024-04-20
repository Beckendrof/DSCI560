import streamlit as st
from htmlTemplates import css, bot_template, user_template
from dotenv import load_dotenv
from scripts.youtube import *
from scripts.search_keywords import *
import shutil
import pickle
import timeit
from PIL import Image
import os

load_dotenv()

@st.cache_data
def delete_image_if_exists(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted folder at path: {folder_path}")

    os.makedirs(folder_path)
    print(f"Created folder at path: {folder_path}")

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']
    st.session_state.timestamps.extend([0, get_frame(user_question)])
    page_num, pdf_name, img_path = check_slides(user_question)
    token=(False, None)

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
            if os.path.exists(f"conversation_images/{message.content}.jpg"):
                token=(True, message.content)
        else:
            if token[0] and st.session_state.timestamps[i][1]:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                st.image(
                    f"conversation_images/{token[1]}.jpg", 
                    caption=f"https://www.youtube.com/watch?v={st.session_state.timestamps[i][1]}&t={int(st.session_state.timestamps[i][0])}"
                    )
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            token=(False, None)

    if page_num is not None:
        st.write(f"Page {page_num} of {pdf_name} contains information related to your question.")
        st.write(f"Image Path: {img_path}")
        img = Image.open(img_path)
        st.image(img, caption=f"Page {page_num} of {pdf_name}")

def load_conversation_chain(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data

def main():
    st.set_page_config(page_title="Chat",
                       page_icon=":teacher:")
    delete_image_if_exists("conversation_images")
    load_dotenv()
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "timestamps" not in st.session_state:
        st.session_state.timestamps = []
    if "slides" not in st.session_state:
        st.session_state.slides = None


    st.header("Chat with TA", anchor=False)

    with st.spinner("Processing"):
        if st.session_state.conversation is None:
            st.session_state.conversation  = load_conversation_chain("../data/conversation_chain.pickle")

    user_question = st.text_input(label="", placeholder="Ask questions", key="user_question")
    if user_question:
        handle_userinput(user_question)

if __name__ == '__main__':
    main()
