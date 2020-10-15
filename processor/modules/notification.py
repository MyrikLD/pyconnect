import os

import notify2

from package import ClientConnection, Package
from package.types import Notification as NotificationMessage
from processor import Module, kdeconnect

notify2.init("PyConnect")


class Notification(Module):
    def __init__(self):
        self.notifications = {}
        super().__init__()

    def notificate(self, client: ClientConnection, pkg: Package):
        message: NotificationMessage = pkg.message

        img_path = os.path.abspath(f"images/{message.appName}.png")

        if pkg.payload_size:
            try:
                data = pkg.read_payload(client, message.payload_hash)
            except Exception as e:
                self.log.exception(e)
            else:
                with open(img_path, "wb") as f:
                    f.write(data)

        if not message.is_cancel:
            # if message.id in self.notifications:
            #     return

            self.log.info(f"{client.id.device_name}: {message.ticker}")

            notify_params = {
                "summary": message.title,
                "message": message.text,
            }
            if os.path.isfile(img_path):
                notify_params["icon"] = img_path

            n = notify2.Notification(**notify_params)
            self.notifications[message.id] = n
            n.show()

            self.log.info(message)
        else:
            if message.id in self.notifications:
                self.notifications[message.id].close()

    incoming = {kdeconnect.Notification: notificate}
