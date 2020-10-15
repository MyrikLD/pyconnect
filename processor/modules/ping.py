from package import ClientConnection, Package
from processor import Module, kdeconnect


class Ping(Module):
    def ping(self, client: ClientConnection, pkg: Package):
        print(f"{client.id.device_name}: Ping!")

    incoming = {kdeconnect.Ping: ping}
