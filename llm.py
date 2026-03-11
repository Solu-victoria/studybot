import os
import json
from openai import OpenAI
import traceback

# Create a Gemini client using OpenAI library
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

def ask_llm(question):

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),  # cost‑efficient and solid for chat
        messages=[
            {"role": "user", "content": question}
        ],
    )
    # Return the assistant response
    return response.choices[0].message.content


def process_message_with_llm(message):
    """
    Parse message for reminders and/or answer study question
    """
    prompt = f"""
    You are a study assistant. The user message is:

    "{message}"

    Tasks:
    1. Determine if this message is asking to set a study reminder.
       - If yes, extract hour (0-23), minute (0-59), and recurring (True/False)
       - If no, set reminder_data to null.
    2. Provide a helpful answer to any study question or a confirmation for the reminder.

    Return as valid JSON:
    {{
      "answer": "<text reply to user>",
      "reminder_data": {{ "hour": 19, "minute": 30, "recurring": true }} OR null
    }}
    """

    try:
        response = ask_llm(prompt)
        print("LLM raw response:", repr(response))  # <-- this shows empty or malformed response
        data = json.loads(response)
        return data.get("answer"), data.get("reminder_data")
    except json.JSONDecodeError:
        print("JSON decode failed. Response was:", repr(response))
        traceback.print_exc()
        return "Sorry, I couldn't understand your message.", None
    except Exception as e:
        print("LLM processing failed:", e)
        traceback.print_exc()
        return "Sorry, I couldn't understand your message.", None