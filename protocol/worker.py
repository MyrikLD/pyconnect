import asyncio
import json
from asyncio import BaseProtocol, Transport
from logging import getLogger

from pydantic import ValidationError

from package import Package
from package.client import ClientConnection
from processor import Processor


class KdeconnectWorkerProtocol(BaseProtocol):
    transport: Transport = None

    def __init__(
        self,
        on_con_lost,
        client_connection: ClientConnection,
        processor: Processor,
    ):
        self.on_con_lost = on_con_lost
        self.client_connection = client_connection
        self.processor = processor
        self.log = getLogger(self.__class__.__name__)

    @property
    def loop(self):
        return asyncio.get_event_loop()

    def connection_made(self, transport: Transport):
        self.transport = transport

    def data_received(self, data: bytes):
        self.log.debug(f"{self.client_connection.id.device_name}: {len(data)}")
        text = data.decode(errors="backslashreplace")
        decoded = json.loads(text)
        self.log.info(decoded)
        try:
            pkg = Package(**decoded)
        except ValidationError:
            self.log.error(f"unknown packet: {decoded}")
            return

        if pkg.type in self.processor.inconming:
            try:
                self.processor.process(self.client_connection, pkg)
            except Exception as e:
                self.log.exception(e)
        else:
            self.log.error(f"No processor for package type: {pkg.type}")

    def error_received(self, exc):
        self.log.error("Error received:", exc)

    def connection_lost(self, exc=None):
        self.log.info(f"Connection closed: {exc}")
        self.on_con_lost.set_result(True)
