from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import pandas as pd
import os

# Load internet packages data
df = pd.read_csv("internet_packages.csv")

# Initialize embeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Define Chroma DB path
db_path = "./chroma_internet_packages_db"
add_documents = not os.path.exists(db_path)

# Create documents if DB doesn't exist
if add_documents:
    documents = []
    ids = []

    for _, row in df.iterrows():
        content = f"""
        Package Name: {row['Name']}
        Price: {row['Price (TRY)']} TRY
        Data Allowance: {row['Data Allowance']}
        Validity: {row['Validity']}
        Speed Limit: {row['Speed Limit']}
        Additional Features: {row['Additional Features']}
        """.strip()

        doc = Document(
            page_content=content,
            metadata={
                "id": row["Package ID"],
                "name": row["Name"],
                "price": row["Price (TRY)"],
                "data": row["Data Allowance"],
                "validity": row["Validity"],
                "speed": row["Speed Limit"],
                "features": row["Additional Features"]
            },
            id=str(row["Package ID"])
        )
        documents.append(doc)
        ids.append(str(row["Package ID"]))

# Initialize vector store
vector_store = Chroma(
    collection_name="internet_packages",
    persist_directory=db_path,
    embedding_function=embeddings
)

# Add documents if new
if add_documents:
    vector_store.add_documents(documents, ids=ids)

# Set up retriever
internet_package_retriever = vector_store.as_retriever(search_kwargs={"k": 2})
