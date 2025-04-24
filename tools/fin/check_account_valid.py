from pathlib import Path
import json
import random

# this is made to demonstrate functionality but it could just as durably be an API call
# called as part of a temporal activity with automatic retries
def check_account_valid(args: dict) -> dict:
    
    email = args.get("email")
    account_id = args.get("account_id")

    # throw an error here sometimes to simulate failure
    if isErrorOften() :
         raise RuntimeError(f"FinAPI Simulated Exception: Getting Balances for {account_id} failed.!")

    file_path = Path(__file__).resolve().parent.parent / "data" / "customer_account_data.json"
    if not file_path.exists():
        return {"error": "Data file not found."}
    
    with open(file_path, "r") as file:
        data = json.load(file)
    account_list = data["accounts"]

    for account in account_list:
        if account["email"] == email or account["account_id"] == account_id:
            return{"status": "account valid"}
        
    return_msg = "Account not found with email address " + email + " or account ID: " + account_id
    return {"error": return_msg}

def isErrorRarely() -> bool:
    if random.randint(1, 10) > 9 :
        return True    
    return False

def isErrorOften() -> bool:
    if random.randint(1, 10) > 7 :
        return True    
    return False