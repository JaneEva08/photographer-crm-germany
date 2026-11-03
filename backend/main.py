from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from . import models, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Photo CRM", version="0.1.0", description="Учебная CRM фотографа: клиенты, съёмки и задачи.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/clients", response_model=list[schemas.ClientRead], tags=["clients"])
def clients(q: str | None = None, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    stmt = select(models.Client).order_by(models.Client.id).offset(offset).limit(limit)
    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(or_(models.Client.name.ilike(pattern), models.Client.email.ilike(pattern), models.Client.phone.ilike(pattern)))
    return db.scalars(stmt).all()


@app.post("/clients", response_model=schemas.ClientRead, status_code=201, tags=["clients"])
def create_client(payload: schemas.ClientCreate, db: Session = Depends(get_db)):
    row = models.Client(**payload.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return row


@app.get("/clients/{item_id}", response_model=schemas.ClientRead, tags=["clients"])
def get_client(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Client, item_id)
    if not row: raise HTTPException(404, "Клиент не найден")
    return row


@app.patch("/clients/{item_id}", response_model=schemas.ClientRead, tags=["clients"])
def update_client(item_id: int, payload: schemas.ClientUpdate, db: Session = Depends(get_db)):
    row = db.get(models.Client, item_id)
    if not row: raise HTTPException(404, "Клиент не найден")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(row, key, value)
    db.commit(); db.refresh(row)
    return row


@app.delete("/clients/{item_id}", status_code=204, tags=["clients"])
def delete_client(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Client, item_id)
    if not row: raise HTTPException(404, "Клиент не найден")
    db.delete(row); db.commit()
    return Response(status_code=204)


@app.get("/deals", response_model=list[schemas.DealRead], tags=["deals"])
def deals(q: str | None = None, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    stmt = select(models.Deal).order_by(models.Deal.id).offset(offset).limit(limit)
    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(or_(models.Deal.title.ilike(pattern), models.Deal.theme.ilike(pattern)))
    return db.scalars(stmt).all()


@app.post("/deals", response_model=schemas.DealRead, status_code=201, tags=["deals"])
def create_deal(payload: schemas.DealCreate, db: Session = Depends(get_db)):
    if payload.client_id is not None and not db.get(models.Client, payload.client_id): raise HTTPException(404, "Клиент не найден")
    row = models.Deal(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return row


@app.patch("/deals/{item_id}", response_model=schemas.DealRead, tags=["deals"])
def update_deal(item_id: int, payload: schemas.DealUpdate, db: Session = Depends(get_db)):
    row = db.get(models.Deal, item_id)
    if not row: raise HTTPException(404, "Съёмка не найдена")
    if payload.client_id is not None and not db.get(models.Client, payload.client_id): raise HTTPException(404, "Клиент не найден")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(row, key, value)
    db.commit(); db.refresh(row)
    return row


@app.delete("/deals/{item_id}", status_code=204, tags=["deals"])
def delete_deal(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Deal, item_id)
    if not row: raise HTTPException(404, "Съёмка не найдена")
    db.delete(row); db.commit()
    return Response(status_code=204)


@app.get("/tasks", response_model=list[schemas.TaskRead], tags=["tasks"])
def tasks(q: str | None = None, completed: bool | None = None, limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    stmt = select(models.Task).order_by(models.Task.id).offset(offset).limit(limit)
    if q: stmt = stmt.where(models.Task.title.ilike(f"%{q.strip()}%"))
    if completed is not None: stmt = stmt.where(models.Task.completed == completed)
    return db.scalars(stmt).all()


@app.post("/tasks", response_model=schemas.TaskRead, status_code=201, tags=["tasks"])
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    if payload.client_id is not None and not db.get(models.Client, payload.client_id): raise HTTPException(404, "Клиент не найден")
    if payload.deal_id is not None and not db.get(models.Deal, payload.deal_id): raise HTTPException(404, "Съёмка не найдена")
    row = models.Task(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return row


@app.patch("/tasks/{item_id}", response_model=schemas.TaskRead, tags=["tasks"])
def update_task(item_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    row = db.get(models.Task, item_id)
    if not row: raise HTTPException(404, "Задача не найдена")
    values = payload.model_dump(exclude_unset=True)
    if values.get("client_id") is not None and not db.get(models.Client, values["client_id"]): raise HTTPException(404, "Клиент не найден")
    if values.get("deal_id") is not None and not db.get(models.Deal, values["deal_id"]): raise HTTPException(404, "Съёмка не найдена")
    for key, value in values.items(): setattr(row, key, value)
    db.commit(); db.refresh(row)
    return row


@app.delete("/tasks/{item_id}", status_code=204, tags=["tasks"])
def delete_task(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Task, item_id)
    if not row: raise HTTPException(404, "Задача не найдена")
    db.delete(row); db.commit()
    return Response(status_code=204)
