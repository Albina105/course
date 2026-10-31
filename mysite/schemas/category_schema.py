from pydantic import BaseModel


class CategoryInputSchema(BaseModel):
    category_name: str

class CategoryOutSchema(BaseModel):
    id: int
    category_name: str
