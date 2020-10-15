import asyncio
import logging
from socket import (
    AF_INET,
    SOCK_STREAM,
    socket,
)

from OpenSSL import SSL, crypto
from OpenSSL.crypto import X509

from cert import cert_name, load_keys
from cert_store import ClientCertsStore
from package import Package
from package.client import Client, ClientConnection
from package.types import Identity
from processor import Processor
from processor.modules.clipboard import Clipboard
from processor.modules.notification import Notification
from processor.modules.pair import Pair
from processor.modules.ping import Ping
from protocol.discovery import KdeconnectDiscoveryProtocol
from protocol.worker import KdeconnectWorkerProtocol


def get_ssock(me: Identity, client: Client):
    store = ClientCertsStore("devices.json")

    def verify_cb(conn, cert: X509, errnum, depth, ok):
        if not ok and errnum != 18:
            raise Exception("Not self-signed cert")
        if cert.get_issuer().CN != client.id.device_id:
            raise Exception("Invalid cert name")

        old_cert_text = store.get(client.id.device_id)
        if old_cert_text:
            old_cert = crypto.load_certificate(crypto.FILETYPE_PEM, old_cert_text)
            if old_cert.to_cryptography() != cert.to_cryptography():
                raise Exception("Cert not equal")

        return True

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

    sock = socket(AF_INET, SOCK_STREAM)

    ssock = SSL.Connection(context=ctx, socket=sock)
    ssock.set_accept_state()

    sock.connect((str(client.ip), client.port))

    ssock.setblocking(1)
    sock.send(Package.create(me).bytes())

    ssock.do_handshake()

    return ssock


async def work_with_client(me: Identity, client: Client, processor: Processor):
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()
    # ssl_ctx = context()

    # client_cert = get_cert(me, client)
    # ssl_ctx.load_verify_locations(cafile='asd.pem')

    ssock = get_ssock(me, client)
    cert = crypto.dump_certificate(
        crypto.FILETYPE_PEM, ssock.get_peer_certificate()
    ).decode()

    cc = ClientConnection(**client.dict(), sock=ssock, cert=cert)

    transport, protocol = await loop.create_connection(
        lambda: KdeconnectWorkerProtocol(
            on_con_lost, client_connection=cc, processor=processor
        ),
        sock=ssock,
    )
    try:
        await on_con_lost
    finally:
        transport.close()


async def main():
    processor = Processor([Notification(), Ping(), Pair(), Clipboard()])
    keys = load_keys()
    me = Identity.me(
        cert_name(keys[0]),
        incoming_capabilities=set(processor.inconming),
        outgoing_capabilities=set(processor.outgoing),
    )

    print("Starting detection")

    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    protocol: KdeconnectDiscoveryProtocol
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: KdeconnectDiscoveryProtocol(on_con_lost, id=me, timeout=60, first=True),
        local_addr=("0.0.0.0", 1716),
    )

    try:
        await on_con_lost
    finally:
        transport.close()
        clients = protocol.clients

    print(list(clients))

    if not clients:
        print("No client detected")
        return
    if len(clients) > 1:
        print(f"Multiple clients detected: {[i.id.device_id for i in clients]}")

    client = clients[0]

    print(f"connect to: {client}")

    await work_with_client(me, client, processor)


logging.basicConfig(level=logging.DEBUG)
asyncio.run(main())
