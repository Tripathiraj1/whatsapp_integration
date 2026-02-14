import os
from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import requests
import asyncio
import time
import smtplib
from email.mime.text import MIMEText
from collections import defaultdict

load_dotenv()
GPT_API = os.getenv("GPT_API")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ALERT_INTERVAL = os.getenv("ALERT_INTERVAL")  # seconds
last_alert_time = {} # to store last alert time for each error
processed_message_ids = set() # to prevent duplicate processing

# -------------------
# app
# -------------------
app = FastAPI()

# -------------------
# classes
# -------------------
class ChatRequest(BaseModel):
    prompt: str

class WhatsAppRequest(BaseModel):
    to: str
    message: str
    context_message_id: str


# ---------------------
# functions
# ---------------------
def get_openai_client():
    api_key = os.getenv("GPT_API")
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY") # Fallback
    if not api_key:
        raise ValueError("GPT_API or OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)

def mark_as_read(message_id):
    # this function marks the message as read for provided message id
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def typing_indicator(message_id):
    # this function sends a typing indicator for provided message id
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
        "typing_indicator": {
            "type": "text"
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def send_email(subject, message):
    # this function sends an email to the admin 
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = ADMIN_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email alert failed:", e)

def notify_error(error_text):
    # this function notifies the admin for any error encountered unique to timeframe
    global last_alert_time
    current_time = time.time()
    # Use first part of error as key (group similar errors)
    error_key = error_text[:100]
    # Check if alert was sent recently
    if error_key in last_alert_time:
        if current_time - last_alert_time[error_key] < ALERT_INTERVAL:
            return  # Skip alert
    # Update last alert time
    last_alert_time[error_key] = current_time
    # Send email
    subject = "WhatsApp Bot Error"
    message = f"""
        Error occurred:
        {error_text}
        Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
    """
    send_email(subject, message)

# ---------------------
# registered paths
# ---------------------
@app.get("/")
def index():
    return "FastAPI with Conda is working!"

@app.post("/chat/")
def chat_with_gpt(chat_request: ChatRequest):
    # this function chats with gpt and returns its response
    try:
        # Replicating the logic from views.py
        if not chat_request.prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": chat_request.prompt}
            ],
            temperature=0.7, 
            timeout = 20
        )
        
        reply = response.choices[0].message.content
        return {
            "status": "success",
            "response": reply
        }
        
    except Exception as e:
        # In case of specific errors, you might want to catch them separately
        # replicating the general catch-all from views.py
        print("error in getting response from gpt", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/whatsapp")
def send_whatsapp_message(payload: WhatsAppRequest):
    # this function sends a whatsapp message to the provided number and add context of previous message
    TO_NUMBER = payload.to
    MESSAGE = payload.message
    CONTEXT = payload.context_message_id
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": TO_NUMBER,
        "type": "text",
        "context": {
            "message_id": CONTEXT
        },
        "text": {
            "preview_url": False,
            "body": MESSAGE
        }
    }

    response = requests.post(url, headers=headers, json=data)

    return {
        "status_code": response.status_code,
        "response": response.json()
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    # this function verifies the webhook
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)




# -----------------------------
# BACKGROUND PROCESSING
# -----------------------------
def process_message(sender, message_id, text):
    # this function processes the message and sends a response to the sender
    # Duplicate protection
    if message_id in processed_message_ids:
        return
    processed_message_ids.add(message_id)

    try:
        # Simulate long processing
        mark_as_read(message_id)
        typing_indicator(message_id)
        chat_request = ChatRequest(prompt=text) #Generate response from gpt
        reply_text = chat_with_gpt(chat_request).get("response")
        payload = WhatsAppRequest(to=sender, message=reply_text, context_message_id=message_id)
        answer = send_whatsapp_message(payload) #Send response to sender
        

    except Exception as e:
        error_text = str(e)
        # notify_error(error_text)
        answer = send_whatsapp_message(WhatsAppRequest(to=sender, message=f"Its not you... Its us.. \nWill be back soon", context_message_id=message_id))
        print("Error parsing WhatsApp payload:", e)


# -----------------------------
# WEBHOOK
# -----------------------------
@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    # this function handles the webhook
    try:
        body = await request.json()
    except Exception:
        return {"status": "ignored"}

    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        # Handle user messages only
        if "messages" in value:
            msg = value["messages"][0]
            sender = msg.get("from")
            message_id = msg.get("id")

            if msg.get("type") == "text":
                text = msg["text"]["body"]

                background_tasks.add_task(
                    process_message,
                    sender,
                    message_id,
                    text
                )
    except Exception as e:
        # notify_error(f"Webhook parsing error: {str(e)}")
        print("got error at responding to whatsapp", e)

    # Immediate response (<1 sec)
    return {"status": "received"}