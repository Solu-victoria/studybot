import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

# PostgreSQL setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()


class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False)
    hour = Column(Integer, nullable=False)
    minute = Column(Integer, nullable=False)
    message = Column(String, default='📚 Study reminder! Time to study. What topic do you want help with today?')
    active = Column(Boolean, default=True)


Base.metadata.create_all(bind=engine)


def send_whatsapp(phone, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": phone, "type": "text", "text": {"body": message}}
    requests.post(url, headers=headers, json=data)


def schedule_reminder(reminder: Reminder):
    scheduler.add_job(
        send_whatsapp,
        "cron",
        args=[reminder.phone, reminder.message],
        hour=reminder.hour,
        minute=reminder.minute,
        id=str(reminder.id),
        replace_existing=True
    )


def load_reminders():
    db = SessionLocal()
    reminders = db.query(Reminder).filter(Reminder.active == True).all()
    for r in reminders:
        schedule_reminder(r)
    db.close()


def create_reminder(phone: str, hour: int, minute: int):
    db = SessionLocal()
    reminder = Reminder(phone=phone, hour=hour, minute=minute)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    schedule_reminder(reminder)
    db.close()
    return reminder