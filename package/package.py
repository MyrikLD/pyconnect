import hashlib
import socket
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from OpenSSL import SSL, crypto
from pydantic import BaseModel, Field, ValidationError, validator

from processor.capability import Capability, kdeconnect
from .types import Identity, Notification, Pair, Ping

if TYPE_CHECKING:
    from . import ClientConnection

package_types = {
    kdeconnect.Identity: Identity,
    kdeconnect.Pair: Pair,
    kdeconnect.Ping: Ping,
    kdeconnect.Notification: Notification,
}


class PayloadTransferInfo(BaseModel):
    port: int


class Package(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: int
    type: Capability
    body: dict

    payload_size: Optional[int] = Field(alias="payloadSize")
    payload_transfer_info: Optional[PayloadTransferInfo] = Field(
        alias="payloadTransferInfo"
    )

    def read_payload(self, client: "ClientConnection", payload_hash) -> bytes:
        def verify_cb(conn, cert, errnum, depth, ok):
            old_cert = crypto.load_certificate(
                crypto.FILETYPE_PEM, client.cert.encode()
            )
            if old_cert.to_cryptography() != cert.to_cryptography():
                raise Exception("Certificate error")
            return 1

        ctx = SSL.Context(method=SSL.TLSv1_2_METHOD)
        ciphers = [
            "ECDHE-ECDSA-AES256-GCM-SHA384",
            "ECDHE-ECDSA-AES128-GCM-SHA256",
            "ECDHE-RSA-AES128-SHA",
        ]
        ctx.set_cipher_list(":".join(ciphers).encode())
        ctx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb)

        ctx.use_privatekey_file("key.pem")
        ctx.use_certificate_file("cert.pem")

        sock = SSL.Connection(ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        sock.connect((str(client.ip), self.payload_transfer_info.port))
        sock.do_handshake()
        data = sock.recv(self.payload_size)

        if payload_hash != hashlib.md5(data).hexdigest():
            raise Exception('Invalid payload hash')

        return data

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

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        kwargs["by_alias"] = True
        return super().dict(**kwargs)
