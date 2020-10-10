import notify2

from processor import Module, kdeconnect

notify2.init("PyConnect")


class Notification(Module):
    def __init__(self):
        self.notifications = {}

    def notificate(self, message):
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

    incoming = {kdeconnect.Notification: notificate}
