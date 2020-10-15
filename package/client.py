from ipaddress import IPv4Address

from OpenSSL import SSL
from pydantic import BaseModel

from package.types import Identity


class Client(BaseModel):
    ip: IPv4Address
    id: Identity

    @property
    def port(self) -> int:
        return self.id.tcp_port

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        kwargs["by_alias"] = True
        return super().dict(**kwargs)


class ClientConnection(Client):
    class Config:
        arbitrary_types_allowed = True

    sock: SSL.Connection
    cert: str
