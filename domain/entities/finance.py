from decimal import Decimal
from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Invoice(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    vendor: str
    amount: Decimal
    currency: str = "MXN"
    due_date: date
    is_paid: bool = False

    def mark_as_paid(self) -> "Invoice":
        return self.model_copy(update={"is_paid": True})


class Expense(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    description: str
    amount: Decimal
    currency: str = "MXN"
    category: str
    date: date
    invoice_id: UUID | None = None
