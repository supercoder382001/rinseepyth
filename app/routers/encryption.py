from fastapi import APIRouter, HTTPException
from app.utility.encryption_utils import encrypt_aes256

router = APIRouter()

@router.post("/encrypt")
async def encrypt_data(data: dict):
    """API endpoint to encrypt JSON data."""
    try:
        encrypted_string = encrypt_aes256(data)
        return {"encrypted_data": encrypted_string}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
