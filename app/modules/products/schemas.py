from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    title: str
    description: str


class ProductPrivateResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str

    model_config = ConfigDict(from_attributes=True)
