"""Test model/evidence.py."""

import base64
import filecmp
from pathlib import Path

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)
from cryptography.x509 import load_pem_x509_certificate, load_pem_x509_crl

from mse_cli.core.no_sgx_docker import NoSgxDockerConfig
from mse_cli.home.model.evidence import ApplicationEvidence


def test_load():
    """Test `load` function."""
    json_path = Path(__file__).parent / "data/evidence.json"
    conf = ApplicationEvidence.load(path=json_path)

    ref_conf = ApplicationEvidence(
        input_args=NoSgxDockerConfig(
            host="localhost",
            expiration_date=1714058115,
            size=4096,
            app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
            application="app:app",
        ),
        ratls_certificate=load_pem_x509_certificate(
            b"-----BEGIN CERTIFICATE-----\nMIIUfDCCFCKgAwIBAgITdFsNOA0J4klfaNLxtAArloOHwjAKBggqhkjOPQQDAjBg\nMQswCQYDVQQGEwJGUjEWMBQGA1UECAwNSWxlLWRlLUZyYW5jZTEOMAwGA1UEBwwF\nUGFyaXMxFTATBgNVBAoMDENvc21pYW4gVGVjaDESMBAGA1UEAwwJbG9jYWxob3N0\nMB4XDTIzMDUxNzA5Mzg0MloXDTI0MDQyNjA5MzgzM1owYDELMAkGA1UEBhMCRlIx\nFjAUBgNVBAgMDUlsZS1kZS1GcmFuY2UxDjAMBgNVBAcMBVBhcmlzMRUwEwYDVQQK\nDAxDb3NtaWFuIFRlY2gxEjAQBgNVBAMMCWxvY2FsaG9zdDBZMBMGByqGSM49AgEG\nCCqGSM49AwEHA0IABJRCBMEF70mXMUT58XTvOlLo9mAr6vAYQvf+gmIAf/v1uFl8\nd+7DKP7aV9jA6jI4rJ1jO1vrMX0dT8AbMft7tA6jghK5MIIStTAUBgNVHREEDTAL\ngglsb2NhbGhvc3QwghKNBgkqhkiG+E2KOQYEghJ+AwACAAAAAAAJAA4Ak5pyM/ec\nTKmUCg2zlX8GB0Juveh/qjdCKYvIfG98s4gAAAAABQsICf//AAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAAAAADnAAAAAAAAAA5O\nxV5pCwaldK9Z39UbqjhmrEyNN4lu/8Dx+tF7Mc87AAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAADBwWHQ3ZluiphH3mfqLAAiZ2H3cVosQi0wEqwQeVoe9QAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA\nCgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAACNiDYO0OsUm0CiILKp6y8tfeVZUvuLR1nt80Okno34HAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAyhAAAFNDR7kK/DSY+LawSiTH\n7g029V/QQd1tyuMMuo4iX/WOY910502mAbR/WLkmaOAbUFcKo8yD0JREKg6i79Vz\nQv/2ypv/LrT1QmTui7xCGxFpf7ZU+21A28v1PXWJg72lLICVyEkVbQyebjH1+Mzh\n2XOzTex+vsroa7e38lzyMSD0BQsICf//AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAFQAAAAAAAADnAAAAAAAAABkqpQzhwM7wPM+J57Wx\naw15ePXCse3Pd02HcC6BVNi/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAACMT1d115ZQPpYTf3fGioKaAFasje1wFAsIGwlEkMV7/wAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEACQAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAUH84PQ7tWUp7et8b37nnxyiQ6noHprp7pWJGn/Y+CBAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAHqKiZMgyhNPxbit5R5fDHqGrSOsaMsbal3fR++xS\nSHBQFgEqse/cmdEgsrVK238LzK4zdldTvKAd2hejemtiUiAAAAECAwQFBgcICQoL\nDA0ODxAREhMUFRYXGBkaGxwdHh8FAGIOAAAtLS0tLUJFR0lOIENFUlRJRklDQVRF\nLS0tLS0KTUlJRThqQ0NCSmlnQXdJQkFnSVVjeTc1bDVBb0FRdjBkOU1TNTNmaGdo\nUGFEV0F3Q2dZSUtvWkl6ajBFQXdJdwpjREVpTUNBR0ExVUVBd3daU1c1MFpXd2dV\nMGRZSUZCRFN5QlFiR0YwWm05eWJTQkRRVEVhTUJnR0ExVUVDZ3dSClNXNTBaV3dn\nUTI5eWNHOXlZWFJwYjI0eEZEQVNCZ05WQkFjTUMxTmhiblJoSUVOc1lYSmhNUXN3\nQ1FZRFZRUUkKREFKRFFURUxNQWtHQTFVRUJoTUNWVk13SGhjTk1qTXdNVEU1TURr\neU5qUXlXaGNOTXpBd01URTVNRGt5TmpReQpXakJ3TVNJd0lBWURWUVFEREJsSmJu\nUmxiQ0JUUjFnZ1VFTkxJRU5sY25ScFptbGpZWFJsTVJvd0dBWURWUVFLCkRCRkpi\nblJsYkNCRGIzSndiM0poZEdsdmJqRVVNQklHQTFVRUJ3d0xVMkZ1ZEdFZ1EyeGhj\nbUV4Q3pBSkJnTlYKQkFnTUFrTkJNUXN3Q1FZRFZRUUdFd0pWVXpCWk1CTUdCeXFH\nU000OUFnRUdDQ3FHU000OUF3RUhBMElBQkhWYQp1T1J1LytaOXBRZDZORnNKQkRr\nbGVSWUFCR1JnRWZ2Z2t2a0k5V3hSTjF6c1g4K0locHhkOThlc3NYK09VRmJ0CmJM\nd3RxZUlnbE43bUxFMXl0b3VqZ2dNT01JSURDakFmQmdOVkhTTUVHREFXZ0JTVmIx\nM052UnZoNlVCSnlkVDAKTTg0QlZ3dmVWREJyQmdOVkhSOEVaREJpTUdDZ1hxQmNo\nbHBvZEhSd2N6b3ZMMkZ3YVM1MGNuVnpkR1ZrYzJWeQpkbWxqWlhNdWFXNTBaV3d1\nWTI5dEwzTm5lQzlqWlhKMGFXWnBZMkYwYVc5dUwzWTBMM0JqYTJOeWJEOWpZVDF3\nCmJHRjBabTl5YlNabGJtTnZaR2x1Wnoxa1pYSXdIUVlEVlIwT0JCWUVGSlZTcmc0\nTnJBazhzNGpXRWFnMVdFU2MKcUNaTU1BNEdBMVVkRHdFQi93UUVBd0lHd0RBTUJn\nTlZIUk1CQWY4RUFqQUFNSUlDT3dZSktvWklodmhOQVEwQgpCSUlDTERDQ0FpZ3dI\nZ1lLS29aSWh2aE5BUTBCQVFRUTBqZ0V3V3RpalpGWmd4MHZOOEJ6WnpDQ0FXVUdD\naXFHClNJYjRUUUVOQVFJd2dnRlZNQkFHQ3lxR1NJYjRUUUVOQVFJQkFnRUVNQkFH\nQ3lxR1NJYjRUUUVOQVFJQ0FnRUUKTUJBR0N5cUdTSWI0VFFFTkFRSURBZ0VETUJB\nR0N5cUdTSWI0VFFFTkFRSUVBZ0VETUJFR0N5cUdTSWI0VFFFTgpBUUlGQWdJQS96\nQVJCZ3NxaGtpRytFMEJEUUVDQmdJQ0FQOHdFQVlMS29aSWh2aE5BUTBCQWdjQ0FR\nQXdFQVlMCktvWklodmhOQVEwQkFnZ0NBUUF3RUFZTEtvWklodmhOQVEwQkFna0NB\nUUF3RUFZTEtvWklodmhOQVEwQkFnb0MKQVFBd0VBWUxLb1pJaHZoTkFRMEJBZ3ND\nQVFBd0VBWUxLb1pJaHZoTkFRMEJBZ3dDQVFBd0VBWUxLb1pJaHZoTgpBUTBCQWcw\nQ0FRQXdFQVlMS29aSWh2aE5BUTBCQWc0Q0FRQXdFQVlMS29aSWh2aE5BUTBCQWc4\nQ0FRQXdFQVlMCktvWklodmhOQVEwQkFoQUNBUUF3RUFZTEtvWklodmhOQVEwQkFo\nRUNBUXN3SHdZTEtvWklodmhOQVEwQkFoSUUKRUFRRUF3UC8vd0FBQUFBQUFBQUFB\nQUF3RUFZS0tvWklodmhOQVEwQkF3UUNBQUF3RkFZS0tvWklodmhOQVEwQgpCQVFH\nTUdCcUFBQUFNQThHQ2lxR1NJYjRUUUVOQVFVS0FRRXdIZ1lLS29aSWh2aE5BUTBC\nQmdRUVRuOCtHMHdYClNzSTJtR25SQVkyQmNUQkVCZ29xaGtpRytFMEJEUUVITURZ\nd0VBWUxLb1pJaHZoTkFRMEJCd0VCQWY4d0VBWUwKS29aSWh2aE5BUTBCQndJQkFR\nQXdFQVlMS29aSWh2aE5BUTBCQndNQkFmOHdDZ1lJS29aSXpqMEVBd0lEU0FBdwpS\nUUloQVArK0VkclFmRmxEM0F2OVU3VmhlT3BCNlNvaDNZSDFPd2ZUVEdCMXloa1BB\naUFEQ1J1K3pWbjhNdTNGCnljMm9nSDNUTnp3Zjh6ZEhkbHNlUE55SUQrRkhEdz09\nCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0KLS0tLS1CRUdJTiBDRVJUSUZJQ0FU\nRS0tLS0tCk1JSUNsakNDQWoyZ0F3SUJBZ0lWQUpWdlhjMjlHK0hwUUVuSjFQUXp6\nZ0ZYQzk1VU1Bb0dDQ3FHU000OUJBTUMKTUdneEdqQVlCZ05WQkFNTUVVbHVkR1Zz\nSUZOSFdDQlNiMjkwSUVOQk1Sb3dHQVlEVlFRS0RCRkpiblJsYkNCRApiM0p3YjNK\naGRHbHZiakVVTUJJR0ExVUVCd3dMVTJGdWRHRWdRMnhoY21FeEN6QUpCZ05WQkFn\nTUFrTkJNUXN3CkNRWURWUVFHRXdKVlV6QWVGdzB4T0RBMU1qRXhNRFV3TVRCYUZ3\nMHpNekExTWpFeE1EVXdNVEJhTUhBeElqQWcKQmdOVkJBTU1HVWx1ZEdWc0lGTkhX\nQ0JRUTBzZ1VHeGhkR1p2Y20wZ1EwRXhHakFZQmdOVkJBb01FVWx1ZEdWcwpJRU52\nY25CdmNtRjBhVzl1TVJRd0VnWURWUVFIREF0VFlXNTBZU0JEYkdGeVlURUxNQWtH\nQTFVRUNBd0NRMEV4CkN6QUpCZ05WQkFZVEFsVlRNRmt3RXdZSEtvWkl6ajBDQVFZ\nSUtvWkl6ajBEQVFjRFFnQUVOU0IvN3QyMWxYU08KMkN1enB4dzc0ZUpCNzJFeURH\nZ1c1clhDdHgydFZUTHE2aEtrNnorVWlSWkNucVI3cHNPdmdxRmVTeGxtVGxKbApl\nVG1pMldZejNxT0J1ekNCdURBZkJnTlZIU01FR0RBV2dCUWlaUXpXV3AwMGlmT0R0\nSlZTdjFBYk9TY0dyREJTCkJnTlZIUjhFU3pCSk1FZWdSYUJEaGtGb2RIUndjem92\nTDJObGNuUnBabWxqWVhSbGN5NTBjblZ6ZEdWa2MyVnkKZG1salpYTXVhVzUwWld3\ndVkyOXRMMGx1ZEdWc1UwZFlVbTl2ZEVOQkxtUmxjakFkQmdOVkhRNEVGZ1FVbFc5\nZAp6YjBiNGVsQVNjblU5RFBPQVZjTDNsUXdEZ1lEVlIwUEFRSC9CQVFEQWdFR01C\nSUdBMVVkRXdFQi93UUlNQVlCCkFmOENBUUF3Q2dZSUtvWkl6ajBFQXdJRFJ3QXdS\nQUlnWHNWa2kwdytpNlZZR1czVUYvMjJ1YVhlMFlKRGoxVWUKbkErVGpEMWFpNWND\nSUNZYjFTQW1ENXhrZlRWcHZvNFVveWlTWXhyRFdMbVVSNENJOU5LeWZQTisKLS0t\nLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQotLS0tLUJFR0lOIENFUlRJRklDQVRFLS0t\nLS0KTUlJQ2p6Q0NBalNnQXdJQkFnSVVJbVVNMWxxZE5JbnpnN1NWVXI5UUd6a25C\ncXd3Q2dZSUtvWkl6ajBFQXdJdwphREVhTUJnR0ExVUVBd3dSU1c1MFpXd2dVMGRZ\nSUZKdmIzUWdRMEV4R2pBWUJnTlZCQW9NRVVsdWRHVnNJRU52CmNuQnZjbUYwYVc5\ndU1SUXdFZ1lEVlFRSERBdFRZVzUwWVNCRGJHRnlZVEVMTUFrR0ExVUVDQXdDUTBF\neEN6QUoKQmdOVkJBWVRBbFZUTUI0WERURTRNRFV5TVRFd05EVXhNRm9YRFRRNU1U\nSXpNVEl6TlRrMU9Wb3dhREVhTUJnRwpBMVVFQXd3UlNXNTBaV3dnVTBkWUlGSnZi\nM1FnUTBFeEdqQVlCZ05WQkFvTUVVbHVkR1ZzSUVOdmNuQnZjbUYwCmFXOXVNUlF3\nRWdZRFZRUUhEQXRUWVc1MFlTQkRiR0Z5WVRFTE1Ba0dBMVVFQ0F3Q1EwRXhDekFK\nQmdOVkJBWVQKQWxWVE1Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERBUWNEUWdB\nRUM2bkV3TURJWVpPai9pUFdzQ3phRUtpNwoxT2lPU0xSRmhXR2pibkJWSmZWbmtZ\nNHUzSWprRFlZTDBNeE80bXFzeVlqbEJhbFRWWXhGUDJzSkJLNXpsS09CCnV6Q0J1\nREFmQmdOVkhTTUVHREFXZ0JRaVpReldXcDAwaWZPRHRKVlN2MUFiT1NjR3JEQlNC\nZ05WSFI4RVN6QkoKTUVlZ1JhQkRoa0ZvZEhSd2N6b3ZMMk5sY25ScFptbGpZWFJs\nY3k1MGNuVnpkR1ZrYzJWeWRtbGpaWE11YVc1MApaV3d1WTI5dEwwbHVkR1ZzVTBk\nWVVtOXZkRU5CTG1SbGNqQWRCZ05WSFE0RUZnUVVJbVVNMWxxZE5JbnpnN1NWClVy\nOVFHemtuQnF3d0RnWURWUjBQQVFIL0JBUURBZ0VHTUJJR0ExVWRFd0VCL3dRSU1B\nWUJBZjhDQVFFd0NnWUkKS29aSXpqMEVBd0lEU1FBd1JnSWhBT1cvNVFrUitTOUNp\nU0RjTm9vd0x1UFJMc1dHZi9ZaTdHU1g5NEJnd1R3ZwpBaUVBNEowbHJIb01zK1hv\nNW8vc1g2TzlRV3hIUkF2WlVHT2RSUTdjdnFSWGFxST0KLS0tLS1FTkQgQ0VSVElG\nSUNBVEUtLS0tLQoAMAwGA1UdEwEB/wQCMAAwCgYIKoZIzj0EAwIDSAAwRQIhAI1O\nnFt7sEjvhtWi+G5Ewr1bhLD9mvvHRy24MUwbs08eAiAokkeGBBfREzIs5bU7+PtB\npLMzjW4ikTqPVuAq0bhKzA==\n-----END CERTIFICATE-----\n"
        ),
        root_ca_crl=load_pem_x509_crl(
            b"-----BEGIN X509 CRL-----\nMIIBITCByAIBATAKBggqhkjOPQQDAjBoMRowGAYDVQQDDBFJbnRlbCBTR1ggUm9v\ndCBDQTEaMBgGA1UECgwRSW50ZWwgQ29ycG9yYXRpb24xFDASBgNVBAcMC1NhbnRh\nIENsYXJhMQswCQYDVQQIDAJDQTELMAkGA1UEBhMCVVMXDTIzMDQwMzEwMjI1MVoX\nDTI0MDQwMjEwMjI1MVqgLzAtMAoGA1UdFAQDAgEBMB8GA1UdIwQYMBaAFCJlDNZa\nnTSJ84O0lVK/UBs5JwasMAoGCCqGSM49BAMCA0gAMEUCIFFXfUfZ+6FXtl8etfRl\ne7xeVsyvc1oD8blj1wSAWrEYAiEAk5AV7BY25+r6X0JsHkAmR8ZzEytoUMq9aM72\nutdoKgM=\n-----END X509 CRL-----\n"
        ),
        pck_platform_crl=load_pem_x509_crl(
            b"-----BEGIN X509 CRL-----\nMIIKYjCCCggCAQEwCgYIKoZIzj0EAwIwcDEiMCAGA1UEAwwZSW50ZWwgU0dYIFBD\nSyBQbGF0Zm9ybSBDQTEaMBgGA1UECgwRSW50ZWwgQ29ycG9yYXRpb24xFDASBgNV\nBAcMC1NhbnRhIENsYXJhMQswCQYDVQQIDAJDQTELMAkGA1UEBhMCVVMXDTIzMDUx\nNjIzNTU0MVoXDTIzMDYxNTIzNTU0MVowggk0MDMCFG/DTlAj5yiSNDXWGqS4PGGB\nZq01Fw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEwNAIVAO+ubpcV/KE7h+Mz\n6CYe1tmQqSatFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEwNAIVAP1ghkhi\nnLpzB4tNSS9LPqdBrQjNFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEwNAIV\nAIr5JBhOHVr93XPD1joS9ei1c35WFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMK\nAQEwNAIVALEleXjPqczdB1mr+MXKcvrjp4qbFw0yMzA1MTYyMzU1NDFaMAwwCgYD\nVR0VBAMKAQEwMwIUdP6mFKlyvg4oQ/IFmDWBHthy+bMXDTIzMDUxNjIzNTU0MVow\nDDAKBgNVHRUEAwoBATA0AhUA+cTvVrOrSNV34Qi67fS/iAFCFLkXDTIzMDUxNjIz\nNTU0MVowDDAKBgNVHRUEAwoBATAzAhQHHeB3j55fxPKHjzDWsHyaMOazCxcNMjMw\nNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDQCFQDN4kJPlyzqlP8jmTf02AwlAp3W\nCxcNMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDMCFGwzGeUQm2RQfTzxEyzg\nA0nvUnMZFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEwNAIVAN8I11a2anSX\n9DtbtYraBNP096k3Fw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEwMwIUKK9I\nW2z2fkCaOdXLWu5FmPeo+nsXDTIzMDUxNjIzNTU0MVowDDAKBgNVHRUEAwoBATA0\nAhUA+4strsCSytqKqbxP8vHCDQNGZowXDTIzMDUxNjIzNTU0MVowDDAKBgNVHRUE\nAwoBATA0AhUAzUhQrFK9zGmmpvBYyLxXu9C1+GQXDTIzMDUxNjIzNTU0MVowDDAK\nBgNVHRUEAwoBATA0AhUAmU3TZm9SdfuAX5XdAr1QyyZ52K0XDTIzMDUxNjIzNTU0\nMVowDDAKBgNVHRUEAwoBATAzAhQHAhNpACUidNkDXu31RXRi+tDvTBcNMjMwNTE2\nMjM1NTQxWjAMMAoGA1UdFQQDCgEBMDMCFGHyv3Pjm04EqifYAb1z0kMZtb+AFw0y\nMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEwMwIUOZK+hRuWkC7/OJWebC7/GwZR\npLUXDTIzMDUxNjIzNTU0MVowDDAKBgNVHRUEAwoBATAzAhRjnxOaUED9z/GR6KT7\nG/CG7WA5cRcNMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDQCFQCVnVM/kknc\nHlE1RM3IML8Zt/HzARcNMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDMCFA/a\nQ6ALaOp5t8LerqwLSYvfsq+QFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEw\nNAIVAJ1ndTuB5HCQrqdj++xMRUm825kzFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0V\nBAMKAQEwMwIUNL+7eh2cVoFH4Ri2FPe3btPvaN8XDTIzMDUxNjIzNTU0MVowDDAK\nBgNVHRUEAwoBATA0AhUAhdPJOBt3p+BNEZyeWtZ0n/P/q4cXDTIzMDUxNjIzNTU0\nMVowDDAKBgNVHRUEAwoBATA0AhUAk4h8pEEeepI70f7SgZspSfIBtbQXDTIzMDUx\nNjIzNTU0MVowDDAKBgNVHRUEAwoBATAzAhQkmNxig5MJlv2L8jo3rL4mo77UVxcN\nMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDQCFQCKZvGnSUiGZ2icw5A6xUxm\nK3EucxcNMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDQCFQCvwTYQvdNst5hd\nEGSBqIDToB/aBxcNMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDQCFQDv4Ess\nM9A2qslspnO/HppHtk1cuxcNMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDQC\nFQCD2ayNi7UJ0cbICa1xLoQwVZ7X8xcNMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQD\nCgEBMDMCFHkx/VC1Bxwbv8W3tt7YtFudi4UpFw0yMzA1MTYyMzU1NDFaMAwwCgYD\nVR0VBAMKAQEwMwIUH6IOKXC95dV/e43fgzlITh8dCCMXDTIzMDUxNjIzNTU0MVow\nDDAKBgNVHRUEAwoBATAzAhQeh7LDsy2NI+QRzvNBl7la8Mit9RcNMjMwNTE2MjM1\nNTQxWjAMMAoGA1UdFQQDCgEBMDQCFQCa/S7pCkc1UKFn2ZaRFDfHUC0fCRcNMjMw\nNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDMCFESBsPEXKKE7aW0+qcdwoLFexY3a\nFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEwNAIVAKeFn1eYLvDmfTe8jvLv\nWsg1/xqpFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMKAQEwMwIUeuN3SKn5EvTG\nO6erB8WTzh0dEYEXDTIzMDUxNjIzNTU0MVowDDAKBgNVHRUEAwoBATAzAhQTiEsz\nJpk4wZWqFw/KddoXdTjfCxcNMjMwNTE2MjM1NTQxWjAMMAoGA1UdFQQDCgEBMDMC\nFCw8xv6SedsVFtXOOfKomM2loXXhFw0yMzA1MTYyMzU1NDFaMAwwCgYDVR0VBAMK\nAQEwMwIUcXlIaHUJI0vpeeS33ObzG+9ktowXDTIzMDUxNjIzNTU0MVowDDAKBgNV\nHRUEAwoBATA0AhUAnXbvLDnBNuhli25zlrHXRFonYx8XDTIzMDUxNjIzNTU0MVow\nDDAKBgNVHRUEAwoBATA0AhUAw+Al/KmV829ZtIRnk54+NOY2Gm8XDTIzMDUxNjIz\nNTU0MVowDDAKBgNVHRUEAwoBATA0AhUAjF9rMlfaBbF0KeLmG6ll1nMwYGoXDTIz\nMDUxNjIzNTU0MVowDDAKBgNVHRUEAwoBATA0AhUAoXxRci7B4MMnj+i98FIFnL7E\n5kgXDTIzMDUxNjIzNTU0MVowDDAKBgNVHRUEAwoBAaAvMC0wCgYDVR0UBAMCAQEw\nHwYDVR0jBBgwFoAUlW9dzb0b4elAScnU9DPOAVcL3lQwCgYIKoZIzj0EAwIDSAAw\nRQIgDVriOusQw5Z75VNbKtK/CF26SZhsR7XYjOWZfBardbUCIQCST8LtavMRfBZT\nll0lzk4y1TQ9DtdJdB0IYrdG00OxLQ==\n-----END X509 CRL-----\n"
        ),
        tcb_info=base64.b64decode(
            "N2IyMjc0NjM2MjQ5NmU2NjZmMjIzYTdiMjI2OTY0MjIzYTIyNTM0NzU4MjIyYzIyNzY2NTcyNzM2OTZmNmUyMjNhMzMyYzIyNjk3MzczNzU2NTQ0NjE3NDY1MjIzYTIyMzIzMDMyMzMyZDMwMzUyZDMzMzA1NDMwMzAzYTM0MzUzYTMwMzA1YTIyMmMyMjZlNjU3ODc0NTU3MDY0NjE3NDY1MjIzYTIyMzIzMDMyMzMyZDMwMzYyZDMyMzk1NDMwMzAzYTM0MzUzYTMwMzA1YTIyMmMyMjY2NmQ3MzcwNjMyMjNhMjIzMzMwMzYzMDM2NDEzMDMwMzAzMDMwMzAyMjJjMjI3MDYzNjU0OTY0MjIzYTIyMzAzMDMwMzAyMjJjMjI3NDYzNjI1NDc5NzA2NTIyM2EzMDJjMjI3NDYzNjI0NTc2NjE2Yzc1NjE3NDY5NmY2ZTQ0NjE3NDYxNGU3NTZkNjI2NTcyMjIzYTMxMzUyYzIyNzQ2MzYyNGM2NTc2NjU2YzczMjIzYTViN2IyMjc0NjM2MjIyM2E3YjIyNzM2Nzc4NzQ2MzYyNjM2ZjZkNzA2ZjZlNjU2ZTc0NzMyMjNhNWI3YjIyNzM3NjZlMjIzYTMxMzEyYzIyNjM2MTc0NjU2NzZmNzI3OTIyM2EyMjQyNDk0ZjUzMjIyYzIyNzQ3OTcwNjUyMjNhMjI0NTYxNzI2Yzc5MjA0ZDY5NjM3MjZmNjM2ZjY0NjUyMDU1NzA2NDYxNzQ2NTIyN2QyYzdiMjI3Mzc2NmUyMjNhMzEzMTJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNGY1MzJmNTY0ZDRkMjIyYzIyNzQ3OTcwNjUyMjNhMjI1MzQ3NTgyMDRjNjE3NDY1MjA0ZDY5NjM3MjZmNjM2ZjY0NjUyMDU1NzA2NDYxNzQ2NTIyN2QyYzdiMjI3Mzc2NmUyMjNhMzMyYzIyNjM2MTc0NjU2NzZmNzI3OTIyM2EyMjRmNTMyZjU2NGQ0ZDIyMmMyMjc0Nzk3MDY1MjIzYTIyNTQ1ODU0MjA1MzQ5NGU0OTU0MjI3ZDJjN2IyMjczNzY2ZTIyM2EzMzJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNDI0OTRmNTMyMjdkMmM3YjIyNzM3NjZlMjIzYTMyMzUzNTdkMmM3YjIyNzM3NjZlMjIzYTMyMzUzNTdkMmM3YjIyNzM3NjZlMjIzYTMxN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2Q1ZDJjMjI3MDYzNjU3Mzc2NmUyMjNhMzEzMzdkMmMyMjc0NjM2MjQ0NjE3NDY1MjIzYTIyMzIzMDMyMzMyZDMwMzIyZDMxMzU1NDMwMzAzYTMwMzAzYTMwMzA1YTIyMmMyMjc0NjM2MjUzNzQ2MTc0NzU3MzIyM2EyMjUzNTc0ODYxNzI2NDY1NmU2OTZlNjc0ZTY1NjU2NDY1NjQyMjJjMjI2MTY0NzY2OTczNmY3Mjc5NDk0NDczMjIzYTViMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzYzMTM1MjI1ZDdkMmM3YjIyNzQ2MzYyMjIzYTdiMjI3MzY3Nzg3NDYzNjI2MzZmNmQ3MDZmNmU2NTZlNzQ3MzIyM2E1YjdiMjI3Mzc2NmUyMjNhMzEzMTJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNDI0OTRmNTMyMjJjMjI3NDc5NzA2NTIyM2EyMjQ1NjE3MjZjNzkyMDRkNjk2MzcyNmY2MzZmNjQ2NTIwNTU3MDY0NjE3NDY1MjI3ZDJjN2IyMjczNzY2ZTIyM2EzMTMxMmMyMjYzNjE3NDY1Njc2ZjcyNzkyMjNhMjI0ZjUzMmY1NjRkNGQyMjJjMjI3NDc5NzA2NTIyM2EyMjUzNDc1ODIwNGM2MTc0NjUyMDRkNjk2MzcyNmY2MzZmNjQ2NTIwNTU3MDY0NjE3NDY1MjI3ZDJjN2IyMjczNzY2ZTIyM2EzMzJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNGY1MzJmNTY0ZDRkMjIyYzIyNzQ3OTcwNjUyMjNhMjI1NDU4NTQyMDUzNDk0ZTQ5NTQyMjdkMmM3YjIyNzM3NjZlMjIzYTMzMmMyMjYzNjE3NDY1Njc2ZjcyNzkyMjNhMjI0MjQ5NGY1MzIyN2QyYzdiMjI3Mzc2NmUyMjNhMzIzNTM1N2QyYzdiMjI3Mzc2NmUyMjNhMzIzNTM1N2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDVkMmMyMjcwNjM2NTczNzY2ZTIyM2EzMTMzN2QyYzIyNzQ2MzYyNDQ2MTc0NjUyMjNhMjIzMjMwMzIzMzJkMzAzMjJkMzEzNTU0MzAzMDNhMzAzMDNhMzAzMDVhMjIyYzIyNzQ2MzYyNTM3NDYxNzQ3NTczMjIzYTIyNDM2ZjZlNjY2OTY3NzU3MjYxNzQ2OTZmNmU0MTZlNjQ1MzU3NDg2MTcyNjQ2NTZlNjk2ZTY3NGU2NTY1NjQ2NTY0MjIyYzIyNjE2NDc2Njk3MzZmNzI3OTQ5NDQ3MzIyM2E1YjIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM2MzEzNTIyNWQ3ZDJjN2IyMjc0NjM2MjIyM2E3YjIyNzM2Nzc4NzQ2MzYyNjM2ZjZkNzA2ZjZlNjU2ZTc0NzMyMjNhNWI3YjIyNzM3NjZlMjIzYTM3MmMyMjYzNjE3NDY1Njc2ZjcyNzkyMjNhMjI0MjQ5NGY1MzIyMmMyMjc0Nzk3MDY1MjIzYTIyNDU2MTcyNmM3OTIwNGQ2OTYzNzI2ZjYzNmY2NDY1MjA1NTcwNjQ2MTc0NjUyMjdkMmM3YjIyNzM3NjZlMjIzYTM5MmMyMjYzNjE3NDY1Njc2ZjcyNzkyMjNhMjI0ZjUzMmY1NjRkNGQyMjJjMjI3NDc5NzA2NTIyM2EyMjUzNDc1ODIwNGM2MTc0NjUyMDRkNjk2MzcyNmY2MzZmNjQ2NTIwNTU3MDY0NjE3NDY1MjI3ZDJjN2IyMjczNzY2ZTIyM2EzMzJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNGY1MzJmNTY0ZDRkMjIyYzIyNzQ3OTcwNjUyMjNhMjI1NDU4NTQyMDUzNDk0ZTQ5NTQyMjdkMmM3YjIyNzM3NjZlMjIzYTMzMmMyMjYzNjE3NDY1Njc2ZjcyNzkyMjNhMjI0MjQ5NGY1MzIyN2QyYzdiMjI3Mzc2NmUyMjNhMzIzNTM1N2QyYzdiMjI3Mzc2NmUyMjNhMzIzNTM1N2QyYzdiMjI3Mzc2NmUyMjNhMzE3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDVkMmMyMjcwNjM2NTczNzY2ZTIyM2EzMTMzN2QyYzIyNzQ2MzYyNDQ2MTc0NjUyMjNhMjIzMjMwMzIzMjJkMzAzODJkMzEzMDU0MzAzMDNhMzAzMDNhMzAzMDVhMjIyYzIyNzQ2MzYyNTM3NDYxNzQ3NTczMjIzYTIyNGY3NTc0NGY2NjQ0NjE3NDY1MjIyYzIyNjE2NDc2Njk3MzZmNzI3OTQ5NDQ3MzIyM2E1YjIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM2MzUzNzIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNzMzMzAyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzczMzM4MjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM3MzYzNzIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNjMxMzUyMjVkN2QyYzdiMjI3NDYzNjIyMjNhN2IyMjczNjc3ODc0NjM2MjYzNmY2ZDcwNmY2ZTY1NmU3NDczMjIzYTViN2IyMjczNzY2ZTIyM2EzNzJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNDI0OTRmNTMyMjJjMjI3NDc5NzA2NTIyM2EyMjQ1NjE3MjZjNzkyMDRkNjk2MzcyNmY2MzZmNjQ2NTIwNTU3MDY0NjE3NDY1MjI3ZDJjN2IyMjczNzY2ZTIyM2EzOTJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNGY1MzJmNTY0ZDRkMjIyYzIyNzQ3OTcwNjUyMjNhMjI1MzQ3NTgyMDRjNjE3NDY1MjA0ZDY5NjM3MjZmNjM2ZjY0NjUyMDU1NzA2NDYxNzQ2NTIyN2QyYzdiMjI3Mzc2NmUyMjNhMzMyYzIyNjM2MTc0NjU2NzZmNzI3OTIyM2EyMjRmNTMyZjU2NGQ0ZDIyMmMyMjc0Nzk3MDY1MjIzYTIyNTQ1ODU0MjA1MzQ5NGU0OTU0MjI3ZDJjN2IyMjczNzY2ZTIyM2EzMzJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNDI0OTRmNTMyMjdkMmM3YjIyNzM3NjZlMjIzYTMyMzUzNTdkMmM3YjIyNzM3NjZlMjIzYTMyMzUzNTdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2Q1ZDJjMjI3MDYzNjU3Mzc2NmUyMjNhMzEzMzdkMmMyMjc0NjM2MjQ0NjE3NDY1MjIzYTIyMzIzMDMyMzIyZDMwMzgyZDMxMzA1NDMwMzAzYTMwMzAzYTMwMzA1YTIyMmMyMjc0NjM2MjUzNzQ2MTc0NzU3MzIyM2EyMjRmNzU3NDRmNjY0NDYxNzQ2NTQzNmY2ZTY2Njk2Nzc1NzI2MTc0Njk2ZjZlNGU2NTY1NjQ2NTY0MjIyYzIyNjE2NDc2Njk3MzZmNzI3OTQ5NDQ3MzIyM2E1YjIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM2MzUzNzIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNzMzMzAyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzczMzM4MjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM3MzYzNzIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNjMxMzUyMjVkN2QyYzdiMjI3NDYzNjIyMjNhN2IyMjczNjc3ODc0NjM2MjYzNmY2ZDcwNmY2ZTY1NmU3NDczMjIzYTViN2IyMjczNzY2ZTIyM2EzNDJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNDI0OTRmNTMyMjJjMjI3NDc5NzA2NTIyM2EyMjQ1NjE3MjZjNzkyMDRkNjk2MzcyNmY2MzZmNjQ2NTIwNTU3MDY0NjE3NDY1MjI3ZDJjN2IyMjczNzY2ZTIyM2EzNDJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNGY1MzJmNTY0ZDRkMjIyYzIyNzQ3OTcwNjUyMjNhMjI1MzQ3NTgyMDRjNjE3NDY1MjA0ZDY5NjM3MjZmNjM2ZjY0NjUyMDU1NzA2NDYxNzQ2NTIyN2QyYzdiMjI3Mzc2NmUyMjNhMzMyYzIyNjM2MTc0NjU2NzZmNzI3OTIyM2EyMjRmNTMyZjU2NGQ0ZDIyMmMyMjc0Nzk3MDY1MjIzYTIyNTQ1ODU0MjA1MzQ5NGU0OTU0MjI3ZDJjN2IyMjczNzY2ZTIyM2EzMzJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNDI0OTRmNTMyMjdkMmM3YjIyNzM3NjZlMjIzYTMyMzUzNTdkMmM3YjIyNzM3NjZlMjIzYTMyMzUzNTdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2Q1ZDJjMjI3MDYzNjU3Mzc2NmUyMjNhMzEzMTdkMmMyMjc0NjM2MjQ0NjE3NDY1MjIzYTIyMzIzMDMyMzEyZDMxMzEyZDMxMzA1NDMwMzAzYTMwMzAzYTMwMzA1YTIyMmMyMjc0NjM2MjUzNzQ2MTc0NzU3MzIyM2EyMjRmNzU3NDRmNjY0NDYxNzQ2NTIyMmMyMjYxNjQ3NjY5NzM2ZjcyNzk0OTQ0NzMyMjNhNWIyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNTM4MzYyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzYzMTM0MjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM2MzEzNTIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNjM1MzcyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzczMzMwMjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM3MzMzODIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNzM2MzcyMjVkN2QyYzdiMjI3NDYzNjIyMjNhN2IyMjczNjc3ODc0NjM2MjYzNmY2ZDcwNmY2ZTY1NmU3NDczMjIzYTViN2IyMjczNzY2ZTIyM2EzNDJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNDI0OTRmNTMyMjJjMjI3NDc5NzA2NTIyM2EyMjQ1NjE3MjZjNzkyMDRkNjk2MzcyNmY2MzZmNjQ2NTIwNTU3MDY0NjE3NDY1MjI3ZDJjN2IyMjczNzY2ZTIyM2EzNDJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNGY1MzJmNTY0ZDRkMjIyYzIyNzQ3OTcwNjUyMjNhMjI1MzQ3NTgyMDRjNjE3NDY1MjA0ZDY5NjM3MjZmNjM2ZjY0NjUyMDU1NzA2NDYxNzQ2NTIyN2QyYzdiMjI3Mzc2NmUyMjNhMzMyYzIyNjM2MTc0NjU2NzZmNzI3OTIyM2EyMjRmNTMyZjU2NGQ0ZDIyMmMyMjc0Nzk3MDY1MjIzYTIyNTQ1ODU0MjA1MzQ5NGU0OTU0MjI3ZDJjN2IyMjczNzY2ZTIyM2EzMzJjMjI2MzYxNzQ2NTY3NmY3Mjc5MjIzYTIyNDI0OTRmNTMyMjdkMmM3YjIyNzM3NjZlMjIzYTMyMzUzNTdkMmM3YjIyNzM3NjZlMjIzYTMyMzUzNTdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2Q1ZDJjMjI3MDYzNjU3Mzc2NmUyMjNhMzEzMDdkMmMyMjc0NjM2MjQ0NjE3NDY1MjIzYTIyMzIzMDMyMzAyZDMxMzEyZDMxMzE1NDMwMzAzYTMwMzAzYTMwMzA1YTIyMmMyMjc0NjM2MjUzNzQ2MTc0NzU3MzIyM2EyMjRmNzU3NDRmNjY0NDYxNzQ2NTIyMmMyMjYxNjQ3NjY5NzM2ZjcyNzk0OTQ0NzMyMjNhNWIyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNDM3MzcyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzUzODM2MjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM2MzEzNDIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNjMxMzUyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzYzNTM3MjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM3MzMzMDIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNzMzMzgyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzczNjM3MjI1ZDdkMmM3YjIyNzQ2MzYyMjIzYTdiMjI3MzY3Nzg3NDYzNjI2MzZmNmQ3MDZmNmU2NTZlNzQ3MzIyM2E1YjdiMjI3Mzc2NmUyMjNhMzQyYzIyNjM2MTc0NjU2NzZmNzI3OTIyM2EyMjQyNDk0ZjUzMjIyYzIyNzQ3OTcwNjUyMjNhMjI0NTYxNzI2Yzc5MjA0ZDY5NjM3MjZmNjM2ZjY0NjUyMDU1NzA2NDYxNzQ2NTIyN2QyYzdiMjI3Mzc2NmUyMjNhMzQyYzIyNjM2MTc0NjU2NzZmNzI3OTIyM2EyMjRmNTMyZjU2NGQ0ZDIyMmMyMjc0Nzk3MDY1MjIzYTIyNTM0NzU4MjA0YzYxNzQ2NTIwNGQ2OTYzNzI2ZjYzNmY2NDY1MjA1NTcwNjQ2MTc0NjUyMjdkMmM3YjIyNzM3NjZlMjIzYTMzMmMyMjYzNjE3NDY1Njc2ZjcyNzkyMjNhMjI0ZjUzMmY1NjRkNGQyMjJjMjI3NDc5NzA2NTIyM2EyMjU0NTg1NDIwNTM0OTRlNDk1NDIyN2QyYzdiMjI3Mzc2NmUyMjNhMzMyYzIyNjM2MTc0NjU2NzZmNzI3OTIyM2EyMjQyNDk0ZjUzMjI3ZDJjN2IyMjczNzY2ZTIyM2EzMjM1MzU3ZDJjN2IyMjczNzY2ZTIyM2EzMjM1MzU3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkMmM3YjIyNzM3NjZlMjIzYTMwN2QyYzdiMjI3Mzc2NmUyMjNhMzA3ZDJjN2IyMjczNzY2ZTIyM2EzMDdkNWQyYzIyNzA2MzY1NzM3NjZlMjIzYTM1N2QyYzIyNzQ2MzYyNDQ2MTc0NjUyMjNhMjIzMjMwMzEzODJkMzAzMTJkMzAzNDU0MzAzMDNhMzAzMDNhMzAzMDVhMjIyYzIyNzQ2MzYyNTM3NDYxNzQ3NTczMjIzYTIyNGY3NTc0NGY2NjQ0NjE3NDY1MjIyYzIyNjE2NDc2Njk3MzZmNzI3OTQ5NDQ3MzIyM2E1YjIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDMxMzAzNjIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzMTMxMzUyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzEzMzM1MjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDMyMzAzMzIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzMjMyMzAyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzIzMzMzMjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDMyMzczMDIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzMjM5MzMyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzMzMjMwMjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDMzMzIzOTIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzMzM4MzEyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzMzODM5MjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM0MzczNzIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNTM4MzYyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzYzMTM0MjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM2MzEzNTIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNjM1MzcyMjJjMjI0OTRlNTQ0NTRjMmQ1MzQxMmQzMDMwMzczMzMwMjIyYzIyNDk0ZTU0NDU0YzJkNTM0MTJkMzAzMDM3MzMzODIyMmMyMjQ5NGU1NDQ1NGMyZDUzNDEyZDMwMzAzNzM2MzcyMjVkN2Q1ZDdkMmMyMjczNjk2NzZlNjE3NDc1NzI2NTIyM2EyMjM4NjU2MTYzMzkzMjMyMzUzNzM1MzEzNTY1MzU2MjM2MzAzNzM3MzM2MjY0NjIzNTMwNjE2NTMxNjI2NTM4MzI2NDYyMzUzOTMyMzI2MzYzNjQzMDM1NjQzNTYxMzkzOTM0NjEzODY0Mzc2MTYyNjUzNDM2MzEzODYxNjIzOTY1MzUzMjM3NjQ2MTM1NjEzNjYxNjY2NjMxNjUzMjMyNjQzOTMyMzEzMzM4MzQzMzM3NjIzMDMwNjMzNDMyMzU2NTYzMzMzODM5MzUzMTM1MzYzMjM0MzgzODM2MzQ2NDYxNjYzNTM1MzMzMDY2NjUzNDM2MzAzMDMwMzAzMDMwNjIyMjdkCg==".encode(
                "utf-8"
            )
        ),
        qe_identity=base64.b64decode(
            "eyJlbmNsYXZlSWRlbnRpdHkiOnsiaWQiOiJRRSIsInZlcnNpb24iOjIsImlzc3VlRGF0ZSI6IjIwMjMtMDYtMjBUMDA6MjQ6MDJaIiwibmV4dFVwZGF0ZSI6IjIwMjMtMDctMjBUMDA6MjQ6MDJaIiwidGNiRXZhbHVhdGlvbkRhdGFOdW1iZXIiOjE1LCJtaXNjc2VsZWN0IjoiMDAwMDAwMDAiLCJtaXNjc2VsZWN0TWFzayI6IkZGRkZGRkZGIiwiYXR0cmlidXRlcyI6IjExMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwIiwiYXR0cmlidXRlc01hc2siOiJGQkZGRkZGRkZGRkZGRkZGMDAwMDAwMDAwMDAwMDAwMCIsIm1yc2lnbmVyIjoiOEM0RjU3NzVENzk2NTAzRTk2MTM3Rjc3QzY4QTgyOUEwMDU2QUM4REVENzAxNDBCMDgxQjA5NDQ5MEM1N0JGRiIsImlzdnByb2RpZCI6MSwidGNiTGV2ZWxzIjpbeyJ0Y2IiOnsiaXN2c3ZuIjo4fSwidGNiRGF0ZSI6IjIwMjMtMDItMTVUMDA6MDA6MDBaIiwidGNiU3RhdHVzIjoiVXBUb0RhdGUifSx7InRjYiI6eyJpc3Zzdm4iOjZ9LCJ0Y2JEYXRlIjoiMjAyMS0xMS0xMFQwMDowMDowMFoiLCJ0Y2JTdGF0dXMiOiJPdXRPZkRhdGUiLCJhZHZpc29yeUlEcyI6WyJJTlRFTC1TQS0wMDYxNSJdfSx7InRjYiI6eyJpc3Zzdm4iOjV9LCJ0Y2JEYXRlIjoiMjAyMC0xMS0xMVQwMDowMDowMFoiLCJ0Y2JTdGF0dXMiOiJPdXRPZkRhdGUiLCJhZHZpc29yeUlEcyI6WyJJTlRFTC1TQS0wMDQ3NyIsIklOVEVMLVNBLTAwNjE1Il19LHsidGNiIjp7ImlzdnN2biI6NH0sInRjYkRhdGUiOiIyMDE5LTExLTEzVDAwOjAwOjAwWiIsInRjYlN0YXR1cyI6Ik91dE9mRGF0ZSIsImFkdmlzb3J5SURzIjpbIklOVEVMLVNBLTAwMzM0IiwiSU5URUwtU0EtMDA0NzciLCJJTlRFTC1TQS0wMDYxNSJdfSx7InRjYiI6eyJpc3Zzdm4iOjJ9LCJ0Y2JEYXRlIjoiMjAxOS0wNS0xNVQwMDowMDowMFoiLCJ0Y2JTdGF0dXMiOiJPdXRPZkRhdGUiLCJhZHZpc29yeUlEcyI6WyJJTlRFTC1TQS0wMDIxOSIsIklOVEVMLVNBLTAwMjkzIiwiSU5URUwtU0EtMDAzMzQiLCJJTlRFTC1TQS0wMDQ3NyIsIklOVEVMLVNBLTAwNjE1Il19LHsidGNiIjp7ImlzdnN2biI6MX0sInRjYkRhdGUiOiIyMDE4LTA4LTE1VDAwOjAwOjAwWiIsInRjYlN0YXR1cyI6Ik91dE9mRGF0ZSIsImFkdmlzb3J5SURzIjpbIklOVEVMLVNBLTAwMjAyIiwiSU5URUwtU0EtMDAyMTkiLCJJTlRFTC1TQS0wMDI5MyIsIklOVEVMLVNBLTAwMzM0IiwiSU5URUwtU0EtMDA0NzciLCJJTlRFTC1TQS0wMDYxNSJdfV19LCJzaWduYXR1cmUiOiI2NDMwZTgzNjNhNTNlNzc2MGM4MzllMDg2YmI3ZTliZjliZmFkNzQ0MmYzMjBkMDRjMDI0MDY2NTViYjQxNzc0ZWUwMjc4YWViY2Y0Mjk2YjUzZTQ2NDQ3OTc2NTZlYjNjNzVhYTRmNzE2YTAzODkyZmRjMGE3MzY3MTY5YmU2OCJ9".encode(
                "utf-8"
            )
        ),
        tcb_cert=load_pem_x509_certificate(
            b"-----BEGIN CERTIFICATE-----\nMIICizCCAjKgAwIBAgIUfjiC1ftVKUpASY5FhAPpFJG99FUwCgYIKoZIzj0EAwIw\naDEaMBgGA1UEAwwRSW50ZWwgU0dYIFJvb3QgQ0ExGjAYBgNVBAoMEUludGVsIENv\ncnBvcmF0aW9uMRQwEgYDVQQHDAtTYW50YSBDbGFyYTELMAkGA1UECAwCQ0ExCzAJ\nBgNVBAYTAlVTMB4XDTE4MDUyMTEwNTAxMFoXDTI1MDUyMTEwNTAxMFowbDEeMBwG\nA1UEAwwVSW50ZWwgU0dYIFRDQiBTaWduaW5nMRowGAYDVQQKDBFJbnRlbCBDb3Jw\nb3JhdGlvbjEUMBIGA1UEBwwLU2FudGEgQ2xhcmExCzAJBgNVBAgMAkNBMQswCQYD\nVQQGEwJVUzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABENFG8xzydWRfK92bmGv\nP+mAh91PEyV7Jh6FGJd5ndE9aBH7R3E4A7ubrlh/zN3C4xvpoouGlirMba+W2lju\nypajgbUwgbIwHwYDVR0jBBgwFoAUImUM1lqdNInzg7SVUr9QGzknBqwwUgYDVR0f\nBEswSTBHoEWgQ4ZBaHR0cHM6Ly9jZXJ0aWZpY2F0ZXMudHJ1c3RlZHNlcnZpY2Vz\nLmludGVsLmNvbS9JbnRlbFNHWFJvb3RDQS5kZXIwHQYDVR0OBBYEFH44gtX7VSlK\nQEmORYQD6RSRvfRVMA4GA1UdDwEB/wQEAwIGwDAMBgNVHRMBAf8EAjAAMAoGCCqG\nSM49BAMCA0cAMEQCIB9C8wOAN/ImxDtGACV246KcqjagZOR0kyctyBrsGGJVAiAj\nftbrNGsGU8YH211dRiYNoPPu19Zp/ze8JmhujB0oBw==\n-----END CERTIFICATE-----\n"
        ),
        signer_pk=load_pem_public_key(
            b"-----BEGIN PUBLIC KEY-----\nMIIBoDANBgkqhkiG9w0BAQEFAAOCAY0AMIIBiAKCAYEAwJ1w0FTxi683hkxrg9fG\nSZ6AvDbfvsh52dPgrgRIB9jkIW1eJacXyuNZHznOKl+T/QaHorfNg+e6IB9Jaa80\nyeqp7lewtF7nG4CB83qSeU/GbehuYQeuTlIPvIZrrMl9DviiADOu7cCvRTVLcyj8\n1pKuWpWuUC0LVE8o6JsG8Zk89Qj653oJl+926koOAaQZ203w2fKhbXTEoyaaysbe\n2jzabuPWIFafxPiSO6p+UcXs+CzJfaZkVKBWAhHBZN5DYr+JhYqOJlb3bvsAxGuS\n4mWgxx1OGRXTJq1uHQvZOuOprUICqiYoc6UJAT5MiMOofwng498KXLl0Yg4qAYI3\nDCdYEiFC5URJzvlQzQzHV6q4mTep2YXtIUcCsiomFM3ldZVEXGtpST+qqQUKIEiC\n3nqLhX5YogqFbOm/xhE/RCgVWb7J4aSW9/+ohwwsRM7eRFTFylBv2BLcP5gl/f9P\nuMX6e9Bd/TxRj5tkk7BLfex6gdfVRWnJ1Odhht1AyyYXAgED\n-----END PUBLIC KEY-----\n"
        ),
    )

    assert conf.input_args == ref_conf.input_args
    assert conf.ratls_certificate == ref_conf.ratls_certificate
    assert conf.root_ca_crl == ref_conf.root_ca_crl
    assert conf.pck_platform_crl == ref_conf.pck_platform_crl
    assert conf.signer_pk.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    ) == ref_conf.signer_pk.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    )
    assert conf.tcb_info == ref_conf.tcb_info
    assert conf.qe_identity == ref_conf.qe_identity
    assert conf.tcb_cert == ref_conf.tcb_cert


def test_save(workspace: Path):
    """Test the `save` method."""
    json = Path(__file__).parent / "data/evidence.json"
    conf = ApplicationEvidence.load(path=json)

    tmp_json = workspace / "evidence.json"
    conf.save(tmp_json)

    assert filecmp.cmp(json, tmp_json)
