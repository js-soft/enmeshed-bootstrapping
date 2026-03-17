# pyright: reportMissingTypeStubs=false

import json

from adbutils import AdbDevice
from websockets.sync.server import Server, ServerConnection, serve

from . import adb_lib

APP_ID = "eu.enmeshed.app.dev"
APP_REQUESTED_PERMISSIONS = [
    "android.permission.CAMERA",
    "android.permission.POST_NOTIFICATIONS",
]
C2_WS = {"host": "localhost", "port": 9099}


def wipe_cache(device: AdbDevice) -> None:
    adb_lib.wipe_app_cache(device, APP_ID)


def prepare_device(device: AdbDevice) -> None:
    adb_lib.reverse_port_fwd(device, "tcp:8090", "tcp:8090")
    adb_lib.reverse_port_fwd(device, "tcp:8092", "tcp:8092")
    adb_lib.reverse_port_fwd(device, "tcp:9099", "tcp:9099")
    adb_lib.grant_app_permissions(device, APP_ID, APP_REQUESTED_PERMISSIONS)


def start(
    device: AdbDevice,
    *,
    wipe: bool = True,
):
    if wipe:
        wipe_cache(device)
    prepare_device(device)
    adb_lib.start_app(device, APP_ID, ".MainActivity")


def c2_send(data: dict[object, object]) -> dict[object, object]:
    server: Server | None = None
    result = {}

    def handler(ws: ServerConnection) -> None:
        hello = json.loads(ws.recv())
        assert hello.get("signal") == "connected"
        ws.send(json.dumps(data))
        result["response"] = json.loads(ws.recv())
        ws.close()
        server.shutdown()

    with serve(handler, C2_WS["host"], C2_WS["port"]) as srv:
        server = srv
        srv.serve_forever()

    return result["response"]
