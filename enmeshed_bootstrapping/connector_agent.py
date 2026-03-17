# pyright: reportUnknownMemberType = false, reportMissingTypeStubs = false, reportExplicitAny = false, reportAny = false
# assumes app is built and installed and the connector is running
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from ollama import ChatResponse, Client

from .connector_sdk import ConnectorSDK

CONNECTOR_BASE_URL = os.environ["CONNECTOR_BASE_URL"]
CONNECTOR_API_KEY = os.environ["CONNECTOR_API_KEY"]
WEBHOOK_ENDPOINT_HOSTNAME = os.environ["WEBHOOK_ENDPOINT_HOSTNAME"]  # e.g. localhost
WEBHOOK_ENDPOINT_PORT = int(os.environ["WEBHOOK_ENDPOINT_PORT"])  # e.g. 10001
OLLAMA_HOST = os.environ["OLLAMA_HOST"]  # e.g. http://localhost:5512

connector = ConnectorSDK(CONNECTOR_BASE_URL, CONNECTOR_API_KEY)
ollama_client = Client(host=OLLAMA_HOST)


def generate_reply(title: str, body: str) -> str:
    response: ChatResponse = ollama_client.chat(
        model="gemma3:4b",
        messages=[
            {
                "role": "system",
                "content": "Du bist ein ulkiger Quatschkopfagent. Antworte ulkig auf die Nutzeremail (bestehend aus Titel und Inhalt).",
            },
            {
                "role": "user",
                "content": f"Titel: {title}\nInhalt: {body}",
            },
        ],
    )
    return response["message"]["content"]


def handle_webhook(data: dict[Any, Any]) -> Any:
    trigger: str | None = data.get("trigger")

    if not trigger == "consumption.messageProcessed":
        return None

    message = data["data"]["message"]
    if message["isOwn"]:
        return None

    content = message["content"]
    if content["@type"] != "Mail":
        return None

    sender_addr = message["createdBy"]
    title = content["subject"]
    body = content["body"]

    reply = generate_reply(title, body)
    connector.post_message(
        sender_addr,
        f"re: {title}",
        reply,
    )

    return {}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))

        result = {}
        if self.path == "/":
            result = handle_webhook(body)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        _ = self.wfile.write(json.dumps(result).encode())


def run_agent_forever():
    srv = HTTPServer((WEBHOOK_ENDPOINT_HOSTNAME, WEBHOOK_ENDPOINT_PORT), Handler)
    srv.serve_forever()


__all__ = [
    "run_agent_forever",
]
