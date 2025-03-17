from pydantic import BaseModel


class EncryptedDataRequest(BaseModel):
    encrypted_data: str  # AES-256 encrypted string
