from vector import retriver,lookup_customer
from vector_internet_issues import internet_issue_retriever
from vector_packages import internet_package_retriever
# from vector_package_scinarios import intent_scenario_retrievers
from langchain.tools import tool
import pandas as pd
from vector_store_lookup import store_retriever
@tool
def lookup_store_address(query: str) -> str:
    """
    Aramaya göre en uygun telekom mağazasını bulur.
    Mağaza adresi, telefon numarası, çalışma saatleri ve hizmetlerini döner.
    """
    print("LOOKUP STORE ADDRESS CALLED")
    results = store_retriever.invoke(query)
    if not results:
        return "Eşleşen mağaza bulunamadı."

    response_lines = []
    for doc in results:
        meta = doc.metadata
        response = (
            f"İlçe: {meta.get('ilce', 'N/A')}\n"
            f"İl: {meta.get('il', 'N/A')}\n"
            f"Adres: {meta.get('adres', 'N/A')}\n"
            f"Telefon: {meta.get('telefon', 'N/A')}\n"
            f"Çalışma Saatleri: {meta.get('calisma_saatleri', 'N/A')}\n"
            f"Hizmetler: {meta.get('hizmetler', 'N/A')}"
        )
        response_lines.append(response)

    return "\n---\n".join(response_lines)

print(lookup_store_address("Kadıköy telekom mağazası"))
