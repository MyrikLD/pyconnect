import ssl

from cert import load_keys


def context(
    cert_filename="cert.pem",
    key_filename="key.pem",
):
    load_keys(cert_filename, key_filename)

    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.options |= ssl.OP_NO_TLSv1
    ssl_ctx.options |= ssl.OP_NO_TLSv1_1
    ssl_ctx.load_cert_chain(cert_filename, keyfile=key_filename)
    # ssl_ctx.load_verify_locations(cafile="client_ca.pem")
    ssl_ctx.verify_mode = ssl.CERT_OPTIONAL
    ssl_ctx.check_hostname = False
    ciphers = [
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-SHA",
    ]
    ssl_ctx.set_ciphers(":".join(ciphers))

    return ssl_ctx
