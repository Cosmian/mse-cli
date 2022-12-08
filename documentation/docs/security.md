## Intel SGX and Gramine

Intel Software Guard eXtensions (SGX) offers hardware-based memory encryption that isolates specific application code and data in memory.
Intel SGX allows user-level code to allocate private regions of memory, called enclaves, which are designed to be protected from processes running at higher privilege levels.

Because working with Intel SGX requires low-level C programming with the Intel SDK, we use Gramine-SGX, a lightweight guest OS designed to run a single Linux application with minimal host requirements and no modification.
It is the foundation of Microservice Encryption which allows us to expose a Python confidential web microservices in the cloud.

## Code encryption

Before sending the Python code of your microservice, each file is encrypted with XSalsa20-Poly1305 using a random symmetric key.
The symmetric key is provisioned when you are confident that your code is running in the microservice by doing the remote attestation.


## Remote attestation

A very important aspect Intel SGX (and more generally Trusted Execution Environnments) is attestation.
This is a mechanism for a remote user to verify that the application runs on a real hardware in an up-to-date hardware and software with the expected initial state.
In other words, remote attestation provides the assurance to the user that the remotely executing SGX enclave is trusted and that the correct code is executed.

To process the remote attestation, an *SGX quote* is required as a proof of trustworthiness.
It's a structure which contains, among others, interesting fields for the end user:

- `MRENCLAVE`, SHA-256 hash digest of the memory footprint during the execution of the code
- `MRSIGNER`, SHA-256 hash digest of Cosmian's enclave signer public key
- Debug flag, which must not be set in production
- Intel's certification chain and signature to attest the quote

Verification of trustworthiness is done using [intel-sgx-ra](http://gitlab.cosmian.com/core/intel-sgx-ra).

The *SGX quote* is embedded in the TLS certificate used by the microservice in a protocol called RA-TLS.

## RA-TLS

To ease the transport of the quote without modifying TLS, the quote is directly embedded in an X509 extension of the TLS certificate.
In addition, a SHA-256 hash digest of the certificate public key is included in the `REPORTDATA` field of the quote to link the quote to the certificate (i.e. the certificate has been generated in the code corresponding to `MRENCLAVE`).

It allows to fetch the certificate before using the API provided by the microservice and check first that it runs in an up-to-date SGX enclave with the correct code (by checking `MRENCLAVE`).
Then you can add the certificate as CA in your HTTPS client to be sure that you will always interact with the same microservice you checked.
