from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


def utcnow():
    return datetime.now(timezone.utc)


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    email: Mapped[str | None] = mapped_column(String(254), index=True)
    phone: Mapped[str | None] = mapped_column(String(48))
    language: Mapped[str] = mapped_column(String(2), default="DE")
    status: Mapped[str] = mapped_column(String(24), default="active", index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    deals: Mapped[list["Deal"]] = relationship(back_populates="client")
    tasks: Mapped[list["Task"]] = relationship(back_populates="client")


class Deal(Base):
    __tablename__ = "deals"
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(180), index=True)
    theme: Mapped[str] = mapped_column(String(80), default="Другое", index=True)
    shoot_date: Mapped[date | None] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(24), default="new", index=True)
    amount_eur: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    client: Mapped[Client | None] = relationship(back_populates="deals")
    tasks: Mapped[list["Task"]] = relationship(back_populates="deal")


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"), index=True)
    deal_id: Mapped[int | None] = mapped_column(ForeignKey("deals.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(180), index=True)
    due_date: Mapped[date | None] = mapped_column(Date, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    client: Mapped[Client | None] = relationship(back_populates="tasks")
    deal: Mapped[Deal | None] = relationship(back_populates="tasks")
