from pydantic import BaseModel, Field, ConfigDict

config = ConfigDict(from_attributes=True)

class CategorySchema(BaseModel):
    model_config = config
    name : str = Field(
        title="",
        description="",
    )

class CategoryResponse(BaseModel):
    id: int = Field(
        title="Category Id",
        description="Primary Key for Category Table",
    )
    name: str = Field(
        title="Category Name",
        description="Name of the Category",
    )
