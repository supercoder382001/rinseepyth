import requests
import os
from fastapi import APIRouter, HTTPException, Header
from app.models import EncryptedDataRequest
from dotenv import load_dotenv
from app.utility.encryption_utils import decrypt_aes256

# Load environment variables
load_dotenv()

# SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_URL="https://zmvjylvafmgqpxqtrblc.supabase.co"
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inptdmp5bHZhZm1ncXB4cXRyYmxjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyMzQ4OTgxMiwiZXhwIjoyMDM5MDY1ODEyfQ.5cdLeGHxXVoEqmrF27N1d1oDmTWdzbZmKeo4yCusSn0"
VERIFY_OTP_URL = f"{SUPABASE_URL}/rest/v1/rpc/verifyotp"

# Initialize FastAPI Router
router = APIRouter()


def fetch_user_details(decrypted_data):
    """Calls Supabase function, processes response, and handles errors."""
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inptdmp5bHZhZm1ncXB4cXRyYmxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjM0ODk4MTIsImV4cCI6MjAzOTA2NTgxMn0.-qK5cu9zPoVtcpGAf14-XuJ55SMYXpfpXXgp6lz-Z4M",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    # Extract required fields
    if "email" not in decrypted_data:
        raise HTTPException(status_code=400, detail="Missing required field: email")

    email = decrypted_data["email"]
    otp = decrypted_data["otp"]

    payload = {"email": email, "otp": otp}

    response = requests.post(VERIFY_OTP_URL, json=payload, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    # Step 2: Check if Supabase returned success (code == 101)
    if isinstance(response_data, dict) and response_data.get("code") == 101:
        return {
            "message": "OTP Verified",
            "status": True,
            "code": 101
        }
    if isinstance(response_data, dict) and response_data.get("code") == 102:
        return {
            "message": "Incorrect OTP",
            "status": True,
            "code": 102
        }

    # Step 3: Handle other responses as errors
    error_message = response_data.get("message", "Supabase function call failed")
    raise HTTPException(status_code=response.status_code, detail=error_message)


@router.post("/verifyotp")
async def get_user_details(request: EncryptedDataRequest):
    """Decrypts encrypted data, extracts fields, and fetches user details from Supabase."""
    # try:
    #     authtokens = decrypt_aes256(authtoken)
    # except Exception:
    #     raise HTTPException(status_code=401, detail="Failed to decrypt authtoken")

    # Step 1: Decrypt the AES-256 encrypted data
    try:
        decrypted_data = decrypt_aes256(request.encrypted_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt data")

    # Step 2: Get response from Supabase
    supabase_response = fetch_user_details(decrypted_data)

    # Step 3: Return the processed response
    return supabase_response
