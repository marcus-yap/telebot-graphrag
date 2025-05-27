import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TelegramChatFileLoader

load_dotenv()

def embed_telegram_chat():
    loader = TelegramChatFileLoader("./data/telegram_export/export.json")
    docs = loader.load()

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))
    persist_dir = "./data/vector_store/chroma_langchain_db"

    vector_store = Chroma.from_documents(documents = docs, embedding_function=embeddings, persist_directory=persist_dir)
    vector_store.persist()
    print("Vector store created and persisted successfully.")

if __name__ == "__main__":
    embed_telegram_chat()
    print("Embedding and indexing completed.")