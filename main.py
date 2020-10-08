import asyncio
from socket import (
    create_connection,
)

import notify2

from cert import generate_selfsigned_cert
from encryption import context
from package import Package
from package.types import Identity
from protocol.discovery import KdeconnectDiscoveryProtocol
from protocol.dispatcher import KdeconnectWorkingProtocol

notify2.init("PyConnect")


async def main():
    print("Starting detection")

    my_id = Identity.me()
    cert_pem, key_pem = generate_selfsigned_cert(my_id.device_id)
    with open("cert.pem", "wb") as f:
        f.write(cert_pem)
    with open("key.pem", "wb") as f:
        f.write(key_pem)

    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: KdeconnectDiscoveryProtocol(loop, on_con_lost, timeout=60, first=True),
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

    client_ip = list(clients)[0]
    client_id: Identity = clients[client_ip]

    print(f"connect to: {client_ip}")

    on_con_lost = loop.create_future()

    with create_connection((str(client_ip), client_id.tcp_port)) as sock:
        id_pkg = Package.create(Identity.me())
        sock.send(id_pkg.bytes())

        ssl_ctx = context()

        with ssl_ctx.wrap_socket(sock, server_side=True) as ssock:
            transport, protocol = await loop.create_connection(
                lambda: KdeconnectWorkingProtocol(loop, on_con_lost, client=client_id),
                sock=ssock,
            )

            try:
                await on_con_lost
            finally:
                transport.close()


asyncio.run(main())
