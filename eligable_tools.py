from vector import retriver, lookup_customer
from vector_internet_issues import internet_issue_retriever
from vector_packages import internet_package_retriever
from langchain.tools import tool
import pandas as pd
import os
from vector_student import student_package_retriever
import csv

@tool
def check_if_student(phone_number: str):
    """
    Checks whether a customer is marked as a student in the database.

    Parameters:
        phone_number (str): The customer's registered phone number.

    Returns:
        dict: {
            "status": "success" | "not_found",
            "message": Human-readable summary,
            "data": Current student status (e.g. {"is student": "Yes" | "No" | "N/A"})
        }

    Notes:
        - "is_Student" field in the customer's record is used for this check.
        - Returns "N/A" if the field is missing.
    """
    customer = lookup_customer(phone_number)
    if not customer:
        return {
            "status": "not_found",
            "message": "No customer found with that phone number.",
            "data": None
        }

    is_student = customer.get("is_Student", "N/A")
    return {
        "status": "success",
        "message": f"Student status for {phone_number}: {is_student}.",
        "data": {"is student": is_student}
    }

@tool
def initiate_student_package(
    phone_n: str,
    current_package: str,
    student_package: str,
    is_student: bool,
    confirmation: bool
) -> str:
    """
    Uygun olan bir müşteri için öğrenci paketine geçiş işlemini başlatır.

    Parametreler:
        phone_n (str): Müşterinin kayıtlı telefon numarası.
        current_package (str): Müşterinin mevcut paketi.
        student_package (str): Geçiş yapılacak öğrenci paketi.
        is_student (bool): Müşteri öğrenci paketine uygun ise True.
        confirmation (bool): Müşteri paket değişikliğini onayladıysa True.

    Dönüş:
        str: İşlemin sonucunu açıklayan mesaj.

    Notlar:
        - Fonksiyon 'customers_infor.csv' dosyasını yeni paket bilgisi ile günceller.
        - Müşteri uygun değilse veya onay vermediyse herhangi bir değişiklik yapılmaz.
    """
    import csv
    rows = []
    found = False

    if not is_student:
        return "Müşteri öğrenci paketine uygun değil."

    if not confirmation:
        return "Müşteri, öğrenci paketine geçişi onaylamalıdır."

    with open('customers_infor.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['PhoneNumber'] == phone_n:
                row['Package'] = student_package
                found = True
            rows.append(row)

    with open('customers_infor.csv', mode='w', newline='') as file:
        fieldnames = ["CustomerID", "Name", "PhoneNumber", "Email", "Address", "Package", "AccountStatus", "Roaming","is_Student"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if found:
        return f"{phone_n} numaralı müşteri için paket {current_package} paketinden '{student_package}' paketine güncellendi."
    else:
        return f"{phone_n} numaralı müşteri bulunamadı."
@tool
def lookup_student_package(query: str) -> str:
    """
    Kullanıcının sorgusuna göre mevcut öğrenci paketlerini arar.
    Paket detayları ve özelliklerini döndürür.
    """
    print("STUDENT PACKAGE LOOKUP CALLED")
    results = student_package_retriever.invoke(query)
    if not results:
        return "Eşleşen öğrenci paketi bulunamadı."

    response_lines = []
    for doc in results:
        meta = doc.metadata
        response = (
            f"Paket: {meta.get('name', 'N/A')}\n"
            f"Fiyat: {meta.get('price', 'N/A')} TRY\n"
            f"Veri: {meta.get('data', 'N/A')}\n"
            f"Hız: {meta.get('speed', 'N/A')}\n"
            f"Geçerlilik: {meta.get('validity', 'N/A')}\n"
            f"Ekstra Özellikler: {meta.get('features', 'N/A')}"
        )
        response_lines.append(response)

    return "\n---\n".join(response_lines)

