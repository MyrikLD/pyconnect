from datetime import datetime

from pydantic import BaseModel, ValidationError, validator

from processor.capability import Capability, kdeconnect
from .types import Identity, Notification, Pair, Ping

package_types = {
    kdeconnect.Identity: Identity,
    kdeconnect.Pair: Pair,
    kdeconnect.Ping: Ping,
    kdeconnect.Notification: Notification,
}


class Package(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: int
    type: Capability
    body: dict

    @validator("type", pre=True)
    def capability_validator(cls, v):
        if isinstance(v, Capability):
            return v
        return kdeconnect(v)

    @property
    def message(self):
        try:
            return package_types[self.type](**self.body)
        except ValidationError:
            raise Exception(f"Unknown {self.type} message: {self.body}")

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

    def bytes(self) -> bytes:
        return (self.json() + "\n").encode()

    @staticmethod
    def __json_encoder__(v):
        return str(v)
