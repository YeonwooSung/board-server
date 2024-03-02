from pydantic import BaseModel, Field, ConfigDict

config = ConfigDict(from_attributes=True)

class PostsSchema(BaseModel):
    model_config = config
    title : str = Field(
        title="",
        description="",
    )
    content : str = Field(
        title="",
        description="",
    )
    author_id : int = Field(
        title="",
        description="",
    )
    category_id : int = Field(
        title="",
        description="",
    )


class PostsResponse(BaseModel):
    id: int = Field(
        title="",
        description="",
    )
    title: str = Field(
        title="",
        description="",
    )
    content: str = Field(
        title="",
        description="",
    )
    author_id: int = Field(
        title="",
        description="",
    )
    category_id: int = Field(
        title="",
        description="",
    )
