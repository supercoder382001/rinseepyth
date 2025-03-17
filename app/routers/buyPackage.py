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
PACKAGE_URL = f"{SUPABASE_URL}/rest/v1/rpc/package"

# Initialize FastAPI Router
router = APIRouter()


def process_package_response(decrypted_data, authtokens):
    """Calls Supabase function, processes response, and handles errors."""
    headers = {
        "Authorization": f"Bearer {authtokens}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    # Extract required fields
    required_fields = ["orderid", "packageid", "schedule", "userid", "wallet"]
    if not all(field in decrypted_data for field in required_fields):
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(required_fields)}")

    orderid = decrypted_data["orderid"]
    packageid = decrypted_data["packageid"]
    schedule = decrypted_data["schedule"]
    userid = decrypted_data["userid"]
    wallet = decrypted_data["wallet"]

    payload = {
        "orderid": orderid,
        "packageid": packageid,
        "schedule": schedule,
        "userid": userid,
        "wallet": wallet
    }

    response = requests.post(PACKAGE_URL, json=payload, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    # Step 2: Check if Supabase returned success (code == 101)
    if isinstance(response_data, dict) and response_data.get("code") == 101:
        return {
            "message": "Package processed successfully",
            "status": True,
            "code": 101
        }

    # Step 3: Handle other responses as errors
    error_message = response_data.get("message", "Supabase function call failed")
    raise HTTPException(status_code=response.status_code, detail=error_message)


@router.post("/package")
async def process_package(request: EncryptedDataRequest, authtoken: str = Header(...)):
    """Decrypts encrypted data, extracts fields, and processes package request in Supabase."""
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
    supabase_response = process_package_response(decrypted_data, authtokens["details"])

    # Step 3: Return the processed response
    return supabase_response
