import os
import uuid
from datetime import datetime, timedelta
from typing import Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends.interfaces import RSABackend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import OID_COMMON_NAME


def create_key():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=RSABackend(),
    )
    return key


def generate_selfsigned_cert(key=None):
    """Generates self signed certificate for a hostname, and optional IP addresses."""

    hostname = "_".join(str(i) for i in uuid.uuid1().fields)

    # Generate our key
    if key is None:
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )

    name = x509.Name([x509.NameAttribute(OID_COMMON_NAME, hostname)])

    # best practice seem to be to include the hostname in the SAN, which *SHOULD* mean COMMON_NAME is ignored.
    alt_names = [x509.DNSName(hostname)]

    san = x509.SubjectAlternativeName(alt_names)

    # path_len=0 means this cert can only sign itself, not other certs.
    basic_contraints = x509.BasicConstraints(ca=True, path_length=0)
    now = datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(1000)
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=10 * 365))
        .add_extension(basic_contraints, False)
        .add_extension(san, False)
        .sign(key, hashes.SHA256(), default_backend())
    )
    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return cert_pem, key_pem


def load_keys(cert_filename="cert.pem", key_filename="key.pem") -> Tuple[bytes, bytes]:
    if os.path.isfile(cert_filename) and os.path.isfile(key_filename):
        with open(cert_filename, "rb") as f:
            cert_pem = f.read()
        with open(key_filename, "rb") as f:
            key_pem = f.read()

    else:
        cert_pem, key_pem = generate_selfsigned_cert()

        with open(cert_filename, "wb") as f:
            f.write(cert_pem)
        with open(key_filename, "wb") as f:
            f.write(key_pem)

    return cert_pem, key_pem


def cert_name(cert_pem: bytes) -> str:
    cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
    names = [i.value for i in cert.subject.get_attributes_for_oid(OID_COMMON_NAME)]
    return names[0]
