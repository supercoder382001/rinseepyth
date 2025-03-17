import requests
import os
from fastapi import APIRouter, HTTPException, Header
from app.models import EncryptedDataRequest
from dotenv import load_dotenv
from app.utility.encryption_utils import decrypt_aes256
import time

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
COUPON_ORDER_URL = f"{SUPABASE_URL}/rest/v1/rpc/CouponOrder"

# Initialize FastAPI Router
router = APIRouter()


def order_response(decrypted_data, authtokens):
    """Calls Supabase function, processes response, and handles errors."""
    auth_header = authtokens
    headers = {
        "Authorization": f"Bearer {auth_header}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    # cart = decrypted_data["cart"]  # Ensured to exist and be a list
    # coupon = decrypted_data["coupon"]
    # indextime = decrypted_data["indextime"]
    # orderid = decrypted_data["orderid"]
    # paymentmode = decrypted_data["paymentmode"]
    # preference = decrypted_data["preference"]
    # process = decrypted_data["process"]
    # schedule = decrypted_data["schedule"]
    # totalvalue = decrypted_data["totalvalue"]
    # userid = decrypted_data["userid"]
    # value = decrypted_data["value"]
    # wallet = decrypted_data["wallet"]
    current_time = int(time.time() * 1000)

    # Create the array
    data = [
        {"Time": current_time, "Pname": "Confirmed", "Status": "Done"},
        {"Time": 1, "Pname": "Pickup", "Status": "Pending"},
        {"Time": 1, "Pname": "InProcess", "Status": "Pending"},
        {"Time": 1, "Pname": "OFD", "Status": "Pending"},
        {"Time": 1, "Pname": "Delivered", "Status": "Pending"}
    ]

    cart = decrypted_data["items"]  # Ensured to exist and be a list
    coupon = decrypted_data["couponid"]
    indextime = decrypted_data["deliveryinfo"]["typeindex"]
    orderid = decrypted_data["orderid"]
    paymentmode = decrypted_data["Paymentmode"]
    preference = decrypted_data["preference"]
    process = data
    schedule = decrypted_data["deliveryinfo"]
    totalvalue = decrypted_data["Total"]
    userid = decrypted_data["userid"]
    value = decrypted_data["value"]
    wallet = decrypted_data["id"]


    payload = {
        "cart": cart,
        "coupon": coupon,
        "indextime": indextime,
        "orderid": orderid,
        "paymentmode": paymentmode,
        "preference": preference,
        "process": process,
        "schedule": schedule,
        "totalvalue": totalvalue,
        "userid": userid,
        "value": value,
        "wallet": wallet
    }

    response = requests.post(COUPON_ORDER_URL, json=payload, headers=headers)

    # Step 1: Parse Supabase JSON response
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response")

    # Step 2: Check if Supabase returned success (code == 101)
    if isinstance(response_data, dict):
        return {
            "message": "Order processed successfully",
            "status": True,
            "code": 101,
            "data":response_data
        }

    # Step 3: Handle other responses as errors
    error_message = response_data.get("message", "Supabase function call failed")
    raise HTTPException(status_code=response.status_code, detail=error_message)


@router.post("/placeorders")
async def placeorder(request: EncryptedDataRequest, authtoken: str = Header(...)):
    """Decrypts encrypted data, extracts fields, and processes the Supabase response."""
    try:
        authtokens = decrypt_aes256(authtoken)
    except Exception:
        raise HTTPException(status_code=401, detail="Failed to decrypt authtoken")
    # Step 1: Decrypt the AES-256 encrypted data
    try:
        decrypted_data = decrypt_aes256(request.encrypted_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt data")

    # Step 3: Get response from Supabase
    supabase_response = order_response(decrypted_data, authtokens["details"])

    # Step 4: Return the processed response
    return supabase_response
