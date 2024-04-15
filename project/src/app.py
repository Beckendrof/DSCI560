import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import HuggingFaceHub
from htmlTemplates import css, bot_template, user_template
from dotenv import load_dotenv
from youtube import *
import shutil
import spacy
import os
from langchain import OpenAI

load_dotenv()
nlp = spacy.load("en_core_web_sm")

@st.cache_data
def delete_image_if_exists(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted folder at path: {folder_path}")

    os.makedirs(folder_path)
    print(f"Created folder at path: {folder_path}")

def preprocess_text(text):
    lines = text.split("\n")
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    processed_text = "\n".join(lines)
    if len(processed_text) > 480:
        return processed_text[:480]
    return processed_text

def preprocess_chunks(chunks):
    preprocessed_chunks = []
    for chunk in chunks:
        preprocessed_chunk = preprocess_text(chunk)
        preprocessed_chunks.append(preprocessed_chunk)
        if len(preprocessed_chunk) > 480:
            print(f"Warning: Chunk length exceeds 480 characters after preprocessing. Length: {len(preprocessed_chunk)}")
    return preprocessed_chunks

@st.cache_data
def get_text_chunks():
    with open('../data/piazza_data.txt', 'r', encoding='utf-8') as file:
        piazza_data = file.read()

    with open('../data/machine_learning.txt', 'r', encoding='utf-8') as file:
        wiki_data = file.read()

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(piazza_data + wiki_data)
    chunks = preprocess_chunks(chunks)
    return chunks

@st.cache_data
def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = OpenAI(
        temperature=0,
        api_key=os.environ.get("OPENAI_API_KEY"),
        model_name="gpt-3.5-turbo-1106"
    )

    # llm = HuggingFaceHub(repo_id="CohereForAI/c4ai-command-r-plus", model_kwargs={"temperature":0.5, "max_length":500}, huggingfacehub_api_token=os.environ.get("HUGGINGFACE_API_KEY"))
    
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}),
        memory=memory,
    )
    return conversation_chain

@st.cache_data
def cache_timestamps(data):
    return data

def handle_userinput(user_question, selected_chat):
    response = st.session_state.chats[selected_chat]["conversation"]({'question': user_question})
    st.session_state.chats[selected_chat]["chat_history"] = response['chat_history']
    st.session_state.chats[selected_chat]["timestamps"].extend([0, get_frame(user_question)])
    print_chat_history(selected_chat)
        
def print_chat_history(selected_chat):
    token=(False, None)

    for i, message in enumerate(st.session_state.chats[selected_chat]["chat_history"]):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
            if os.path.exists(f"conversation_images/{message.content}.jpg"):
                token=(True, message.content)
        else:
            if token[0] and st.session_state.chats[selected_chat]["timestamps"][i][1]:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                st.image(
                    f"conversation_images/{token[1]}.jpg", 
                    caption=f"https://www.youtube.com/watch?v={st.session_state.chats[selected_chat]['timestamps'][i][1]}&t={int(st.session_state.chats[selected_chat]['timestamps'][i][0])}"
                    )
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            token=(False, None)


def main():
    st.set_page_config(page_title="Chat",
                       page_icon=":teacher:")
    delete_image_if_exists("conversation_images")
    load_dotenv()
    st.write(css, unsafe_allow_html=True)

    text_chunks = get_text_chunks()
    vectorstore = get_vectorstore(text_chunks)

    st.header("Chat with TA", anchor=False)
    if "chats" not in st.session_state:
        st.session_state.chats = {}
    st.session_state.chats[f"Chat 1"] = {
        "conversation": None,
        "chat_history": [],
        "timestamps": []
    }
    if st.sidebar.button("New Chat", key="new_chat_button"):
        number = len(st.session_state.chats.keys())
        st.session_state.chats[f"Chat {number+1}"] = {
            "conversation": None,
            "chat_history": [],
            "timestamps": []
        }

    selected_chat = None
    st.sidebar.header("Chats")
    for chat_name in st.session_state.chats.keys():
        if st.sidebar.button(chat_name, key=f"chat_{chat_name}"):
            selected_chat = chat_name
            print_chat_history(selected_chat)

    if not selected_chat:
        selected_chat = next(iter(st.session_state.chats))

    with st.spinner("Processing"):
        if st.session_state.chats[selected_chat]["conversation"] is None:
            st.session_state.chats[selected_chat]["conversation"]  = get_conversation_chain(
                vectorstore)

    user_question = st.text_input(label="", placeholder="Ask questions", key="user_question")
    if user_question:
        handle_userinput(user_question, selected_chat)


if __name__ == '__main__':
    main()
