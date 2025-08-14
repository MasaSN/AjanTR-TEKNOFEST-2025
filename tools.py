from vector import retriver,lookup_customer
from vector_internet_issues import internet_issue_retriever
from vector_packages import internet_package_retriever
# from vector_package_scinarios import intent_scenario_retrievers
from langchain.tools import tool
import pandas as pd
@tool
def lookup_internet_package(query: str) -> str:
    """
    Searches available internet packages based on user query .
    Returns package details and features.
    """
    print("LOOKUP INTERNET PACKAGE INFO CALLED")
    results = internet_package_retriever.invoke(query)
    if not results:
        return "No matching internet package found."

    response_lines = []
    for doc in results:
        meta = doc.metadata
        response = (
            f"Package: {meta.get('name', 'N/A')}\n"
            f"Price: {meta.get('price', 'N/A')} TRY\n"
            f"Data: {meta.get('data', 'N/A')}\n"
            f"Speed: {meta.get('speed', 'N/A')}\n"
            f"Validity: {meta.get('validity', 'N/A')}\n"
            f"Features: {meta.get('features', 'N/A')}"
        )
        response_lines.append(response)

    return "\n---\n".join(response_lines)

@tool
def retrive_customer_information(identifier: str, field: str) -> str:
    """
    Müşteri bilgilerini CSV dosyasından getirir.
    - 'identifier': Müşteri telefon numarası, e-posta veya ID
    - 'field': İstenen bilgi, ör. 'Package', 'Email', 'AccountStatus','CustomerID'.
      Tüm bilgileri almak için 'all' kullanın.
    """
    print("RETRIVE CUSTOMER INFO CALLED")
    
    print(field)
    customer = lookup_customer(identifier)

    if not customer:
        return "No matching customer found."

    if field != "all":
        value = customer.get(field)
        if value:
            return f"{field.title()}: {value}"
        else:
            return f"No value found for field '{field}'."

    # Return full customer info
    return (
    f"Müşteri ID: {customer.get('CustomerID','N/A')}\n"
    f"Müşteri Adı: {customer.get('Name', 'N/A')}\n"
    f"Paket: {customer.get('Package', 'N/A')}\n"
    f"Hesap Durumu: {customer.get('AccountStatus', 'N/A')}\n"
    f"Telefon: {customer.get('PhoneNumber', 'N/A')}\n"
    f"E-posta: {customer.get('Email', 'N/A')}\n"
    f"Adres: {customer.get('Address', 'N/A')}\n"
    f"Dolaşım: {customer.get('Roaming','N/A')}"
)



@tool
def lookup_internet_issue(query: str) -> str:
    """
    İnternet bağlantısı ile ilgili yaygın sorunları arar ve olası nedenler ile çözümlerini sunar.
    Girdi, sorunun kısa bir açıklaması olmalıdır, örneğin: 'yavaş internet' veya 'wifi çalışmıyor'.
    """
    print("İNTERNET SORUNU ARAMA METODU ÇAĞRILDI")
    results = internet_issue_retriever.invoke(query)
    if not results:
        return "Verilen açıklama için ilgili bir internet sorunu bulunamadı."

    responses = []
    for doc in results:
        meta = doc.metadata
        response = (
            f"Sorun Kategorisi: {meta.get('category', 'N/A')}\n"
            f"Açıklama: {meta.get('description', 'N/A')}\n"
            f"Olası Neden: {meta.get('cause', 'N/A')}\n"
            f"Önerilen Çözüm: {meta.get('solution', 'N/A')}"
        )
        responses.append(response)
    
    return "\n---\n".join(responses)

import csv

@tool
def initiate_package_change(phone_n: str,current_package:str, wanted_package: str,isPackage_available:bool, confirmation:bool) -> str:
    """
    Changes the package of the user to another from the available packages. you can find the available packages using the tool lookup_internet_package
    It takes the user's phone number, the package they want, and their confirmation and updates their package.
    """
    print("INITIATE PACKAGE CHANGE CALLED")
    rows = []
    found = False
    if not confirmation :
        return "the user must confirm switching packages "
    if not isPackage_available:
        return "istedigi paketim mevcut degil"
    with open('customers_infor.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row['PhoneNumber'] == phone_n:
                row['Package'] = wanted_package
                found = True
            rows.append(row)

    # Write back the updated data
    with open('customers_infor.csv', mode='w', newline='') as file:
        fieldnames = ["CustomerID", "Name", "PhoneNumber", "Email", "Address", "Package", "AccountStatus","Roaming"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if found:
        return f"Package updated from {current_package} to '{wanted_package}' for {phone_n}."
    else:
        return f"No customer found with phone number {phone_n}."    

# activating Roaming
@tool
def activate_roaming(phone_number: str, Authorized: bool):
    """
    Activates international roaming for a customer if they are authorized.

    This tool updates the customer's roaming status in the database. Authorization
    must be verified using the `authorize_user` tool before calling this.

    Parameters:
        phone_number (str): The customer's registered phone number.
        Authorized (bool): Set to True if the user has been successfully authorized.

    Returns:
        dict: {
            "status": "success" | "unauthorized" | "not_found",
            "message": Human-readable summary,
            "data": Roaming status (e.g. {"roaming": "Active"})
        }
    """
    customer = lookup_customer(phone_number)
    if not customer:
        return {
            "status": "not_found",
            "message": "No customer found with that phone number.",
            "data": None
        }

    if customer.get("Roaming", "").strip().lower() == "active":
        return {
            "status": "success",
            "message": "International roaming is already active.",
            "data": {"roaming": "Active"}
        }

    if not Authorized:
        return {
            "status": "unauthorized",
            "message": "User must be authorized before activating roaming.",
            "data": None
        }

    rows = []
    found = False

    with open('customers_infor.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['PhoneNumber'] == phone_number:
                row['Roaming'] = 'Active'
                found = True
            rows.append(row)

    with open('customers_infor.csv', mode='w', newline='') as file:
        fieldnames = ["CustomerID", "Name", "PhoneNumber", "Email", "Address", "Package", "AccountStatus", "Roaming","is_Student"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if found:
        return {
            "status": "success",
            "message": "Roaming successfully activated for this number.",
            "data": {"roaming": "Active"}
        }
    else:
        return {
            "status": "not_found",
            "message": f"No matching customer found to update roaming for {phone_number}.",
            "data": None
        }

@tool
def authorize_user(last_4_digits_of_id: str, phone_number: str):
    """
    Verifies that the user is authorized by matching the last 4 digits of their ID 
    with the CustomerID in the system.

    Use this tool to check if the user is verified before allowing any account changes.

    Parameters:
        last_4_digits_of_id (str): Last 4 digits of the user's government ID.
        phone_number (str): The customer's registered phone number.

    Returns:
        dict: {
            "status": "success" | "unauthorized" | "not_found",
            "message": Human-readable summary,
            "data": Authorization result (e.g. {"authorized": True})
        }
    """
    customer = lookup_customer(phone_number)
    if customer == None:
        return {
            "status": "not_found",
            "message": "Customer not found. Cannot authorize.",
            "data": None
        }
    customer_id = str(customer.get("CustomerID", ""))
    if customer_id[-4:] != last_4_digits_of_id:
        return {
            "status": "unauthorized",
            "message": "The last 4 digits do not match.",
            "data": None
        }

    return {
        "status": "success",
        "message": "User successfully authorized.",
        "data": {"authorized": True}
    }
import csv
from typing import Dict
from langchain.tools import tool

@tool
def update_customer_information(identifier: str, updates: Dict[str, str], confirmation: bool) -> str:
    """
    Müşteri bilgilerini CSV dosyasında günceller.
    
    - identifier: Müşteriyi tanımlamak için kullanılan değer.'PhoneNumber','Email', 'Address', 'AccountStatus' gibi CSV sütun adları ile eşleşen bir değer olmalıdır.
    - updates: Güncellenecek alan(lar) ve yeni değer(ler) sözlüğü.
               Örnek: {"Package": "Premium", "AccountStatus": "Active"}
               Buradaki anahtarlar CSV dosyasındaki sütun adlarıyla (İngilizce) aynı olmalıdır.
    - confirmation: 'True' ise güncelleme yapılır, aksi halde işlem durdurulur.
    
    Döndürür: Güncelleme başarılı veya hata mesajı.
    """
    print("UPDATE CUSTOMER INFORMATION CALLED")
    
    if not confirmation:
        return "Kullanıcı, bilgilerin güncellenmesini onaylamalıdır."
    
    rows = []
    found = False
    
    with open('customers_infor.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # identifier, CSV içindeki herhangi bir alanın değeriyle eşleşirse
            if identifier in row.values():
                for key, value in updates.items():
                    if key in row:
                        row[key] = value
                found = True
            rows.append(row)
    
    if not found:
        return f"'{identifier}' bilgisine sahip müşteri bulunamadı."
    
    # Güncellenmiş verileri CSV'ye yaz
    with open('customers_infor.csv', mode='w', newline='') as file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return f"Müşteri '{identifier}' bilgileri başarıyla güncellendi: {updates}"

def pay_bill():
    """
    Fatura ödeme işlemi için kullanıcıya bilgi verir.
    
    Online veya CSV üzerinden ödeme yapılamaz. Kullanıcıya,
    faturayı yalnızca mevcut adreslerimizde ödeyebileceğini bildirir.
    
    Döndürür: Bilgilendirme mesajı.
    """
    print("PAY BILL FUNCTION CALLED")
    return "You can only pay bills in person at our available addresses."

# print(res)
# res =activate_roaming("555-1234",True)
# print(res)