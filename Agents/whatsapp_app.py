import os
import sys

from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse

# Ensure Agents directory is in sys.path for imports to work
sys.path.insert(0, os.path.dirname(__file__))

from graph_builder import build_graph

app = FastAPI()
graph = build_graph()


@app.get("/")
def home():
    return {"status": "WhatsApp AI Assistant is running"}


@app.get("/whatsapp")
def whatsapp_get():
    return {"message": "This endpoint only accepts POST requests from Twilio."}


@app.post("/whatsapp")
async def whatsapp_reply(request: Request, Body: str = Form(...)):
    client = request.client
    if client:
        print(f"Incoming WhatsApp request from {client.host}:{client.port}")

    print("Incoming message:", Body)

    user_question = Body.strip()

    try:
        result = graph.invoke({
            "question": user_question
        })

        answer = result.get("answer", "")
        if not answer:
            answer = "Sorry, I couldn't generate an answer right now."

    except Exception as e:
        print("Error while generating answer:", e)
        answer = "Sorry, something went wrong while processing your message."

    if len(answer) > 1500:
        answer = answer[:1500] + "..."

    print("Generated answer:", answer)

    response = MessagingResponse()
    response.message(answer)

    return PlainTextResponse(str(response), media_type="application/xml")


