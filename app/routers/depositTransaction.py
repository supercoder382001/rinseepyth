import requests
import os
from fastapi import APIRouter, HTTPException, Header
from app.models import EncryptedDataRequest
from dotenv import load_dotenv
from app.utility.encryption_utils import decrypt_aes256

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DEPOSIT_TRANSACTION_URL = f"{SUPABASE_URL}/rest/v1/rpc/DepositTransaction"

# Initialize FastAPI Router
router = APIRouter()


def process_deposit_transaction(decrypted_data, authtokens):
    """Calls Supabase function, processes response, and handles errors."""
    headers = {
        "Authorization": f"Bearer {authtokens}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    # Extract required fields
    if not all(key in decrypted_data for key in ["amount", "orderid", "userid"]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    amount = decrypted_data["amount"]
    orderid = decrypted_data["orderid"]
    userid = decrypted_data["userid"]

    payload = {
        "amount": amount,
        "orderid": orderid,
        "userid": userid
    }

    response = requests.post(DEPOSIT_TRANSACTION_URL, json=payload, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    # Step 2: Check if Supabase returned success (code == 101)
    if isinstance(response_data, dict):
        return {
            "message": "Deposit transaction successful",
            "status": True,
            "code": 101
        }

    # Step 3: Handle other responses as errors
    error_message = response_data.get("message", "Supabase function call failed")
    raise HTTPException(status_code=response.status_code, detail=error_message)


@router.post("/deposit-transaction")
async def deposit_transaction(request: EncryptedDataRequest, authtoken: str = Header(...)):
    """Decrypts encrypted data, extracts fields, and processes the deposit transaction."""
    try:
        authtokens = decrypt_aes256(authtoken)
    except Exception:
        raise HTTPException(status_code=401, detail="Failed to decrypt authtoken")

    # Step 1: Decrypt the AES-256 encrypted data
    try:
        decrypted_data = decrypt_aes256(request.encrypted_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt data")

    # Step 2: Get response from Supabase
    supabase_response = process_deposit_transaction(decrypted_data, authtokens["details"])

    # Step 3: Return the processed response
    return supabase_response
