from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd
import json
# Load customer info
df = pd.read_csv('customers_infor.csv')
import pandas as pd

# Load once globally (you can optimize this with caching later)

# Initialize embeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Chroma DB path
db_location = "./chroma_langchain_db"
add_documents = not os.path.exists(db_location)

# Prepare documents if DB doesn't exist
if add_documents:
    documents = []
    ids = []
    for i, row in df.iterrows():
        document = Document(
            page_content=f"""
            Customer Name: {row['Name']}
            Phone Number: {row['PhoneNumber']}
            Email: {row['Email']}
            Address: {row['Address']}
            Package: {row['Package']}
            Account Status: {row['AccountStatus']}
            """.strip(),
            metadata={
                "id": row['CustomerID'],
                "name": row['Name'],
                "email": row['Email'],
                "phone": row['PhoneNumber'],
                "address": row['Address'],
                "package": row['Package'],
                "status": row['AccountStatus']
            },
            id=str(row['CustomerID'])
        )
        documents.append(document)
        ids.append(str(row['CustomerID']))

# Initialize Chroma vector store
vector_store = Chroma(
    collection_name="customers",
    persist_directory=db_location,
    embedding_function=embeddings
)

# Add documents if needed
if add_documents:
    vector_store.add_documents(documents, ids=ids)

# Set up retriever
retriver = vector_store.as_retriever(search_kwargs={"k": 1})


def lookup_customer(identifier: str):
    print("LOOKUP NESTED CALLED")
    identifier = str(identifier)
    print(identifier)
    matches = df[
        (df["PhoneNumber"].astype(str).str.lower() == identifier) |
        (df["Name"].astype(str).str.lower() == identifier) |
        (df["CustomerID"].astype(str).str.lower() == identifier)
    ]

    if matches.empty:
        print("no match found")
        return None

    return matches.iloc[0].to_dict()  # return the first match as a dict


# res =lookup_customer("555-1111")  # Example usage
# print(res)