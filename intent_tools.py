from langchain.tools import tool
import pandas as pd
from langchain_chroma import Chroma
import json
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from datetime import datetime
from datetime import datetime, timezone
embedding = OllamaEmbeddings(model="mxbai-embed-large")
vectorstore = Chroma(
    collection_name="intent_memory",
    persist_directory="./chroma_store_longterm_memory",  # saved on disk
    embedding_function=embedding,
)

user_id = '55555'

@tool
def saving_intent(message: str, intent: str,sensitive_info: bool, entities: dict = {} ) -> dict:
    """Use this tool to save the user's intent and related information.

Parameters:
- message (str): The original user message.
- intent (str): A short label describing the user's goal or request.
- sensitive_info (bool): MUST be set to either True or False.
    - True if the message contains personal, identifying, or sensitive data 
      (e.g., ID number, phone number, address, financial info).
    - False if the message contains no sensitive information.
- isCasual_message (bool): Must be set to either True or False
    - True if the message is a greeting or thanking or does not provide a request or a concern
- entities (dict, optional): A dictionary of extracted relevant details 
  (e.g., {"package": "Gold"}, {"roaming_type": "international"}).

Only call this tool when:
- The user expresses a clear request or goal (e.g., asking for help, changing settings, requesting account info).
- You have identified the intent and any relevant entities.
- You have evaluated whether the content is sensitive and set sensitive_info accordingly.

This tool stores the intent in long-term memory for future reference.
If sensitive_info=True, do NOT save the data—return a message instead.
"""
    # if isCasual_message:
    #     return {
    #         "status": "error",
    #         "reason": "The input is a casual message and there is no need to save it.",
    #         "saved": False
    #     }
    if sensitive_info:
        return {
            "status": "error",
            "reason": "The input contains sensitive information and cannot be saved.",
            "saved": False
        }


    if entities is None:
        entities = {}
    memory_text = f"{intent.lower().strip()} - {message.strip().lower()}"
    now = datetime.now(timezone.utc) 
    doc = Document(
        page_content=memory_text,
        metadata={
            "intent": intent,
            "entities": json.dumps(entities),
            "timestamp": now.isoformat(),
            "user_id": user_id
        }
    )
    vectorstore.add_documents([doc])

    print("SAVING INTET TOOL CALLED")
    print("params-text: ",message)
    print("params-intent: ",intent,entities)
    print("params-entities",entities)
    return{
        "message":message,
        "intent": intent,
        "entities":entities
    }

def retrieve_long_term_memory(user_input: str,user_intent:str, user_id: str, top_k: int = 5):
    """
    Retrieve similar past interactions for a given user from long-term memory (ChromaDB).
    
    Args:
        user_input (str): The current message or query.
        user_id (str): The ID of the user.
        top_k (int): How many similar entries to return.

    Returns:
        List[Document]: Top-k similar memory documents for the user.
    """
    # Perform similarity search
    search_query = f"{user_intent.strip().lower()} {user_input.strip().lower()}"

    all_results = vectorstore.similarity_search(search_query, k=top_k)

    # Filter results for this specific user
    filtered_results = [
        doc for doc in all_results 
        if doc.metadata.get("user_id") == user_id
    ]

    return filtered_results

# res =retrieve_long_term_memory("I would like to change my package", "change package", "1")
# print(res)