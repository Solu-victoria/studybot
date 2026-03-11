from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
import os
from database import SessionLocal, Reminder

scheduler = BackgroundScheduler()

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def send_reminder(reminder_id):
    db = SessionLocal()
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.active == True).first()
    if not reminder:
        db.close()
        return

    try:
        client.messages.create(
            body="📚 Study reminder! Time to study.",
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to=f"whatsapp:{reminder.phone}"
        )
        print(f"Reminder sent to {reminder.phone}")
    except Exception as e:
        print("Reminder failed:", e)

    # Delete one-off reminders
    if not reminder.recurring:
        db.delete(reminder)
        db.commit()
        try:
            scheduler.remove_job(str(reminder_id))
        except Exception:
            pass
    db.close()

def add_reminder(phone, hour, minute, recurring=True):
    db = SessionLocal()
    reminder = Reminder(
        phone=phone,
        hour=hour,
        minute=minute,
        recurring=recurring
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    db.close()

    scheduler.add_job(
        func=send_reminder,
        trigger="cron",
        hour=hour,
        minute=minute,
        args=[reminder.id],
        id=str(reminder.id),
        replace_existing=True
    )

def load_reminders():
    db = SessionLocal()
    reminders = db.query(Reminder).filter(Reminder.active == True).all()
    for r in reminders:
        scheduler.add_job(
            func=send_reminder,
            trigger="cron",
            hour=r.hour,
            minute=r.minute,
            args=[r.id],
            id=str(r.id),
            replace_existing=True
        )
    db.close()