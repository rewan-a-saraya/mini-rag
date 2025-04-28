from pydantic import BaseModel, Field, validators
from typing import Optional
from bson.objectid import  ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    chunk_text: str = Field(..., max_length=1000)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId


    class Config:
        arbitrary_types_allowed = True

