from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=200
    )

    description: str = Field(
        ...,
        min_length=5
    )


class TicketUpdate(BaseModel):
    category: str | None = None
    priority: str | None = None
    status: str | None = None


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str | None
    priority: str | None
    sla_deadline: datetime | None
    resolution_suggestion: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )