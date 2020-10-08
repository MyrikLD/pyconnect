import platform
import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

from strenum import StrEnum


class DeviceType(StrEnum):
    desktop = "desktop"
    phone = "phone"


class Identity(BaseModel):
    device_id: str = Field(alias="deviceId")
    device_name: str = Field(alias="deviceName")
    device_type: DeviceType = Field(alias="deviceType")
    incoming_capabilities: List[str] = Field(alias="incomingCapabilities")
    outgoing_capabilities: List[str] = Field(alias="outgoingCapabilities")
    protocol_version: int = Field(alias="protocolVersion")
    tcp_port: Optional[int] = Field(alias="tcpPort")

    def __repr_args__(self):
        return self.dict(
            exclude={"incoming_capabilities", "outgoing_capabilities"}
        ).items()

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        return super().dict(**kwargs)

    @classmethod
    def me(cls):
        device_id = "_".join(str(i) for i in uuid.uuid1().fields[1:])
        return cls(
            deviceName=platform.node(),
            deviceId=f"_{device_id}_",
            deviceType=DeviceType.desktop,
            protocolVersion=7,
            incomingCapabilities=[
                "kdeconnect.notification",
                "kdeconnect.notification.request",
                "kdeconnect.ping",
            ],
            outgoingCapabilities=[
                "kdeconnect.notification",
                "kdeconnect.notification.request",
                "kdeconnect.notification.action",
                "kdeconnect.notification.reply",
                "kdeconnect.ping",
            ],
            # tcpPort=1716,
        )
