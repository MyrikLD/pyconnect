import platform
from typing import List, Optional, Set

from pydantic import BaseModel, Field, validator

from processor import Capability, kdeconnect
from strenum import StrEnum


class DeviceType(StrEnum):
    desktop = "desktop"
    phone = "phone"


class Identity(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    device_id: str = Field(alias="deviceId")
    device_name: str = Field(alias="deviceName")
    device_type: DeviceType = Field(alias="deviceType")
    incoming_capabilities: List[Capability] = Field(alias="incomingCapabilities")
    outgoing_capabilities: List[Capability] = Field(alias="outgoingCapabilities")
    protocol_version: int = Field(alias="protocolVersion")
    tcp_port: Optional[int] = Field(alias="tcpPort")

    @validator(
        "incoming_capabilities", "outgoing_capabilities", each_item=True, pre=True
    )
    def validate_capabilities(cls, v):
        if isinstance(v, Capability):
            return v
        return kdeconnect(v)

    def __repr_args__(self):
        return self.dict(
            exclude={"incoming_capabilities", "outgoing_capabilities"}
        ).items()

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        kwargs["by_alias"] = True
        return super().dict(**kwargs)

    @classmethod
    def me(
        cls,
        device_id: str,
        incoming_capabilities: Set[Capability] = (),
        outgoing_capabilities: Set[Capability] = (),
    ):
        return cls(
            deviceName=platform.node(),
            deviceId=device_id,
            deviceType=DeviceType.desktop,
            protocolVersion=7,
            incomingCapabilities=sorted(incoming_capabilities),
            outgoingCapabilities=sorted(outgoing_capabilities),
            # tcpPort=1716,
        )
