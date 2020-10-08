import json
from asyncio import AbstractEventLoop, BaseProtocol, Transport

import notify2
from pydantic import ValidationError

from package import Package
from package.package import PackageType
from package.types import Identity, Notification, Pair, Ping


class KdeconnectWorkingProtocol(BaseProtocol):
    transport: Transport = None

    def __init__(self, loop: AbstractEventLoop, on_con_lost, client: Identity):
        self.loop = loop
        self.on_con_lost = on_con_lost

        self.client = client

        self.processor = {
            PackageType.pair: self.on_pair,
            PackageType.ping: self.on_ping,
            PackageType.notification: self.on_notification,
        }
        self.notifications = {}

    def on_ping(self, message: Ping):
        print("Ping!")

    def on_notification(self, message: Notification):
        if not message.is_cancel:
            print(f"{message.id}: {message.ticker}")

            n = notify2.Notification(
                message.title,
                message.text,
            )
            self.notifications[message.id] = n
            n.show()
        else:
            print(f"cancel: {message}")
            if message.id in self.notifications:
                self.notifications[message.id].close()

    def on_pair(self, message: Pair):
        print(f"Pairing with {self.client.device_name}")
        self.transport.write(Package.create(Pair(pair=True)).bytes())

    def connection_made(self, transport: Transport):
        self.transport = transport

    def data_received(self, data: bytes):
        text = data.decode()
        decoded = json.loads(text)
        try:
            pkg = Package(**decoded)
        except ValidationError:
            print(f"unknown packet: {decoded}")
            return

        try:
            message = pkg.message
        except:
            print(f"unknown {pkg.type} message: {pkg.body}")
            return

        if pkg.type in self.processor:
            self.processor[pkg.type](message)
        else:
            print(f"No processor for package type: {pkg.type}")
            return

    def error_received(self, exc):
        print("Error received:", exc)

    def connection_lost(self, exc=None):
        print("Connection closed")
        self.on_con_lost.set_result(True)
