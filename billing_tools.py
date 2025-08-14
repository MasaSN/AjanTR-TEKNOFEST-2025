from vector import retriver,lookup_customer
from vector_internet_issues import internet_issue_retriever
from vector_packages import internet_package_retriever
# from vector_package_scinarios import intent_scenario_retrievers
from langchain.tools import tool
import pandas as pd
import json
import pandas as pd
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


# Example usage
# customer_id = "11111"
# history = get_bill_history_from_csv.invoke({"customer_id": "11111", "limit": 3})

# if isinstance(history, list):
#     print(f"Billing history for customer {customer_id}:")
#     for bill in history:
#         print(f"- {bill['month'].strftime('%Y-%m')}: ${bill['amount']} ({bill['status']})")
# else:
#     print(history)