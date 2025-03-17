import base64
import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Decode Base64 if necessary
encoded_key = b'\x85\xe9\x0e\x1dq\x8b\x11\xdd>e\xe0,\x06\xbe\xcd\x86\xd2\xd4\xd4&\xf8 \xdbC\xf5x`\xd1[\xd9Z\xde'
# SECRET_KEY = base64.b64decode(encoded_key)
SECRET_KEY=encoded_key
def encrypt_aes256(json_data: dict) -> str:

    # Convert JSON to string
    plain_text = json.dumps(json_data)

    # Generate random IV (16 bytes)
    iv = os.urandom(16)

    # Initialize AES cipher
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)

    # Encrypt and pad the data
    encrypted_bytes = cipher.encrypt(pad(plain_text.encode(), AES.block_size))

    # Encode to Base64
    encrypted_combined = base64.b64encode(encrypted_bytes).decode()
    iv_encoded = base64.b64encode(iv).decode()

    # Insert IV at the 5th position
    final_encrypted = encrypted_combined[:4] + iv_encoded + encrypted_combined[4:]

    return final_encrypted


def decrypt_aes256(encrypted_text: str) -> dict:
    """Decrypts AES-256 encrypted JSON by extracting IV from the 5th position."""

    # Extract IV from 5th position
    iv_encoded = encrypted_text[4:28]  # Extract 24-character base64 IV
    encrypted_combined = encrypted_text[:4] + encrypted_text[28:]  # Remove IV

    # Decode IV and encrypted text
    iv = base64.b64decode(iv_encoded)
    encrypted_bytes = base64.b64decode(encrypted_combined)

    # Initialize AES cipher
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)

    # Decrypt and unpad the data
    decrypted_text = unpad(cipher.decrypt(encrypted_bytes), AES.block_size).decode()

    # Convert back to JSON
    return json.loads(decrypted_text)
