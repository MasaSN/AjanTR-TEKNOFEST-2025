import pandas as pd
import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Load student packages data
df_student = pd.read_csv("student_packages.csv")

# Initialize embeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Define Chroma DB path for student packages
student_db_path = "./chroma_student_packages_db"
add_documents = not os.path.exists(student_db_path)

# Create documents if DB doesn't exist
if add_documents:
    documents = []
    ids = []

    for _, row in df_student.iterrows():
        content = f"""
        Paket Adı: {row['Name']}
        Fiyat: {row['Price (TRY)']} TRY
        Veri: {row['Data Allowance']}
        Geçerlilik: {row['Validity']}
        Hız: {row['Speed Limit']}
        Ekstra Özellikler: {row['Additional Features']}
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
student_vector_store = Chroma(
    collection_name="student_packages",
    persist_directory=student_db_path,
    embedding_function=embeddings
)

# Add documents if new
if add_documents:
    student_vector_store.add_documents(documents, ids=ids)

# Set up retriever
student_package_retriever = student_vector_store.as_retriever(search_kwargs={"k": 2})
