#!/usr/bin/env -S uv run --script

import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypedDict

import click
from adbutils import adb  # pyright: ignore[reportMissingTypeStubs]

from enmeshed_bootstrapping import adb_lib, c2_client, dev_app
from enmeshed_bootstrapping.connector_sdk import ConnectorSDK

BB_CONSUMER_API_BASE_URL = "http://localhost:8090"
BB_CONSUMER_API_CLIENT_ID = "test"
BB_CONSUMER_API_CLIENT_SECRET = "test"
BB_SSE_BASE_URL = "http://localhost:8092"
C2_CLIENT_URL = "ws://localhost:9099"
C2_SERVER_HOSTNAME = "localhost"
C2_SERVER_PORT = 9099
CONNECTOR_BASE_URL = "http://localhost:3000"
CONNECTOR_API_KEY = "This_is_a_test_APIKEY_with_30_chars+"

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR / "repos" / "nmshd_app_fork"
APP_DIR = REPO_DIR / "apps" / "enmeshed"
APK_PATH = APP_DIR / "build" / "app" / "outputs" / "flutter-apk" / "app-debug.apk"


def sh(cmd: list[str], cwd: Path | None = None) -> None:
    _ = subprocess.run(cmd, check=True, cwd=cwd)


class LocalAccountDTO(TypedDict):
    id: str
    address: str
    name: str


@click.group()
def cli():
    pass


@cli.command()
def build_app():
    """Clone repo (if needed), run melos bootstrap, generate translations, build debug APK."""
    if not REPO_DIR.exists():
        REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
        sh(["git", "clone", "git@github.com:js-soft/nmshd_app_fork.git", str(REPO_DIR)])

    sh(["melos", "bootstrap"], cwd=REPO_DIR)
    sh(["melos", "generate_translations"], cwd=REPO_DIR)
    sh(
        [
            "flutter",
            "build",
            "apk",
            "--debug",
            "--dart-define",
            f"app_baseUrl={BB_CONSUMER_API_BASE_URL}",
            "--dart-define",
            f"app_clientId={BB_CONSUMER_API_CLIENT_ID}",
            "--dart-define",
            f"app_clientSecret={BB_CONSUMER_API_CLIENT_SECRET}",
            "--dart-define",
            f"app_sseBaseUrl={BB_SSE_BASE_URL}",
            "--dart-define",
            f"app_c2Url={C2_CLIENT_URL}",
        ],
        cwd=APP_DIR,
    )


@cli.command()
@click.option("--device", default=None, help="ADB device serial")
def install_app(device: str | None):
    """Uninstall old app, then install APK via adb."""
    if not APK_PATH.exists():
        raise click.ClickException(
            f"APK not found at {APK_PATH} — run 'build-app' first"
        )

    android_device = adb.device(device)
    adb_lib.uninstall_app(android_device, dev_app.NMSHD_APP_ID)
    adb_lib.install_app(android_device, str(APK_PATH))


# XXX: start --no-bootstrap
@cli.command()
@click.option("--device", default=None, help="ADB device serial")
@click.option("--no-wipe", is_flag=True, help="Skip wiping app cache")
def start_app(device: str | None, no_wipe: bool):
    """Prepare device (port fwd, permissions, wipe) and launch app."""
    android_device = adb.device(device)
    dev_app.start(android_device, wipe_cache=not no_wipe)


@cli.command()
@click.option("--device", default=None, help="ADB device serial")
@click.option("--no-wipe", is_flag=True, help="Skip wiping app cache")
def bootstrap_demo(device: str | None, no_wipe: bool):
    """Full demo: start app, create account, establish relationship, send message."""
    android_device = adb.device(device)
    dev_app.start(android_device, wipe_cache=not no_wipe)

    c2 = c2_client.C2Server(C2_SERVER_HOSTNAME, C2_SERVER_PORT)
    c2.connect()

    response = c2.call(
        "createDefaultAccount",
        {
            "name": "Peter Langweilig",
        },
    )
    assert response["ok"]
    app_account: LocalAccountDTO = response["data"]  # pyright: ignore[reportGeneralTypeIssues, reportAssignmentType, reportUnknownVariableType]

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

    connector.post_message(
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


if __name__ == "__main__":
    cli()
