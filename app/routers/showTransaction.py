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
SHOW_TRANSACTIONS_URL = f"{SUPABASE_URL}/rest/v1/rpc/ShowTransactions"

# Initialize FastAPI Router
router = APIRouter()


def fetch_transactions_response(decrypted_data, authtokens):
    """Calls Supabase function, processes response, and handles errors."""
    headers = {
        "Authorization": f"Bearer {authtokens}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    # Extract required field
    if "userid" not in decrypted_data:
        raise HTTPException(status_code=400, detail="Missing required field: 'userid'")

    userid = decrypted_data["userid"]

    payload = {"userid": userid}

    response = requests.post(SHOW_TRANSACTIONS_URL, json=payload, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    # Step 2: Check if Supabase returned success (code == 101)
    if isinstance(response_data, dict) or isinstance(response_data, list):
        return {
            "message": "Transactions fetched successfully",
            "status": True,
            "code": 101,
            "transactions": response_data
        }

    # Step 3: Handle other responses as errors
    error_message = response_data.get("message", "Supabase function call failed")
    raise HTTPException(status_code=response.status_code, detail=error_message)


@router.post("/showTransactions")
async def show_transactions(request: EncryptedDataRequest, authtoken: str = Header(...)):
    """Decrypts encrypted data, extracts fields, and fetches transactions from Supabase."""
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
    supabase_response = fetch_transactions_response(decrypted_data, authtokens["details"])

    # Step 3: Return the processed response
    return supabase_response
