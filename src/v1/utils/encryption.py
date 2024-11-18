import base64
import hashlib
from typing import Any, cast

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives._asymmetric import AsymmetricPadding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed


class EncryptionMixin:
    def serialize_pem_private_key(
        self,
        base64_encoded_pem_key: str,
        *,
        password: bytes | None = None,
        backend: Any | None = None,
    ) -> RSAPrivateKey:
        key_pem = base64.b64decode(base64_encoded_pem_key)
        rsa_key = serialization.load_pem_private_key(
            key_pem, password=password, backend=backend or default_backend()
        )
        return cast(RSAPrivateKey, rsa_key)

    def get_sha256_hash(self, buffer: bytes) -> bytes:
        return hashlib.sha256(buffer).digest()

    def get_signature(
        self,
        private_key: RSAPrivateKey,
        hash_digest: bytes,
        *,
        padding_: AsymmetricPadding | None = None,
        algorithm: Prehashed | hashes.HashAlgorithm | None = None,
    ) -> bytes:
        return private_key.sign(
            hash_digest,
            padding_ or padding.PKCS1v15(),
            algorithm or hashes.SHA256(),
        )
