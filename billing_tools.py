from vector import retriver,lookup_customer
from vector_internet_issues import internet_issue_retriever
from vector_packages import internet_package_retriever
# from vector_package_scinarios import intent_scenario_retrievers
from langchain.tools import tool
import pandas as pd
import json
import csv
from datetime import datetime

@tool
def lookup_customer_bills(customer_id, limit=3, status=None, include_days_left=False):
    """
    Retrieve recent bill history for a given customer ID from a CSV file.
    Can filter by status and optionally calculate days left to pay.

    Args:
        customer_id (str): The unique ID of the customer.
        limit (int): How many months of history to return (default 3).
        status (str, optional): Filter by 'Paid' or 'Unpaid'.
        include_days_left (bool): If True, include days left to pay.

    Returns:
        list: A list of dictionaries containing month, amount, status, due_date, and optionally days left.
    """
    try:
        df = pd.read_csv('billing.csv')
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
        df["due_date"] = pd.to_datetime(df["due_date"], format="%Y-%m-%d")

        customer_bills = df[df["CustomerID"] == int(customer_id)].copy()
        if customer_bills.empty:
            return json.dumps({"error": f"No billing records found for customer ID: {customer_id}"}, ensure_ascii=False)

        if status:
            customer_bills = customer_bills[customer_bills["status"].str.lower() == status.lower()]

        customer_bills = customer_bills.sort_values(by="month", ascending=False).head(limit)

        bill_list = []
        for _, bill in customer_bills.iterrows():
            bill_info = {
                "month": bill["month"].strftime("%Y-%m"),
                "amount": bill["amount"],
                "status": bill["status"],
                "due_date": bill["due_date"].strftime("%Y-%m-%d")
            }
            if include_days_left and bill["status"].lower() == "unpaid":
                days_left = (bill["due_date"] - pd.Timestamp.now()).days
                bill_info["days_left_to_pay"] = max(days_left, 0)
            bill_list.append(bill_info)

        return json.dumps(bill_list, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@tool
def activate_autobiling(phone_number:str, Authorized:bool):

    """
    Activates autobilling for a customer if they are authorized.

    This tool updates the customer's roaming status in the database. Authorization
    must be verified using the `authorize_user` tool before calling this.

    Parameters:
        phone_number (str): The customer's registered phone number.
        Authorized (bool): Set to True if the user has been successfully authorized.

    Returns:
        dict: {
            "status": "success" | "unauthorized" | "not_found",
            "message": Human-readable summary,
            "data": autobilling status (e.g. {"autobilling": "Active"})
        }
    """
    customer = lookup_customer(phone_number)
    if not customer:
        return {
            "status": "not_found",
            "message": "No customer found with that phone number.",
            "data": None
        }

    if customer.get("AutoBilling", "").strip().lower() == "active":
        return {
            "status": "success",
            "message": "autobilling is already active.",
            "data": {"roaming": "Active"}
        }

    if not Authorized:
        return {
            "status": "unauthorized",
            "message": "User must be authorized before activating autobilling.",
            "data": None
        }

    rows = []
    found = False

    with open('customers_infor.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['PhoneNumber'] == phone_number:
                row['AutoBilling'] = 'Active'
                found = True
            rows.append(row)

    with open('customers_infor.csv', mode='w', newline='') as file:
        fieldnames = ["CustomerID", "Name", "PhoneNumber", "Email", "Address", "Package", "AccountStatus", "Roaming","is_Student","AutoBilling"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if found:
        return {
            "status": "success",
            "message": "Auto billing successfully activated for this number.",
            "data": {"Auto billing ": "Active"}
        }
    else:
        return {
            "status": "not_found",
            "message": f"No matching customer found to update autobilling for {phone_number}.",
            "data": None
        }

@tool
def check_autobilling_status(phone_number: str):
    """
    Checks the current autobilling status for a given customer.

    Parameters:
        phone_number (str): The customer's registered phone number.

    Returns:
        dict: {
            "status": "success" | "not_found",
            "message": Human-readable summary,
            "data": autobilling status (e.g. {"autobilling": "Active"})
        }
    """
    customer = lookup_customer(phone_number)
    if not customer:
        return {
            "status": "not_found",
            "message": "No customer found with that phone number.",
            "data": None
        }

    autobilling_status = customer.get("AutoBilling", "").strip() or "Inactive"
    return {
        "status": "success",
        "message": f"Autobilling status for {phone_number}: {autobilling_status}",
        "data": {"AutoBilling": autobilling_status}
    }
@tool
def deactivate_autobilling(phone_number: str, Authorized: bool):
    """
    Deactivates autobilling for a customer if they are authorized.

    Parameters:
        phone_number (str): The customer's registered phone number.
        Authorized (bool): Set to True if the user has been successfully authorized.

    Returns:
        dict: {
            "status": "success" | "unauthorized" | "not_found",
            "message": Human-readable summary,
            "data": autobilling status (e.g. {"AutoBilling": "Inactive"})
        }
    """
    customer = lookup_customer(phone_number)
    if not customer:
        return {
            "status": "not_found",
            "message": "No customer found with that phone number.",
            "data": None
        }

    if customer.get("AutoBilling", "").strip().lower() == "inactive":
        return {
            "status": "success",
            "message": "Autobilling is already inactive.",
            "data": {"AutoBilling": "Inactive"}
        }

    if not Authorized:
        return {
            "status": "unauthorized",
            "message": "User must be authorized before deactivating autobilling.",
            "data": None
        }

    rows = []
    found = False

    with open('customers_infor.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['PhoneNumber'] == phone_number:
                row['AutoBilling'] = 'Inactive'
                found = True
            rows.append(row)

    with open('customers_infor.csv', mode='w', newline='') as file:
        fieldnames = ["CustomerID", "Name", "PhoneNumber", "Email", "Address", "Package", "AccountStatus", "Roaming", "is_Student", "AutoBilling"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if found:
        return {
            "status": "success",
            "message": "Auto billing successfully deactivated for this number.",
            "data": {"AutoBilling": "Inactive"}
        }
    else:
        return {
            "status": "not_found",
            "message": f"No matching customer found to update autobilling for {phone_number}.",
            "data": None
        }

# Example usage
# customer_id = "11111"
# history = get_bill_history_from_csv.invoke({"customer_id": "11111", "limit": 3})

# if isinstance(history, list):
#     print(f"Billing history for customer {customer_id}:")
#     for bill in history:
#         print(f"- {bill['month'].strftime('%Y-%m')}: ${bill['amount']} ({bill['status']})")
# else:
#     print(history)