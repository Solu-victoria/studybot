from fastapi import FastAPI, Form
from fastapi.responses import Response
from llm import process_message_with_llm
from reminders import add_reminder, load_reminders, scheduler

app = FastAPI()

scheduler.start()
load_reminders()

@app.post("/webhook")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):
    user_phone = From.replace("whatsapp:", "")

    # LLM handles both reminder extraction and study answers
    answer, reminder_data = process_message_with_llm(Body)

    if reminder_data:
        add_reminder(
            phone=user_phone,
            hour=reminder_data["hour"],
            minute=reminder_data["minute"],
            recurring=reminder_data["recurring"]
        )

    # Respond to user in proper TwiML
    twiml = f"""
    <Response>
        <Message>{answer}</Message>
    </Response>
    """
    return Response(content=twiml, media_type="application/xml")