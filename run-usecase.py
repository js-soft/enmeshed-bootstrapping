#!/usr/bin/env -S uv run --script

# pyright: reportUnknownMemberType = false, reportMissingTypeStubs = false, reportExplicitAny = false, reportAny = false
# assumes app is built and installed and the connector is running
import time
from datetime import datetime, timedelta
from typing import TypedDict

import click
from adbutils import adb

from enmeshed_bootstrapping import dev_app
from enmeshed_bootstrapping.connector_sdk import ConnectorSDK

CONNECTOR_BASE_URL = "http://localhost:3000"
CONNECTOR_API_KEY = "This_is_a_test_APIKEY_with_30_chars+"


class LocalAccountDTO(TypedDict):
    id: str
    address: str
    name: str


@click.group()
def cli():
    pass


@cli.command()
@click.option("--device", default=None, help="ADB device serial")
@click.option("--no-wipe", is_flag=True, help="Skip wiping app cache")
def start(device: str | None, no_wipe: bool) -> None:
    android_device = adb.device(device)
    dev_app.start(android_device, wipe_cache=not no_wipe)


@cli.command()
@click.option("--device", default=None, help="ADB device serial")
def run(device: str | None):
    android_device = adb.device(device)
    dev_app.start(android_device)

    app_account: LocalAccountDTO = dev_app.c2_send(  # pyright: ignore[reportAssignmentType]
        {
            "action": "createDefaultAccount",
            "name": "Peter Langweilig",
        }
    )["data"]

    connector = ConnectorSDK(base_url=CONNECTOR_BASE_URL, api_key=CONNECTOR_API_KEY)
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


if __name__ == "__main__":
    cli()
