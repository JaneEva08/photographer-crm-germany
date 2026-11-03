from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=48)
    language: str = Field(default="DE", pattern="^(DE|EN|RU)$")
    status: str = Field(default="active", pattern="^(active|archived)$")
    notes: str | None = None


class ClientRead(ClientCreate, ORMModel):
    id: int
    created_at: datetime


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=48)
    language: str | None = Field(default=None, pattern="^(DE|EN|RU)$")
    status: str | None = Field(default=None, pattern="^(active|archived)$")
    notes: str | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for name in ("name", "language", "status"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} не может быть null")
        return self


class DealCreate(BaseModel):
    client_id: int | None = None
    title: str = Field(min_length=1, max_length=180)
    theme: str = Field(default="Другое", max_length=80)
    shoot_date: date | None = None
    status: str = Field(default="new", pattern="^(new|booked|completed|cancelled)$")
    amount_eur: Decimal = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)
    notes: str | None = None


class DealRead(DealCreate, ORMModel):
    id: int
    created_at: datetime


class DealUpdate(BaseModel):
    client_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=180)
    theme: str | None = Field(default=None, max_length=80)
    shoot_date: date | None = None
    status: str | None = Field(default=None, pattern="^(new|booked|completed|cancelled)$")
    amount_eur: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    notes: str | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for name in ("title", "theme", "status", "amount_eur"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} не может быть null")
        return self


class TaskCreate(BaseModel):
    client_id: int | None = None
    deal_id: int | None = None
    title: str = Field(min_length=1, max_length=180)
    due_date: date | None = None
    completed: bool = False
    notes: str | None = None


class TaskRead(TaskCreate, ORMModel):
    id: int
    created_at: datetime


class TaskUpdate(BaseModel):
    client_id: int | None = None
    deal_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=180)
    due_date: date | None = None
    completed: bool | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def reject_null_title(self):
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title не может быть null")
        return self
