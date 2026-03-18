#!/usr/bin/env -S uv run --script

from typing import TypedDict

import click
import ollama

from enmeshed_bootstrapping import dev_app
from enmeshed_bootstrapping.agents import auto_responder, lsf_agent
from enmeshed_bootstrapping.c2_server import C2Server
from enmeshed_bootstrapping.connector_sdk import ConnectorSDK
from enmeshed_bootstrapping.flows import bootstrap
from enmeshed_bootstrapping.webhook_server import WebhookServer


class LocalAccountDTO(TypedDict):
    id: str
    address: str
    name: str


@click.group()
def cli():
    pass


@cli.command()
def build_app():
    """Compile app."""
    dev_app.build()


@cli.command()
@click.option("--device", default=None, help="ADB device serial")
def install_app(device: str | None):
    """Uninstall old app, then install APK via adb."""
    dev_app.uninstall(device_serial=device)
    dev_app.install(device_serial=device)


@cli.command()
@click.option("--device", default=None, help="ADB device serial")
def start_app(device: str | None = None):
    """Run bootstrap flow."""
    c2 = C2Server()
    connector = ConnectorSDK()
    bootstrap.bootstrap(c2, connector, device_serial=device)


@cli.command()
@click.argument("demo", type=click.Choice(["auto-respond", "lsf"]))
@click.option("--device", default=None, help="ADB device serial")
@click.option("--ollama-host", default=None, help="OLLAMA_HOST")
@click.option(
    "--skip-bootstrap", is_flag=True, default=False, help="Skip the bootstrap flow"
)
def run(
    demo: str,
    device: str | None = None,
    ollama_host: str | None = None,
    skip_bootstrap: bool = False,
) -> None:
    """Run a particular demo."""
    c2 = C2Server()
    connector = ConnectorSDK()
    ollama_client = ollama.Client(host=ollama_host)

    if not skip_bootstrap:
        click.echo("running bootstrap...")
        bootstrap.bootstrap(c2, connector, device_serial=device)

    match demo:
        case "auto-respond":
            click.echo("starting auto responder agent...")
            handlerfn = auto_responder.make_handlerfn(connector, ollama_client)
            webhook_srv = WebhookServer(handlerfn, hostname="0.0.0.0")
            webhook_srv.serve_forever()

        case "lsf":
            click.echo("starting lsf agent...")
            handlerfn = lsf_agent.make_handlerfn(connector, ollama_client)
            webhook_srv = WebhookServer(handlerfn, hostname="0.0.0.0")
            webhook_srv.serve_forever()

        case _:
            raise ValueError(f"no such demo {demo}")


if __name__ == "__main__":
    cli()
