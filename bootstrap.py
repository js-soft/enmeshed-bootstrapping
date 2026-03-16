# pyright: reportUnknownMemberType = false, reportMissingTypeStubs = false, reportExplicitAny = false, reportAny = false
# assumes app is built and installed and the connector is running
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, TypedDict

from adbutils import adb
from devtools import pprint
from ollama import ChatResponse, chat

from src import dev_app
from src.connector_sdk import ConnectorSDK


class LocalAccountDTO(TypedDict):
    id: str
    address: str
    name: str


CONNECTOR_BASE_URL = "http://localhost:3000"
CONNECTOR_API_KEY = "This_is_a_test_APIKEY_with_30_chars+"

connector = ConnectorSDK(base_url=CONNECTOR_BASE_URL, api_key=CONNECTOR_API_KEY)
d = adb.device()
dev_app.run_clean(d)

app_account: LocalAccountDTO = dev_app.c2_send(  # pyright: ignore[reportAssignmentType]
    {
        "action": "createDefaultAccount",
        "name": "Peter Langweilig",
    }
)["data"]
pprint(app_account)

response = connector.post_own_rlt()
truncref = response.result.reference.truncated

_ = dev_app.c2_send(
    {
        "action": "acceptRelationshipTemplate",
        "accountId": app_account["id"],
        "truncRef": truncref,
    }
)

while True:
    rels = connector.get_relationships(peer=app_account["address"], status="Active")
    if len(rels.result) > 0:
        break

    time.sleep(0.5)


connector.post_message(
    app_account["address"],
    f"Willkommen, {app_account['name']}",
    "Herzlich willkommen.",
)

_ = dev_app.c2_send(
    {
        "action": "navigate",
        "path": f"/account/{app_account['id']}",
    }
)


def generate_reply(title: str, body: str) -> str:
    response: ChatResponse = chat(
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

    print("webhook msg", sender_addr, title, body)

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


CONNECTOR_WEBHOOK_PORT = 10001
HTTPServer(("0.0.0.0", CONNECTOR_WEBHOOK_PORT), Handler).serve_forever()
