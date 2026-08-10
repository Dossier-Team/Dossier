from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    phone_numer: str
    state: str
    on_dnc: bool

class Company(BaseModel):
    name: str
    known_aliases: list[str]
    address: str
    created_at: datetime
    num_violations: int

