# pyright: reportMissingTypeStubs=false

from adbutils import AdbDevice

from . import adb_lib

NMSHD_APP_ID = "eu.enmeshed.app.dev"
_APP_REQUESTED_PERMISSIONS = [
    "android.permission.CAMERA",
    "android.permission.POST_NOTIFICATIONS",
]


def _wipe_cache(device: AdbDevice) -> None:
    adb_lib.wipe_app_cache(device, NMSHD_APP_ID)


def _grant_permissions(device: AdbDevice) -> None:
    adb_lib.grant_app_permissions(device, NMSHD_APP_ID, _APP_REQUESTED_PERMISSIONS)


def start(
    device: AdbDevice,
    *,
    wipe_cache: bool = True,
    grant_permissions: bool = True,
):
    if wipe_cache:
        _wipe_cache(device)

    if grant_permissions:
        _grant_permissions(device)

    adb_lib.reverse_port_fwd(device, "tcp:8090", "tcp:8090")
    adb_lib.reverse_port_fwd(device, "tcp:8092", "tcp:8092")
    adb_lib.reverse_port_fwd(device, "tcp:9099", "tcp:9099")

    adb_lib.start_app(device, NMSHD_APP_ID, ".MainActivity")
