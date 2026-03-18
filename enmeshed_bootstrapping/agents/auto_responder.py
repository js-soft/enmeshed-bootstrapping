# pyright: reportUnknownMemberType = false, reportExplicitAny = false, reportAny = false, reportIndexIssue = false, reportUnknownVariableType = false

from typing import cast

import ollama

from enmeshed_bootstrapping.connector_sdk import ConnectorSDK
from enmeshed_bootstrapping.webhook_server import HandlerFn


def make_handlerfn(
    connector: ConnectorSDK,
    ollama_client: ollama.Client,
) -> HandlerFn:
    def handlerfn(trigger: str, data: dict[str, object]) -> dict[str, object]:
        if not trigger == "consumption.messageProcessed":
            return {}

        message = data["data"]["message"]
        if message["isOwn"]:
            return {}

        content = message["content"]
        if content["@type"] != "Mail":
            return {}

        sender_addr = cast(str, message["createdBy"])
        title = cast(str, content["subject"])
        body = cast(str, content["body"])

        response: ollama.ChatResponse = ollama_client.chat(
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
        reply = response["message"]["content"]
        connector.post_mail_message(
            sender_addr,
            f"re: {title}",
            reply,
        )
        return {}

    return handlerfn
