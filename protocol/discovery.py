import json
from asyncio import BaseEventLoop, DatagramTransport, TimerHandle, Transport
from ipaddress import IPv4Address
from socket import (
    SOL_SOCKET,
    SO_BROADCAST,
    SO_REUSEADDR,
)
from typing import Dict, Tuple

from package import Package
from package.types import Identity
from processor.capability import kdeconnect


class KdeconnectDiscoveryProtocol(DatagramTransport):
    transport: Transport = None
    discover_task: TimerHandle
    clients: Dict[IPv4Address, Identity]

    def __init__(
        self,
        loop: BaseEventLoop,
        on_con_lost,
        id: Identity,
        first=True,
        timeout=5,
    ):
        self.loop = loop
        self.on_con_lost = on_con_lost

        self.clients = {}
        self.first = first
        self.timeout = timeout
        self.id = id

        super().__init__()

    def connection_made(self, transport: Transport):
        self.transport = transport

        sock = transport.get_extra_info("socket")
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.loop.call_later(self.timeout, self.transport.close)
        self.discover_task = self.loop.call_later(1, self.discover)

    def discover(self):
        package = Package.create(self.id)

        self.transport.sendto(package.bytes(), ("<broadcast>", 43594))

        self.discover_task = self.loop.call_later(1, self.discover)

    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        ip = IPv4Address(addr[0])

        if ip in self.clients:
            return

        # try:
        package = Package(**json.loads(data.decode()))
        # except Exception as e:
        #     print(e, file=sys.stderr)
        #     return

        if package.type != kdeconnect.Identity:
            return

        # try:
        message: Identity = package.message
        # except Exception as e:
        #     print(e, file=sys.stderr)
        #     return

        if message.device_id == self.id.device_id:
            return

        self.clients[ip] = message
        print(f"find client: {message.device_name}[{message.device_id}]")

        if self.first:
            self.transport.close()

    def error_received(self, exc):
        print("Error received:", exc)

    def connection_lost(self, exc=None):
        self.discover_task.cancel()
        print("Discovery closed")
        self.on_con_lost.set_result(True)
