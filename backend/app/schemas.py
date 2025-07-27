from typing import Optional, Union
from pydantic import BaseModel

class CustomerBase(BaseModel):
    name: str
    phone: str
    address: str

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerOut(CustomerBase):
    id: int
    model_config = {
        "from_attributes": True
    }

class ChatbotIn(BaseModel):
    message: str

class ToolResult(BaseModel):
    ok: bool = True
    data: Optional[Union[dict, list]] = None
    message: Optional[str] = None
