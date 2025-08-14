from vector import retriver, lookup_customer
from vector_internet_issues import internet_issue_retriever
from vector_packages import internet_package_retriever
from langchain.tools import tool
import pandas as pd
import os

import csv
@tool
def check_roaming_status(phone_number: str):
    """
    Checks the international roaming status for a customer.

    Parameters:
        phone_number (str): The customer's registered phone number.

    Returns:
        dict: {
            "status": "success" | "not_found",
            "message": Human-readable summary,
            "data": Current roaming status (e.g. {"roaming": "Active"})
        }
    """
    customer = lookup_customer(phone_number)
    if not customer:
        return {
            "status": "not_found",
            "message": "No customer found with that phone number.",
            "data": None
        }

    roaming_status = customer.get("Roaming", "Unknown")
    return {
        "status": "success",
        "message": f"Roaming status for {phone_number}: {roaming_status}.",
        "data": {"roaming": roaming_status}
    }
@tool
def deactivate_roaming(phone_number: str, Authorized: bool):
    """
    Deactivates international roaming for a customer if they are authorized.

    Parameters:
        phone_number (str): The customer's registered phone number.
        Authorized (bool): Set to True if the user has been successfully authorized.

    Returns:
        dict: {
            "status": "success" | "unauthorized" | "not_found",
            "message": Human-readable summary,
            "data": Roaming status (e.g. {"roaming": "Inactive"})
        }
    """
    customer = lookup_customer(phone_number)
    if not customer:
        return {
            "status": "not_found",
            "message": "No customer found with that phone number.",
            "data": None
        }

    if customer.get("Roaming", "").strip().lower() == "inactive":
        return {
            "status": "success",
            "message": "International roaming is already inactive.",
            "data": {"roaming": "Inactive"}
        }

    if not Authorized:
        return {
            "status": "unauthorized",
            "message": "User must be authorized before deactivating roaming.",
            "data": None
        }

    rows = []
    found = False

    with open('customers_infor.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['PhoneNumber'] == phone_number:
                row['Roaming'] = 'Inactive'
                found = True
            rows.append(row)

    with open('customers_infor.csv', mode='w', newline='') as file:
        fieldnames = ["CustomerID", "Name", "PhoneNumber", "Email", "Address", "Package", "AccountStatus", "Roaming"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if found:
        return {
            "status": "success",
            "message": "Roaming successfully deactivated for this number.",
            "data": {"roaming": "Inactive"}
        }
    else:
        return {
            "status": "not_found",
            "message": f"No matching customer found to update roaming for {phone_number}.",
            "data": None
        }
