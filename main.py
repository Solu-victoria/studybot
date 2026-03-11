from fastapi import FastAPI, Form
from llm import ask_llm
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

    if "remind me" in Body.lower():

        add_reminder(user_phone, 20, 0)

        return """
        <Response>
            <Message>✅ Study reminder set for 8 PM daily.</Message>
        </Response>
        """

    answer = ask_llm(Body)

    return f"""
    <Response>
        <Message>{answer}</Message>
    </Response>
    """