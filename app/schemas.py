from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    tenant_id: int


class EPDCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    product_category: str = Field(min_length=1, max_length=120)
    gwp: float = Field(ge=0)


class EPDRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    product_category: str
    gwp: float
    tenant_id: int
