# import json
# from langchain_core.documents import Document
# from langchain_chroma import Chroma
# from langchain_ollama import OllamaEmbeddings

# # --- Load your JSON file ---
# with open("package_change_scenarios.json", "r", encoding="utf-8") as f:
#     scenario_data = json.load(f)

# # --- Convert to LangChain documents ---
# documents = []
# for scenario in scenario_data:
#     content = f"""
#     Title: {scenario['title']}
#     Description: {scenario['description']}
#     Steps: {" -> ".join(scenario['steps'])}
#     """
#     doc = Document(
#         page_content=content.strip(),
#         metadata={"intent": scenario["intent"]}
#     )
#     documents.append(doc)

# # --- Embed with Ollama ---
# embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
# vector_store = Chroma(
#     collection_name="intent_scenarios",
#     embedding_function=embedding_model
# )

# # --- Add the documents to the store ---
# vector_store.add_documents(documents)

# # --- Use as retriever ---
# intent_scenario_retriever = vector_store.as_retriever(search_kwargs={"k": 1})

# # user_input = "cancel"  # example in Turkish

# # retrieved_doc = intent_scenario_retriever.invoke(user_input)

# # if retrieved_doc:
# #     print("Matched Intent:", retrieved_doc[0].metadata["intent"])
# #     print("Steps to perform:")
# #     print(retrieved_doc[0].page_content)
