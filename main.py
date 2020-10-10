import asyncio
from socket import (
    create_connection,
)

from cert import cert_name, load_keys
from encryption import context
from package import Package
from package.types import Identity
from processor import Processor
from processor.modules.notification import Notification
from processor.modules.ping import Ping
from protocol.discovery import KdeconnectDiscoveryProtocol
from protocol.worker import KdeconnectWorkerProtocol


async def main():
    processor = Processor([Notification(), Ping()])
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
        lambda: KdeconnectDiscoveryProtocol(
            loop, on_con_lost, id=me, timeout=60, first=True
        ),
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
        print(f"Multiple clients detected: {[i.device_id for i in clients.values()]}")

    client_ip = list(clients)[0]
    client_id: Identity = clients[client_ip]

    print(f"connect to: {client_ip}")

    on_con_lost = loop.create_future()

    with create_connection((str(client_ip), client_id.tcp_port)) as sock:
        sock.send(Package.create(me).bytes())

        ssl_ctx = context()

        with ssl_ctx.wrap_socket(sock, server_side=True) as ssock:
            transport, protocol = await loop.create_connection(
                lambda: KdeconnectWorkerProtocol(
                    loop, on_con_lost, client=client_id, processor=processor
                ),
                sock=ssock,
            )

            try:
                await on_con_lost
            finally:
                transport.close()


asyncio.run(main())
