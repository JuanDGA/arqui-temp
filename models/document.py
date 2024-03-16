from typing import Literal

from pydantic import BaseModel


class Document(BaseModel):
    location: str
    owner_id: str
    status: Literal["PENDING", "APPROVED", "REJECTED"]
