from fastapi import FastAPI, Request
import requests
import os
from reminders import create_reminder, load_reminders
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load reminders from DB on startup
load_reminders()


def send_whatsapp(phone, message):
    url = f"https://graph.facebook.com/v18.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
    headers = {"Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": phone, "type": "text", "text": {"body": message}}
    requests.post(url, headers=headers, json=data)


def ask_llm(question):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful study tutor."},
            {"role": "user", "content": question}
        ]
    }
    r = requests.post(url, headers=headers, json=data)
    return r.json()["choices"][0]["message"]["content"]


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    try:
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        phone = body["entry"][0]["changes"][0]["value"]["messages"][0]["from"]

        msg_lower = message.lower()
        if msg_lower.startswith("remind me at"):
            time = msg_lower.replace("remind me at", "").strip()
            hour, minute = map(int, time.split(":"))
            create_reminder(phone, hour, minute)
            send_whatsapp(phone, f"✅ Reminder set for {hour}:{minute}")
        else:
            answer = ask_llm(message)
            send_whatsapp(phone, answer)
    except:
        pass
    return {"status": "ok"}