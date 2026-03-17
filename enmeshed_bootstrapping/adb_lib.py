# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
from adbutils import AdbDevice, adb


def get_device() -> AdbDevice:
    return adb.device()


def wipe_app_cache(device: AdbDevice, app_id: str) -> None:
    _ = device.shell(
        [
            "pm",
            "clear",
            app_id,
        ]
    )


def grant_app_permissions(
    device: AdbDevice,
    app_id: str,
    permissions: list[str],
) -> None:
    for p in permissions:
        _ = device.shell(
            [
                "pm",
                "grant",
                app_id,
                p,
            ]
        )


def start_app(
    device: AdbDevice,
    app_id: str,
    activity: str,
) -> None:
    _ = device.shell(
        [
            "am",
            "start",
            "-n",
            f"{app_id}/{activity}",
        ]
    )


def reverse_port_fwd(
    device: AdbDevice,
    device_port: str,
    host_port: str,
) -> None:
    device.reverse(device_port, host_port)


def uninstall_app(device: AdbDevice, package: str) -> None:
    """Uninstall an app. No-op if not installed."""
    result = device.shell(["pm", "list", "packages", package])
    if package in result:
        _ = device.shell(["pm", "uninstall", package])


def install_app(device: AdbDevice, apk_path: str) -> None:
    """Install an APK from a local file path."""
    device.install(apk_path)
