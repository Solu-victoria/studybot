from fastapi import FastAPI, Form
from fastapi.responses import Response
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

        twiml = """
        <Response>
            <Message>✅ Study reminder set for 8 PM daily.</Message>
        </Response>
        """

        return Response(content=twiml, media_type="application/xml")


    answer = ask_llm(Body)

    twiml = f"""
    <Response>
        <Message>{answer}</Message>
    </Response>
    """

    return Response(content=twiml, media_type="application/xml")