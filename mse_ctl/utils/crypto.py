"""mse_ctl.utils.crypto module."""

import hashlib
from pathlib import Path
import shutil
from typing import Tuple, List
from unicodedata import normalize

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import nacl.public
import nacl.secret
import nacl.signing
import nacl.utils
from nacl.public import PrivateKey, PublicKey, SealedBox
from nacl.secret import SecretBox
from nacl.signing import SigningKey, VerifyKey
from nacl.bindings.crypto_scalarmult import (
    crypto_scalarmult, crypto_scalarmult_ed25519_base,
    crypto_scalarmult_ed25519_SCALARBYTES)
from nacl.bindings import (crypto_sign_keypair, crypto_sign_seed_keypair,
                           crypto_sign_ed25519_sk_to_curve25519,
                           crypto_sign_ed25519_pk_to_curve25519,
                           crypto_sign_SEEDBYTES)

ENC_EXT: str = ".enc"


def pubkey_fingerprint(public_key: bytes) -> bytes:
    """Compute custom public key fingerprint.

    Parameters
    ----------
    public_key: bytes
        Bytes of the public key.

    Returns
    -------
    bytes
        Least significant 8 bytes of SHA3-256(public_key).

    """
    return hashlib.sha3_256(public_key).digest()[-8:]


def x25519_keypair() -> Tuple[bytes, bytes]:
    """Keygen for X25519 (DH using Curve25519 in Montgomery form).

    Returns
    -------
    Tuple[bytes, bytes]
        Keypair (public_key, private_key).

    """
    private_key: PrivateKey = PrivateKey.generate()
    public_key: PublicKey = private_key.public_key

    return bytes(public_key), bytes(private_key)


def x25519_pubkey_from_privkey(private_key: bytes) -> bytes:
    """Recover public key from private key created for X25519.

    Parameters
    ----------
    private_key: bytes
        Bytes of the X25519 private key.

    Returns
    -------
    bytes
        Bytes of the X25519 public key corresponding to `private_key`.

    """
    return bytes(PrivateKey(private_key).public_key)


def ed25519_keygen() -> Tuple[bytes, bytes, bytes]:
    """Keygen for Ed25519 (signature system using the twisted Edwards curve).

    Returns
    -------
    Tuple[bytes, bytes, bytes]
        Triple (public_key, seed, private_key).

    """
    public_key, sk = crypto_sign_keypair()  # type: bytes, bytes
    seed: bytes = sk[:crypto_sign_SEEDBYTES]
    private_key: bytes = hashlib.sha512(
        seed).digest()[:crypto_scalarmult_ed25519_SCALARBYTES]

    return public_key, seed, private_key


def ed25519_seed_keygen(seed: bytes) -> Tuple[bytes, bytes, bytes]:
    """Seeded keygen for Ed25519 (signature system using the twisted Edwards curve).

    Returns
    -------
    Tuple[bytes, bytes, bytes]
        Triple (public_key, seed, private_key).

    """
    public_key, sk = crypto_sign_seed_keypair(seed)

    assert seed == sk[:crypto_sign_SEEDBYTES]

    private_key: bytearray = bytearray(
        hashlib.sha512(seed).digest()[:crypto_scalarmult_ed25519_SCALARBYTES])

    # see: src/libsodium/crypto_sign/ed25519/ref10/keypair.c#L19
    private_key[0] &= 248
    private_key[31] &= 127
    private_key[31] |= 64

    return public_key, seed, bytes(private_key)


def ed25519_pubkey_from_privkey(private_key: bytes) -> bytes:
    """Recover public key from private key created for Ed25519.

    Parameters
    ----------
    private_key: bytes
        Bytes of the Ed25519 private key.

    Returns
    -------
    bytes
        Bytes of the Ed25519 public key corresponding to `private_key`.

    """
    return crypto_scalarmult_ed25519_base(private_key)


def ed25519_to_x25519_keypair(public_key: bytes,
                              seed: bytes) -> Tuple[bytes, bytes]:
    """Map an edwards25519 keypair to a curve25519 keypair.

    Parameters
    ----------
    public_key: bytes
        Bytes of the Ed25519 public key.
    seed : bytes
        Bytes of the Ed25519 seed.

    Returns
    -------
    Tuple[bytes, bytes]
        Keypair for X25519

    """
    x25519_privkey: bytes = crypto_sign_ed25519_sk_to_curve25519(seed +
                                                                 public_key)
    x25519_pubkey: bytes = crypto_sign_ed25519_pk_to_curve25519(public_key)

    return x25519_pubkey, x25519_privkey


def ed25519_to_x25519_pubkey(public_key: bytes) -> bytes:
    """Map an edwards25519 public key to a curve25519 public key.

    Parameters
    ----------
    public_key: bytes
        Bytes of the Ed25519 public key.

    Returns
    -------
    bytes
        Public key for X25519.

    """
    return crypto_sign_ed25519_pk_to_curve25519(public_key)


def x25519(private_key: bytes, public_key: bytes) -> bytes:
    """Scalar multiplication over Curve25519.

    Parameters
    ----------
    private_key: bytes
        Scalar to be used as private key.
    public_key: bytes
        Bytes of the point on the Curve25519.

    Returns
    -------
    bytes
        Point on the Curve25519 to be used as shared secret.

    """
    return crypto_scalarmult(private_key, public_key)


def encrypt(data: bytes, key: bytes) -> bytes:
    """Encrypt bytes `data` using XSalsa20-Poly1305.

    Parameters
    ----------
    data : bytes
        Data to be encrypted.
    key : bytes
        Symmetric key used for encryption.

    Returns
    -------
    bytes
        Ciphertext of `data` using `key`.

    """
    box: SecretBox = SecretBox(key)

    return box.encrypt(data)


def encrypt_file(path: Path, key: bytes) -> Path:
    """Encrypt file `path` using XSalsa20-Poly1305.

    Parameters
    ----------
    path : Path
        Path to the data to be encrypted.
    key : bytes
        Symmetric key used for encryption.

    Returns
    -------
    Path
        Path to the encrypted file `path`.

    """
    if not path.is_file():
        raise FileNotFoundError

    out_path: Path = path.with_suffix(f"{path.suffix}{ENC_EXT}")
    out_path.write_bytes(encrypt(path.read_bytes(), key))

    return out_path


def encrypt_directory(dir_path: Path, patterns: List[str], key: bytes,
                      exceptions: List[str], dir_exceptions: List[str],
                      out_dir_path: Path) -> bool:
    """Encrypt the content of directory `dir_path` using XSalsa20-Poly1305.

    Parameters
    ----------
    dir_path : Path
        Path to the directory to be encrypted.
    patterns: List[str]
        List of patterns to be matched in the directory.
    exceptions: List[str]
        List of files which won't be encrypted.
    dir_exceptions: List[str]
        List of directories which won't be encrypted recursively.
    key : bytes
        Symmetric key used for encryption.
    out_dir_path: Path
        Output directory path.

    Returns
    -------
    bool
        True if success, raise an exception otherwise.

    """
    if not dir_path.is_dir():
        raise NotADirectoryError

    if out_dir_path.exists():
        shutil.rmtree(out_dir_path)

    shutil.copytree(dir_path, out_dir_path)

    for pattern in patterns:  # type: str
        for path in out_dir_path.rglob(pattern):  # type: Path
            if path.is_file() and path.name not in exceptions and all(
                    directory not in path.parts
                    for directory in dir_exceptions):
                encrypt_file(path, key)
                path.unlink()

    return True


def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypt bytes `encrypted_data` using XSalsa20-Poly1305.

    Parameters
    ----------
    encrypted_data : bytes
        Encrypted data to be decrypted.
    key : bytes
        Symmetric key used for encryption.

    Returns
    -------
    bytes
        Cleartext of `encrypted_data`.

    """
    box: SecretBox = SecretBox(key)

    return box.decrypt(encrypted_data)


def decrypt_file(path: Path, key: bytes) -> Path:
    """Decrypt file `path` using XSalsa20-Poly1305.

    Parameters
    ----------
    path : Path
        Path to the data to be decrypted.
    key : bytes
        Symmetric key used for decryption.

    Returns
    -------
    Path
        Path to the decrypted file `path`.

    """
    if not path.is_file():
        raise FileNotFoundError

    out_path: Path = path.with_suffix("")
    out_path.write_bytes(decrypt(path.read_bytes(), key))

    return out_path


def decrypt_directory(dir_path: Path, key: bytes) -> bool:
    """Decrypt the content of directory `dir_path` using XSalsa20-Poly1305.

    Parameters
    ----------
    dir_path : Path
        Path to the directory to be decrypted.
    key : bytes
        Symmetric key used for decryption.

    Returns
    -------
    bool
        True if success, raise an exception otherwise.

    Notes
    -----
    It looks for files with extension ENC_EXT.

    """
    if not dir_path.is_dir():
        raise NotADirectoryError

    for path in dir_path.rglob(f"*{ENC_EXT}"):  # type: Path
        if path.is_file():
            decrypt_file(path, key)
            path.unlink()

    return True


def seal(data: bytes, recipient_public_key: bytes) -> bytes:
    """Seal with seal box of libsodium (X25519 and XSalsa20-Poly1305).

    Parameters
    ----------
    data : bytes
        The data to be sealed.
    recipient_public_key : bytes
        Recipent X25519 public key (32 bytes).

    Returns
    -------
    bytes
        `data` sealed for `recipient_public_key`.


    Notes
    -----
    ephemeral_pk ‖ box(m,
                       recipient_pk,
                       ephemeral_sk,
                       nonce=blake2b(ephemeral_pk ‖ recipient_pk))

    """
    box = SealedBox(PublicKey(recipient_public_key))

    return box.encrypt(data)


def unseal(encrypted_data: bytes, private_key: bytes) -> bytes:
    """Unseal with seal box of libsodium (X25519 and XSalsa20-Poly1305).

    Parameters
    ----------
    encrypted_data : bytes
        The encrypted data to be unsealed:
        ephemeral_pk (32 bytes) || MAC (16 bytes) || box(data) (var).
    private_key : bytes
        X25519 private key (32 bytes).

    Returns
    -------
    bytes
        cleartext data if success.

    """
    box = SealedBox(PrivateKey(private_key))

    return box.decrypt(encrypted_data)


def sign(data: bytes, private_key: bytes) -> bytes:
    """Sign `data` with `private_key` using Ed25519.

    Parameters
    ----------
    data : bytes
        Data to be signed.
    private_key : bytes
        Private key used to sign data.

    Returns
    -------
    bytes
        64 bytes Ed25519 signature.

    """
    signing_key: SigningKey = SigningKey(private_key)

    return signing_key.sign(data).signature


def verify(data: bytes, sig: bytes, public_key: bytes) -> bytes:
    """Verify `sig` with `data` and `public_key` using Ed25519.

    Parameters
    ----------
    data : bytes
        Data which has been signed.
    sig : bytes
        64 bytes signature.
    public_key : bytes
        Public key used to verify the signature.

    Returns
    -------
    bytes
        Original bytes of the message if the verification succeeded.

    """
    verify_key: VerifyKey = VerifyKey(public_key)

    return verify_key.verify(data,
                             sig)  # raise nacl.exceptions.BadSignatureError


def random_symkey() -> bytes:
    """Generate a random symmetric key for XSalsa20-Poly1305.

    Returns
    -------
    bytes
        32 bytes random symmetric key.

    """
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)


def derive_psk(words: Tuple[str, str, str], salt: bytes = b"") -> bytes:
    """Derive the pre-shared secret from BIP39 mnemonic wordlist.

    Parameters
    ----------
    words: Tuple[str, str, str]
        Triple of 3 words from BIP39 mnemonic wordlist.
    salt: bytes
        Cryptographic salt used as additional input to the hash function.

    Returns
    -------
    bytes
        32 bytes pre-shared key.

    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=hashlib.sha256(salt).digest(),
        iterations=390000,
    )

    return kdf.derive(b"".join(
        [normalize("NFKD", word).encode("utf-8") for word in words]))
