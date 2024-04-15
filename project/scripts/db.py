import chromadb
from chromadb.config import Settings
from langchain.text_splitter import CharacterTextSplitter

client = chromadb.PersistentClient(
    path="db/", 
    settings=Settings(anonymized_telemetry=False))

def create_or_replace_collection(name):
    try:
        return client.get_collection(name)
    except:
        return client.create_collection(name=name)

collection = create_or_replace_collection("piazza_data")

with open('piazza_data.txt', 'r', encoding='utf-8') as file:
    piazza_data = file.read()

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

chunks = get_text_chunks(piazza_data)

for i, chunk in enumerate(chunks):
    collection.add(
        documents=[chunk],
        metadatas=[{"source": f"piazza_data_{i+1}"}],
        ids=[f"id{i+1}"]
    )