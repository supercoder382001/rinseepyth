import requests
import os
from fastapi import APIRouter, HTTPException, Header
from dotenv import load_dotenv
from app.utility.encryption_utils import decrypt_aes256

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
AVAILABLE_DATES_URL = f"{SUPABASE_URL}/rest/v1/rpc/Available%20Dates"  # Space in URL replaced with '%20'

# Initialize FastAPI Router
router = APIRouter()


def fetch_available_dates(authtokens):
    """Calls Supabase function, processes response, and handles errors."""
    headers = {
        "Authorization": f"Bearer {authtokens}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(AVAILABLE_DATES_URL, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    # Step 2: Check if response data is a non-empty dictionary
    if isinstance(response_data, dict) or isinstance(response_data,list):
        return {
            "message": "Available dates fetched successfully",
            "status": True,
            "data": response_data
        }

    # Step 3: Handle empty or incorrect response type as an error
    raise HTTPException(status_code=404, detail="No available dates found")


@router.get("/available dates")
async def available_dates(authtoken: str = Header(...)):
    """Decrypts authtoken and fetches available dates from Supabase."""
    try:
        authtokens = decrypt_aes256(authtoken)
    except Exception:
        raise HTTPException(status_code=401, detail="Failed to decrypt authtoken")

    # Step 1: Call Supabase function
    supabase_response = fetch_available_dates(authtokens["details"])

    # Step 2: Return the processed response
    return supabase_response
