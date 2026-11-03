"""Create reproducible, synthetic CRM data for the course assignment."""
import random
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func, select
from .db import Base, SessionLocal, engine
from .models import Client, Deal, Task

NAMES = ["Anna Müller", "Lukas Weber", "Sophie Fischer", "Mia Schneider", "Paul Wagner", "Emma Becker", "Noah Hoffmann", "Lena Schulz"]
THEMES = ["Свадьба", "Love story", "Мероприятие", "Спорт", "Сюжетная съёмка", "Художественная постановка"]
PACKAGES = [180, 250, 320, 390, 450, 640]


def seed(count: int = 1000, seed_value: int = 20261103) -> dict[str, int]:
    if count < 1 or count > 10000:
        raise ValueError("Количество записей должно быть от 1 до 10000")
    rng = random.Random(seed_value)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        existing = db.scalar(select(func.count()).select_from(Client)) or 0
        if existing >= count:
            return {"clients": existing, "created": 0}
        needed = count - existing
        clients = [Client(name=f"{rng.choice(NAMES)} {existing+i+1:04d}",
                          email=f"client{existing+i+1:04d}@example.test", language=rng.choice(["DE", "EN", "RU"]))
                   for i in range(needed)]
        db.add_all(clients); db.flush()
        deals = []
        for i, client in enumerate(clients):
            theme = rng.choice(THEMES)
            d = Deal(client_id=client.id, title=f"{theme} #{existing+i+1}",
                     theme=theme, shoot_date=date.today()+timedelta(days=rng.randint(-90, 180)),
                     status=rng.choice(["new", "booked", "completed", "cancelled"]), amount_eur=Decimal(rng.choice(PACKAGES)))
            deals.append(d)
        db.add_all(deals); db.flush()
        db.add_all([Task(client_id=d.client_id, deal_id=d.id, title=rng.choice(["Отправить договор", "Подтвердить дату", "Подготовить галерею", "Согласовать отбор"]), due_date=d.shoot_date, completed=rng.random() < .4) for d in deals])
        db.commit()
        return {"clients": existing + needed, "created": needed}


if __name__ == "__main__":
    print(seed())
