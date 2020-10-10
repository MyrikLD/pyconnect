import json
from asyncio import AbstractEventLoop, BaseProtocol, Transport

from pydantic import ValidationError

from package import Package
from package.types import Identity, Pair
from processor import Processor, kdeconnect


class KdeconnectWorkerProtocol(BaseProtocol):
    transport: Transport = None

    def __init__(
        self,
        loop: AbstractEventLoop,
        on_con_lost,
        client: Identity,
        processor: Processor,
    ):
        self.loop = loop
        self.on_con_lost = on_con_lost

        self.client = client

        self.processor = processor

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
        except Exception as e:
            print(f"ERROR: {e}")
            return

        if pkg.type == kdeconnect.Pair:
            self.on_pair(message)

        if pkg.type in self.processor.inconming:
            self.processor.process(pkg)
            # self.processor[pkg.type](message)
        else:
            print(f"No processor for package type: {pkg.type}")

    def error_received(self, exc):
        print("Error received:", exc)

    def connection_lost(self, exc=None):
        print("Connection closed")
        self.on_con_lost.set_result(True)
