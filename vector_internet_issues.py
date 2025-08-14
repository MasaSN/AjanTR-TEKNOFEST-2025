from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import pandas as pd
import os

# Load internet issue data
df_issues = pd.read_csv("internet_issues.csv")

# Initialize embeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Chroma DB path
issues_db_path = "./chroma_internet_issues_db"
add_documents = not os.path.exists(issues_db_path)

# Create documents from CSV
if add_documents:
    issue_documents = []
    issue_ids = []

    for _, row in df_issues.iterrows():
        content = f"""
        Issue Category: {row['IssueCategory']}
        Description: {row['IssueDescription']}
        Cause: {row['PossibleCause']}
        Solution: {row['SuggestedSolution']}
        """.strip()
        
        doc = Document(
            page_content=content,
            metadata={
                "category": row['IssueCategory'],
                "description": row['IssueDescription'],
                "cause": row['PossibleCause'],
                "solution": row['SuggestedSolution']
            },
            id=str(row['IssueID'])
        )
        issue_documents.append(doc)
        issue_ids.append(str(row['IssueID']))

# Initialize vector store
issues_vector_store = Chroma(
    collection_name="internet_issues",
    persist_directory=issues_db_path,
    embedding_function=embeddings
)

# Add documents
if add_documents:
    issues_vector_store.add_documents(issue_documents, ids=issue_ids)

# Create retriever
internet_issue_retriever = issues_vector_store.as_retriever(search_kwargs={"k": 2})
