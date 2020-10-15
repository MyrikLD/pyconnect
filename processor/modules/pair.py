from cert_store import ClientCertsStore
from package import ClientConnection, Package
from package.types import Pair as PairMessage
from processor import Module, kdeconnect


class Pair(Module):
    def pair(self, client: ClientConnection, pkg: Package):
        message = pkg.message
        store = ClientCertsStore("devices.json")

        if message.pair:
            print(f"pair with {client.id.device_name}")
            store.add(client)

            client.sock.send(Package.create(PairMessage(pair=True)).bytes())
        else:
            store.remove(client)

    incoming = {kdeconnect.Pair: pair}
