from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
import os
from database import SessionLocal, Reminder

scheduler = BackgroundScheduler()

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def send_reminder(phone):

    client.messages.create(
        body="📚 Study reminder! Time to study.",
        from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
        to=f"whatsapp:{phone}"
    )


def load_reminders():

    db = SessionLocal()

    reminders = db.query(Reminder).filter(Reminder.active == True).all()

    for r in reminders:

        scheduler.add_job(
            send_reminder,
            "cron",
            hour=r.hour,
            minute=r.minute,
            args=[r.phone],
            id=str(r.id),
            replace_existing=True
        )

    db.close()


def add_reminder(phone, hour, minute):

    db = SessionLocal()

    reminder = Reminder(
        phone=phone,
        hour=hour,
        minute=minute
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    db.close()

    scheduler.add_job(
        send_reminder,
        "cron",
        hour=hour,
        minute=minute,
        args=[phone],
        id=str(reminder.id),
        replace_existing=True
    )