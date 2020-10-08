import os
import ssl

from cert import generate_selfsigned_cert
from package.types import Identity


def create_pem():
    my_id = Identity.me()
    cert_pem, key_pem = generate_selfsigned_cert(my_id.device_id)
    with open("cert.pem", "wb") as f:
        f.write(cert_pem)
    with open("key.pem", "wb") as f:
        f.write(key_pem)


def context():
    if not os.path.isfile("cert.pem") or not os.path.isfile("cert.pem"):
        create_pem()

    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.options |= ssl.OP_NO_TLSv1
    ssl_ctx.options |= ssl.OP_NO_TLSv1_1
    # ssl_ctx.load_cert_chain("_certificate.pem", keyfile="_privateKey.pem")
    ssl_ctx.load_cert_chain("cert.pem", keyfile="key.pem")
    # ssl_ctx.load_verify_locations(cafile="client_ca.pem")
    ssl_ctx.check_hostname = False
    ssl_ctx.set_ciphers(
        "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA"
    )

    return ssl_ctx
