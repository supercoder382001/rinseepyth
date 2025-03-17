from fastapi import APIRouter, HTTPException
from app.utility.encryption_utils import decrypt_aes256

router = APIRouter()


@router.post("/decrypt")
async def decrypt_data(data: str):
    """API endpoint to encrypt JSON data."""
    try:
        encrypted_string = decrypt_aes256(data)
        return encrypted_string
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
