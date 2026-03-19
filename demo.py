#!/usr/bin/env -S uv run --script

from typing import TypedDict

import click

from enmeshed_bootstrapping import dev_app
from enmeshed_bootstrapping.agents.auto_responder import AutoResponder
from enmeshed_bootstrapping.agents.lsf_agent import LSFAgent
from enmeshed_bootstrapping.c2_server import C2Server
from enmeshed_bootstrapping.connector_sdk import ConnectorSDK
from enmeshed_bootstrapping.flows import bootstrap
from enmeshed_bootstrapping.ollama_client import OllamaClient

_OLLAMA_DEFAULT_MODEL = "glm-4.7-flash:q4_K_M"


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
@click.option(
    "--ollama-host", default=None, help="Ollama Host (e.g. http://localhost:11434)"
)
@click.option("--ollama-model", default=_OLLAMA_DEFAULT_MODEL, help="ollama model")
@click.option(
    "--skip-bootstrap", is_flag=True, default=False, help="Skip the bootstrap flow"
)
def run(
    demo: str,
    device: str | None = None,
    ollama_host: str | None = None,
    ollama_model: str | None = None,
    skip_bootstrap: bool = False,
) -> None:
    """Run a particular demo."""
    c2 = C2Server()
    connector = ConnectorSDK()
    if ollama_model is None:
        ollama_model = _OLLAMA_DEFAULT_MODEL
    ollama_client = OllamaClient(model=ollama_model, ollama_host=ollama_host)

    if not skip_bootstrap:
        click.echo("running bootstrap...")
        bootstrap.bootstrap(c2, connector, device_serial=device)

    match demo:
        case "auto-respond":
            agent = AutoResponder(
                connector,
                ollama_client,
                webhook_server_hostname="0.0.0.0",
            )
            agent.init()
            click.echo("starting auto responder agent...")
            agent.serve_forever()

        case "lsf":
            agent = LSFAgent(
                connector,
                ollama_client,
                webhook_server_hostname="0.0.0.0",
            )
            agent.init()
            click.echo("LSF Agent is listening...")
            agent.serve_forever()

        case _:
            raise ValueError(f"no such demo {demo}")


if __name__ == "__main__":
    cli()
