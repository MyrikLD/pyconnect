import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from package import ClientConnection


class ClientCertsStore:
    def __init__(self, filename: str):
        self.filename = filename

    def _read(self):
        try:
            with open(self.filename, "r") as f:
                devices = json.load(f) or {}
        except:
            devices = {}

        return devices

    def _write(self, devices):
        with open(self.filename, "w") as f:
            json.dump(devices, f)

    def add(self, client: "ClientConnection"):
        devices = self._read()

        devices[client.id.device_id] = client.cert

        self._write(devices)

    def remove(self, client: "ClientConnection"):
        devices = self._read()

        devices[client.id.device_id] = {
            k: v for k, v in devices.items() if k != client.id.device_id
        }

        self._write(devices)

    def get(self, device_id, default=None):
        return self._read().get(device_id, default)
