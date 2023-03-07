## What is MicroService Encryption?

MicroService Encryption (MSE) allows to easily deploy confidential web application written in Python in Cosmian’s infrastructure with the following security features:

- Code runs in a Trusted Execution Environment (TEE) and is encrypted with your own key.
- Secure channel is established directly and uniquely with your code in the TEE.
- Everyone interacting with your microservice can verify that your code runs in a TEE thanks to a Transport Layer Security (TLS) extension called Remote Attestation TLS (RA-TLS).

## What does MSE protect?

Basically MSE protects any data and metadata against us and the underlying cloud provider who owns the hardware infrastructure.

Then, privilege users or anyone with physical access to the host machine in Cosmian’s infrastructure:

- Can’t alter the integrity of data and code in the protected area of the TEE.
- Can't access the unique TLS server key of your microservice generated inside the TEE or decrypt the TLS session.
- Can't access the secret key used to encrypt your code or obtain the code in plaintext.
- Can’t access the persistant storage of your microservice which is tied to the TEE.

These assumptions remain valid as long as the TEE, namely Intel SGX, and its software stack known as the Trusted Computing Base (TCB) are not subject to severe vulnerabilities.

See [Security Model](https://docs.cosmian.com/microservice_encryption/security/) for more details or just discover MSE with [Getting Started](https://docs.cosmian.com/microservice_encryption/getting_started/).