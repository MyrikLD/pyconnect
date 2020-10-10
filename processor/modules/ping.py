from processor import Module, kdeconnect


class Ping(Module):
    def ping(self, msg):
        print("Ping!")

    incoming = {kdeconnect.Ping: ping}
