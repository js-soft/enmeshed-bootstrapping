import time
from datetime import datetime, timedelta
from typing import TypedDict

from enmeshed_bootstrapping import c2_server, dev_app
from enmeshed_bootstrapping.connector_sdk import ConnectorSDK


class LocalAccountDTO(TypedDict):
    id: str
    address: str
    name: str


def bootstrap(
    c2: c2_server.C2Server,
    connector: ConnectorSDK,
    *,
    device_serial: str | None = None,
):
    dev_app.start(device_serial=device_serial)

    c2.connect()
    response = c2.call(
        "createDefaultAccount",
        {
            "name": "Peter Langweilig",
        },
    )
    assert response["ok"]
    app_account: LocalAccountDTO = response["data"]  # pyright: ignore[reportGeneralTypeIssues, reportAssignmentType, reportUnknownVariableType]

    response = connector.post_own_rlt(
        content={
            "@type": "RelationshipTemplateContent",
            "title": "Huhu =)",
            "onNewRelationship": {
                "@type": "Request",
                "items": [
                    {
                        "@type": "ConsentRequestItem",
                        "consent": "...",
                        "requiresInteraction": False,
                        "mustBeAccepted": False,
                    }
                ],
            },
        },
        expires_at=datetime.now() + timedelta(days=1),
        max_num_allocs=100,
    )
    truncref = response.result.reference.truncated

    _ = c2.call(
        "acceptRelationshipTemplate",
        {
            "accountId": app_account["id"],
            "truncRef": truncref,
        },
    )

    while True:
        rels = connector.get_relationships(peer=app_account["address"], status="Active")
        if len(rels.result) > 0:
            break
        time.sleep(0.5)

    connector.post_mail_message(
        app_account["address"],
        f"Willkommen, {app_account['name']}",
        "Herzlich willkommen.",
    )

    _ = c2.call(
        "navigate",
        {
            "path": f"/account/{app_account['id']}",
        },
    )
