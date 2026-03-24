import uuid
from dataclasses import dataclass


@dataclass
class AuthInfo:
    user_id: uuid.UUID
    email: str
