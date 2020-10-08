from datetime import datetime

from pydantic import BaseModel

from strenum import StrEnum
from .types import Identity, Notification, Pair, Ping


class PackageType(StrEnum):
    identity = "kdeconnect.identity"
    pair = "kdeconnect.pair"
    ping = "kdeconnect.ping"
    notification = "kdeconnect.notification"


package_types = {
    PackageType.identity: Identity,
    PackageType.pair: Pair,
    PackageType.ping: Ping,
    PackageType.notification: Notification,
}


class Package(BaseModel):
    body: dict
    id: int
    type: PackageType

    @property
    def message(self):
        return package_types[self.type](**self.body)

    @property
    def timestamp(self):
        return datetime.utcfromtimestamp(int(self.id // 1000))

    @classmethod
    def create(cls, obj: BaseModel):
        t = {v: k for k, v in package_types.items()}[type(obj)]
        return cls(
            id=int(datetime.utcnow().timestamp() * 1000),
            type=t,
            body=obj.dict(by_alias=True),
        )

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data["id"] = str(data["id"])
        return data

    def bytes(self) -> bytes:
        return (self.json() + "\n").encode()
