import re


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class Capability:
    base: dict

    def __init__(self, name, parent: "Capability" = None):
        self.parent = parent
        self.name = name

        if not parent:
            self.base = {}
        else:
            self.base = parent.base

        for k, v in type(self).__dict__.items():
            if isinstance(v, type):
                obj = v(camel_to_snake(k), self)
                self.base[str(obj)] = obj
                self.__setattr__(k, obj)

    def __str__(self):
        if self.parent:
            return f"{self.parent}.{self.name}"
        return f"{self.name}"

    __repr__ = __str__


class KDEConnect(Capability):
    Identity = Capability
    Pair = Capability

    class Battery(Capability):
        Request = Capability

    class Bigscreen(Capability):
        SST = Capability

    class Clipboard(Capability):
        Connect = Capability

    class Contacts(Capability):
        RequestAllUidsTimestamps = Capability
        RequestVcardsByUid = Capability
        ResponseUidsTimestamps = Capability
        ResponseVcards = Capability

    class Findmyphone(Capability):
        Request = Capability

    class Lock(Capability):
        Request = Capability

    class Mousepad(Capability):
        Keyboardstate = Capability
        Request = Capability
        Echo = Capability

    class Mpris(Capability):
        Request = Capability

    class Notification(Capability):
        Action = Capability
        Reply = Capability
        Request = Capability

    class Photo(Capability):
        Request = Capability

    Ping = Capability
    Presenter = Capability

    class Runcommand(Capability):
        Request = Capability

    class SFTP(Capability):
        Request = Capability

    class Share(Capability):
        class Request(Capability):
            Update = Capability

    class SMS(Capability):
        Request = Capability
        RequestConversation = Capability
        RequestConversations = Capability
        Messages = Capability

    class Systemvolume(Capability):
        Request = Capability

    class Telephony(Capability):
        RequestMute = Capability

    def __call__(self, text) -> "Capability":
        return self.base[text]


kdeconnect = KDEConnect("kdeconnect")


class Capabilities1:
    incoming = {
        kdeconnect.Battery,  # "kdeconnect.battery",
        kdeconnect.Battery.Request,  # "kdeconnect.battery.request",
        kdeconnect.Bigscreen.SST,  # "kdeconnect.bigscreen.stt",
        kdeconnect.Clipboard,  # "kdeconnect.clipboard",
        kdeconnect.Clipboard.Connect,  # "kdeconnect.clipboard.connect",
        kdeconnect.Contacts.ResponseUidsTimestamps,  # "kdeconnect.contacts.response_uids_timestamps",
        kdeconnect.Contacts.ResponseVcards,  # "kdeconnect.contacts.response_vcards",
        kdeconnect.Findmyphone.Request,  # "kdeconnect.findmyphone.request",
        kdeconnect.Lock,  # "kdeconnect.lock",
        kdeconnect.Lock.Request,  # "kdeconnect.lock.request",
        kdeconnect.Mousepad.Echo,  # "kdeconnect.mousepad.echo",
        kdeconnect.Mousepad.Keyboardstate,  # "kdeconnect.mousepad.keyboardstate",
        kdeconnect.Mousepad.Request,  # "kdeconnect.mousepad.request",
        kdeconnect.Mpris,  # "kdeconnect.mpris",
        kdeconnect.Mpris.Request,  # "kdeconnect.mpris.request",
        kdeconnect.Notification,  # "kdeconnect.notification",
        kdeconnect.Notification.Request,  # "kdeconnect.notification.request",
        kdeconnect.Photo,  # "kdeconnect.photo",
        kdeconnect.Ping,  # "kdeconnect.ping",
        kdeconnect.Presenter,  # "kdeconnect.presenter",
        kdeconnect.Runcommand,  # "kdeconnect.runcommand",
        kdeconnect.Runcommand.Request,  # "kdeconnect.runcommand.request",
        kdeconnect.SFTP,  # "kdeconnect.sftp",
        kdeconnect.Share.Request,  # "kdeconnect.share.request",
        kdeconnect.SMS.Messages,  # "kdeconnect.sms.messages",
        kdeconnect.Systemvolume,  # "kdeconnect.systemvolume",
        kdeconnect.Systemvolume.Request,  # "kdeconnect.systemvolume.request",
        kdeconnect.Telephony,  # "kdeconnect.telephony",
    }
    outgoing = {
        kdeconnect.Battery,  # "kdeconnect.battery",
        kdeconnect.Battery.Request,  # "kdeconnect.battery.request",
        kdeconnect.Bigscreen.SST,  # "kdeconnect.bigscreen.stt",
        kdeconnect.Clipboard,  # "kdeconnect.clipboard",
        kdeconnect.Clipboard.Connect,  # "kdeconnect.clipboard.connect",
        kdeconnect.Contacts.RequestAllUidsTimestamps,  # "kdeconnect.contacts.request_all_uids_timestamps",
        kdeconnect.Contacts.RequestVcardsByUid,  # "kdeconnect.contacts.request_vcards_by_uid",
        kdeconnect.Findmyphone.Request,  # "kdeconnect.findmyphone.request",
        kdeconnect.Lock,  # "kdeconnect.lock",
        kdeconnect.Lock.Request,  # "kdeconnect.lock.request",
        kdeconnect.Mousepad.Keyboardstate,  # "kdeconnect.mousepad.keyboardstate",
        kdeconnect.Mousepad.Request,  # "kdeconnect.mousepad.request",
        kdeconnect.Mpris,  # "kdeconnect.mpris",
        kdeconnect.Mpris.Request,  # "kdeconnect.mpris.request",
        kdeconnect.Notification,  # "kdeconnect.notification",
        kdeconnect.Notification.Action,  # "kdeconnect.notification.action",
        kdeconnect.Notification.Reply,  # "kdeconnect.notification.reply",
        kdeconnect.Notification.Request,  # "kdeconnect.notification.request",
        kdeconnect.Photo.Request,  # "kdeconnect.photo.request",
        kdeconnect.Ping,  # "kdeconnect.ping",
        kdeconnect.Runcommand,  # "kdeconnect.runcommand",
        kdeconnect.Runcommand.Request,  # "kdeconnect.runcommand.request",
        kdeconnect.SFTP.Request,  # "kdeconnect.sftp.request",
        kdeconnect.Share.Request,  # "kdeconnect.share.request",
        kdeconnect.Share.Request.Update,  # "kdeconnect.share.request.update",
        kdeconnect.SMS.Request,  # "kdeconnect.sms.request",
        kdeconnect.SMS.RequestConversation,  # "kdeconnect.sms.request_conversation",
        kdeconnect.SMS.RequestConversations,  # "kdeconnect.sms.request_conversations",
        kdeconnect.Systemvolume,  # "kdeconnect.systemvolume",
        kdeconnect.Systemvolume.Request,  # "kdeconnect.systemvolume.request",
        kdeconnect.Telephony.RequestMute,  # "kdeconnect.telephony.request_mute",
    }
