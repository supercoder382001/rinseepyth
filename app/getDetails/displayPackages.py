import requests
import os
from fastapi import APIRouter, HTTPException, Header
from dotenv import load_dotenv
from app.utility.encryption_utils import decrypt_aes256

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print(SUPABASE_URL)
DISPLAY_PACKAGES_URL = f"{SUPABASE_URL}/rest/v1/rpc/displaypackages"

# Initialize FastAPI Router
router = APIRouter()


def fetch_display_packages(authtokens):
    """Calls Supabase function, processes response, and handles errors."""
    headers = {
        "Authorization": f"Bearer {authtokens}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(DISPLAY_PACKAGES_URL, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    # Step 2: Check if response data is a non-empty dictionary
    if isinstance(response_data, list):
        return {
            "message": "Packages fetched successfully",
            "status": True,
            "data": response_data
        }

    # Step 3: Handle empty or incorrect response type as an error
    raise HTTPException(status_code=404, detail="No packages found")


@router.get("/displaypackages")
async def display_packages(authtoken: str = Header(...)):
    """Decrypts authtoken and fetches display packages from Supabase."""
    try:
        authtokens = decrypt_aes256(authtoken)
    except Exception:
        raise HTTPException(status_code=401, detail="Failed to decrypt authtoken")

    # Step 1: Call Supabase function
    print(authtokens)
    supabase_response = fetch_display_packages(authtokens["details"])

    # Step 2: Return the processed response
    return supabase_response
