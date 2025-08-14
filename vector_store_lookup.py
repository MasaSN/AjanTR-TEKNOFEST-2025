from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import pandas as pd
import os

# Load store data
df = pd.read_csv("stores.csv")

# Initialize embeddings (Turkish-compatible)
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Define Chroma DB path
db_path = "./chroma_telekom_magazalar_db"
add_documents = not os.path.exists(db_path)

# Create documents if DB doesn't exist
if add_documents:
    documents = []
    ids = []

    for idx, row in df.iterrows():
        content = f"""
        İlçe: {row['İlçe']}
        İl: {row['İl']}
        Adres: {row['Adres']}
        Telefon: {row['Telefon']}
        Çalışma Saatleri: {row['ÇalışmaSaatleri']}
        Hizmetler: {row['Hizmetler']}
        """.strip()

        doc = Document(
            page_content=content,
            metadata={
                "ilce": row["İlçe"],
                "il": row["İl"],
                "adres": row["Adres"],
                "telefon": row["Telefon"],
                "calisma_saatleri": row["ÇalışmaSaatleri"],
                "hizmetler": row["Hizmetler"]
            },
            id=str(idx)
        )
        documents.append(doc)
        ids.append(str(idx))

# Initialize vector store
vector_store = Chroma(
    collection_name="telekom_magazalar",
    persist_directory=db_path,
    embedding_function=embeddings
)

# Add documents if new
if add_documents:
    vector_store.add_documents(documents, ids=ids)

# Set up retriever
store_retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# Example semantic search

