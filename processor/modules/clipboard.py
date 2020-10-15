import pyperclip

from package import ClientConnection, Package
from processor import Module, kdeconnect


class Clipboard(Module):
    def clipboard(self, client: ClientConnection, pkg: Package):
        message = pkg.message
        pyperclip.copy(message.content)

    def connect(self, client: ClientConnection, pkg: Package):
        pass
        kdeconnect

    incoming = {
        kdeconnect.Clipboard: clipboard,
        kdeconnect.Clipboard.Connect: connect,
    }
