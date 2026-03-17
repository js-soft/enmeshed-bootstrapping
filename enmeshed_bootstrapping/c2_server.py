import json
import queue
import socket
from threading import Thread
from typing import Literal, TypedDict

from websockets.server import ServerProtocol
from websockets.sync.server import ServerConnection

# As Host: C2 Server
_C2_SERVER_HOSTNAME = "localhost"
_C2_SERVER_PORT = 9099


class RCPResponseOk(TypedDict):
    ok: Literal[True]
    data: dict[str, object]


class RCPResponseError(TypedDict):
    ok: Literal[False]
    error: str


RCPResponse = RCPResponseOk | RCPResponseError


def _worker(
    ws_server_host: str,
    ws_server_port: int,
    miso: queue.Queue[str],
    mosi: queue.Queue[str],
) -> None:
    sock = socket.create_server((ws_server_host, ws_server_port))
    while True:
        conn_sock, _ = sock.accept()  # pyright: ignore[reportAny]
        conn_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        protocol = ServerProtocol()
        ws = ServerConnection(conn_sock, protocol)
        try:
            ws.handshake()
            miso.put("")  # send client-connected signal
            while True:
                msg = str(mosi.get())
                ws.send(msg)
                response = str(ws.recv())
                miso.put(response)
        except Exception:
            ws.close()


class C2Server:
    miso: queue.Queue[str]
    mosi: queue.Queue[str]
    thread: Thread

    def __init__(
        self,
        ws_server_hostname: str = _C2_SERVER_HOSTNAME,
        ws_server_port: int = _C2_SERVER_PORT,
    ) -> None:
        self.miso = queue.Queue()
        self.mosi = queue.Queue()
        self.thread = Thread(
            target=_worker,
            args=(
                ws_server_hostname,
                ws_server_port,
                self.miso,
                self.mosi,
            ),
            daemon=True,
        )

    def connect(self) -> None:
        self.thread.start()

        # wait for client-connected signal
        _ = self.miso.get()

    def call(self, action: str, data: dict[str, object]) -> RCPResponse:
        msg = json.dumps({"action": action} | data)
        self.mosi.put(msg)
        return json.loads(self.miso.get())  # pyright: ignore[reportAny]
