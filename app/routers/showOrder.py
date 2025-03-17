import requests
import os
from fastapi import APIRouter, HTTPException, Header
from app.models import EncryptedDataRequest
from dotenv import load_dotenv
from app.utility.encryption_utils import decrypt_aes256

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_URL = "https://zmvjylvafmgqpxqtrblc.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inptdmp5bHZhZm1ncXB4cXRyYmxjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyMzQ4OTgxMiwiZXhwIjoyMDM5MDY1ODEyfQ.5cdLeGHxXVoEqmrF27N1d1oDmTWdzbZmKeo4yCusSn0"
ORDERS_URL = f"{SUPABASE_URL}/rest/v1/rpc/Orders"

# Initialize FastAPI Router
router = APIRouter()


def process_orders_response(decrypted_data, authtokens):
    """Calls Supabase function, processes response, and handles errors."""
    headers = {
        "Authorization": f"Bearer {authtokens}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    # Extract required fields
    if "userid" not in decrypted_data:
        raise HTTPException(status_code=400, detail="Missing required field: userid")

    userid = decrypted_data["userid"]

    payload = {"userid": userid}

    response = requests.post(ORDERS_URL, json=payload, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    # return response_data
    # Step 2: Check if Supabase returned success (code == 101)
    if isinstance(response_data, list):
        return {
            "message": "Orders retrieved successfully",
            "status": True,
            "code": 101,
            "orders": response_data  # Assuming Supabase returns orders in 'data'
        }

    # Step 3: Handle other responses as errors
    error_message = "abc"
    raise HTTPException(status_code=response.status_code, detail=error_message)


@router.post("/orders")
async def fetch_orders(request: EncryptedDataRequest, authtoken: str = Header(...)):
    """Decrypts encrypted data, extracts fields, and fetches orders from Supabase."""
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
    supabase_response = process_orders_response(decrypted_data, authtokens["details"])

    # Step 3: Return the processed response
    return supabase_response
