import requests
import os
from fastapi import APIRouter, HTTPException, Header
from dotenv import load_dotenv
from app.utility.encryption_utils import decrypt_aes256

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ALL_SERVICES_URL = f"{SUPABASE_URL}/rest/v1/rpc/AllServices"

# Initialize FastAPI Router
router = APIRouter()


def fetch_all_services(authtokens):
    """Calls Supabase function, processes response, and handles errors."""
    headers = {
        "Authorization": f"Bearer {authtokens}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(ALL_SERVICES_URL, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    # Step 2: Check if Supabase returned success (code == 101)
    if isinstance(response_data, dict) or isinstance(response_data,list):
        return {
            "message": "All services fetched successfully",
            "status": True,
            "code": 101,
            "data": response_data
        }

    # Step 3: Handle other responses as errors
    error_message = response_data.get("message", "Supabase function call failed")
    raise HTTPException(status_code=response.status_code, detail=error_message)


@router.get("/all-services")
async def all_services(authtoken: str = Header(...)):
    """Decrypts authtoken and fetches all services from Supabase."""
    try:
        authtokens = decrypt_aes256(authtoken)
    except Exception:
        raise HTTPException(status_code=401, detail="Failed to decrypt authtoken")

    # Step 1: Call Supabase function
    supabase_response = fetch_all_services(authtokens["details"])

    # Step 2: Return the processed response
    return supabase_response
