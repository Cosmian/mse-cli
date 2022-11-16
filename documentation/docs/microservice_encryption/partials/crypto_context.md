
New `CryptoContext` generates a random asymmetric key pair and a random symmetric key. You can use your own key generated with OpenSSL as an example: 

=== "Python"

    ```python
    from pathlib import Path

    from cosmian_secure_computation_client import CryptoContext

    # To generate a new Ed25519 private key with OpenSSL:
    # $ openssl genpkey -algorithm ed25519 -out ed25519-priv.pem
    # To generate a random symmetric key:
    # $ openssl rand -out symkey.bin 32
    crypto_ctx = CryptoContext.from_path(
        computation_uuid="xxxxxxxxxxxxxxxxxxxxxx",  # replace this
        side=Side.CodeProvider,  # replace with your role: CodeProvider, DataProvider or ResultConsumer
        words="word1-word2-word3",  # replace with the words given by the Computation Owner
        private_key=Path("ed25519-priv.pem"),
        password=None,  # optional password of the PEM file
        symmetric_key=Path("symkey.bin")
    )
    ```