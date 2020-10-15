import asyncio
import json
from asyncio import DatagramTransport, TimerHandle, Transport
from ipaddress import IPv4Address
from logging import getLogger
from socket import (
    SOL_SOCKET,
    SO_BROADCAST,
    SO_REUSEADDR,
)
from typing import List, Tuple

from package import Package
from package.client import Client
from package.types import Identity
from processor.capability import kdeconnect


class KdeconnectDiscoveryProtocol(DatagramTransport):
    transport: Transport = None
    discover_task: TimerHandle
    clients: List[Client]

    def __init__(
        self,
        on_con_lost,
        id: Identity,
        first=True,
        timeout=5,
    ):
        self.on_con_lost = on_con_lost

        self.clients = []
        self.first = first
        self.timeout = timeout
        self.id = id
        self.log = getLogger(self.__class__.__name__)

        super().__init__()

    @property
    def loop(self):
        return asyncio.get_event_loop()

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

        try:
            package = Package(**json.loads(data.decode()))
        except Exception as e:
            self.log.exception(e)
            return

        if package.type != kdeconnect.Identity:
            return

        try:
            message: Identity = package.message
        except Exception as e:
            self.log.exception(e)
            return

        if message.device_id == self.id.device_id:
            return

        self.clients.append(Client(ip=ip, id=message))
        self.log.info(f"find client: {message.device_name}[{message.device_id}]")

        if self.first:
            self.transport.close()

    def error_received(self, exc):
        self.log.exception("Error received: %s", exc)

    def connection_lost(self, exc=None):
        self.discover_task.cancel()
        self.log.info("Discovery closed: %s", exc)
        self.on_con_lost.set_result(True)
