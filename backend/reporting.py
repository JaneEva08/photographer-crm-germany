from sqlalchemy import select
from sqlalchemy.orm import Session
from . import models


def report_data(kind: str, db: Session):
    if kind == "clients":
        rows = db.scalars(select(models.Client).order_by(models.Client.id)).all()
        headers = ["ID", "Name", "Email", "Phone", "Language", "Status", "Created"]
        data = [[x.id, x.name, x.email or "", x.phone or "", x.language, x.status, x.created_at.isoformat()] for x in rows]
    elif kind == "deals":
        rows = db.scalars(select(models.Deal).order_by(models.Deal.id)).all()
        headers = ["ID", "Client ID", "Title", "Theme", "Shoot date", "Status", "Amount EUR"]
        data = [[x.id, x.client_id or "", x.title, x.theme, x.shoot_date.isoformat() if x.shoot_date else "", x.status, float(x.amount_eur)] for x in rows]
    elif kind == "tasks":
        rows = db.scalars(select(models.Task).order_by(models.Task.id)).all()
        headers = ["ID", "Client ID", "Deal ID", "Title", "Due date", "Completed"]
        data = [[x.id, x.client_id or "", x.deal_id or "", x.title, x.due_date.isoformat() if x.due_date else "", "Yes" if x.completed else "No"] for x in rows]
    else:
        raise ValueError("Вид отчёта: clients, deals или tasks")
    return headers, data
