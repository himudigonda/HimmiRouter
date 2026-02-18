import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

_key = os.getenv("ENCRYPTION_KEY")
if not _key:
    # Generate one if not set (mostly for dev/test) - but in prod this should be set
    print("WARNING: ENCRYPTION_KEY not set in .env using newly generated one for now.")
    _key = Fernet.generate_key().decode()

_fernet = Fernet(_key.encode())


def encrypt(data: str) -> str:
    return _fernet.encrypt(data.encode()).decode()


def decrypt(token: str) -> str:
    return _fernet.decrypt(token.encode()).decode()
