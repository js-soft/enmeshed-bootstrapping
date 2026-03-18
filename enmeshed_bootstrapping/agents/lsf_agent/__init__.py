# pyright: reportUnknownMemberType = false, reportExplicitAny = false, reportAny = false, reportIndexIssue = false, reportUnknownVariableType = false

from typing import cast

import ollama

from enmeshed_bootstrapping.connector_sdk import ConnectorSDK
from enmeshed_bootstrapping.webhook_server import HandlerFn

_SYSTEM_PROMPT = """Du bist ein LSF-Agent innerhalb einer Universitätsverwaltungssoftware, der den Self-Service der Studenten unterstützt. Du besitzt folgende Funktionen:

- Versand des aktuellen Immatrikulationsbescheids
- Versand des aktuellen Transcript-of-Records bzw. Notenspiegels

Du erhältst Nachrichten von Studenten in Form von Betreff und Inhalt. Analysiere das Anliegen des Studierenden und beantworte seine Fragen oder gehe seinen Aufforderungen nach, ggf. durch Toolscalls. Wenn kein Toolcall zum Anliegen passt oder du die Fragen nicht beantworten kannst, antworte höflich, dass du die Anfrage nicht verarbeiten kannst."""

# Usecases
# --------
# - Transcript schicken
# - aktuelle Imma
# - matrikelnummer veregessen
# - anmeldung Prüfung


def make_handlerfn(
    connector: ConnectorSDK,
    ollama_client: ollama.Client,
) -> HandlerFn:
    def handlerfn(
        trigger: str,
        data: dict[str, object],
    ) -> dict[str, object]:
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
            model="llama3.1:8b",
            messages=[
                {
                    "role": "system",
                    "content": _SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Betreff: {title}\nInhalt: {body}",
                },
            ],
            tools=[send_immatrikulationsbescheid, send_transcript],
            think=False,
        )

        if response.message.tool_calls:
            for call in response.message.tool_calls:
                match call.function.name:
                    case "send_transcript":
                        connector.post_message(
                            sender_addr,
                            "send_transcript() called",
                            "",
                        )
                    case "send_immatrikulationsbescheid":
                        connector.post_message(
                            sender_addr,
                            "send_immatrikulationsbescheid() called",
                            "",
                        )
                    case _ as fnname:
                        raise ValueError(f"invalid function call {fnname}")
        else:
            reply = response["message"]["content"]
            connector.post_message(
                sender_addr,
                f"re: {title}",
                reply,
            )
        return {}

    return handlerfn


def send_immatrikulationsbescheid() -> None:
    """Schickt eine Nachricht mit dem aktuellen Immatrikulationsbescheid an den Studierenden. Der Bescheid wird als PDF Dokument versendet."""
    return None


def send_transcript() -> None:
    """Schickt eine Nachricht mit dem aktuellen Notenspiegel an den Studierenden. Der Bescheid wird als PDF Dokument versendet."""
    return None
