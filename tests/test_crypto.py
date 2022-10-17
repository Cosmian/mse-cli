from mse_ctl.utils.crypto import *

from keys import *


def test_encrypt():
    message: bytes = b"Hello World!"

    assert (len(CP_SYMKEY) == len(DP1_SYMKEY) == len(DP2_SYMKEY) ==
            len(RC_SYMKEY) == 32)

    ciphertext: bytes = encrypt(message, CP_SYMKEY)
    cleartext: bytes = decrypt(ciphertext, CP_SYMKEY)
    assert message == cleartext


def test_seal():
    message: bytes = b"Hello World!"

    assert (len(CP_X25519_PUBKEY) == len(DP1_X25519_PUBKEY) ==
            len(DP2_X25519_PUBKEY) == len(RC_X25519_PUBKEY) == 32)
    assert (len(CP_X25519_PRIVKEY) == len(DP1_X25519_PRIVKEY) ==
            len(DP2_X25519_PRIVKEY) == len(RC_X25519_PRIVKEY) == 32)

    ciphertext: bytes = seal(message, CP_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, CP_X25519_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, DP1_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, DP1_X25519_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, DP2_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, DP2_X25519_PRIVKEY)
    assert message == cleartext

    ciphertext: bytes = seal(message, RC_X25519_PUBKEY)
    cleartext: bytes = unseal(ciphertext, RC_X25519_PRIVKEY)
    assert message == cleartext


def test_sign():
    assert (len(CP_ED25519_PUBKEY) == len(DP1_ED25519_PUBKEY) ==
            len(DP2_ED25519_PUBKEY) == len(RC_ED25519_PUBKEY) == 32)
    assert (len(CP_ED25519_PRIVKEY) == len(DP1_ED25519_PRIVKEY) ==
            len(DP2_ED25519_PRIVKEY) == len(RC_ED25519_PRIVKEY) == 32)
    assert (len(CP_ED25519_SEED) == len(DP1_ED25519_SEED) ==
            len(DP2_ED25519_SEED) == len(RC_ED25519_SEED) == 32)

    test_keys: List[Tuple[bytes, bytes, bytes]] = [
        (CP_SYMKEY, CP_ED25519_SEED, CP_ED25519_PUBKEY),
        (DP1_SYMKEY, DP1_ED25519_SEED, DP1_ED25519_PUBKEY),
        (DP2_SYMKEY, DP2_ED25519_SEED, DP2_ED25519_PUBKEY),
        (RC_SYMKEY, RC_ED25519_SEED, RC_ED25519_PUBKEY)
    ]

    for (msg, sk, pk) in test_keys:
        sig: bytes = sign(msg, sk)
        assert verify(msg, sig, pk) == msg


def test_sig_and_seal():
    enclave_ed25519_pk, enclave_ed25519_seed, enclave_ed25519_sk = ed25519_keygen(
    )
    enclave_x25519_pk, enclave_x25519_sk = ed25519_to_x25519_keypair(
        enclave_ed25519_pk, enclave_ed25519_seed)

    seal_box: bytes = seal(DP1_SYMKEY, enclave_x25519_pk)
    assert len(seal_box) == 80

    sig: bytes = sign(seal_box, DP1_ED25519_SEED)
    assert len(sig) == 64

    sealed_symkey: bytes = sig + seal_box
    assert len(sealed_symkey) == 144

    assert verify(sealed_symkey[64:], sealed_symkey[:64],
                  DP1_ED25519_PUBKEY) == sealed_symkey[64:]

    unsealed_symkey: bytes = unseal(sealed_symkey[64:], enclave_x25519_sk)

    assert len(unsealed_symkey) == 32


def test_dalek_sig():
    test_sigs: List[Tuple[bytes, bytes, bytes]] = [
        (CP_SYMKEY,
         bytes.fromhex(
             "9396352cad80c5be7bf7f897dc677770a29f9c9f734efc6e131d73f012e79cc3"
             "11666810104773d590cbb1aa3a8889bb3bc0d79f5de9525772287da66871f906"
         ), CP_ED25519_PUBKEY),
        (DP1_SYMKEY,
         bytes.fromhex(
             "d700eeff0b13ef1d61f9447625d556ae966ac259cb684deb13cb51d427b656ec"
             "00ae9b57efb0a3a922b316d6356be8ca1876b3f6f982b04172d3dea88ed51e0a"
         ), DP1_ED25519_PUBKEY),
        (DP2_SYMKEY,
         bytes.fromhex(
             "33146fb37293a4a30ca209a8ed051e153d1f528e9d40e106567fdd8a16ec7511"
             "d29e4b0c6e790146643a36fca83c63cc59a274f806be4b5718c1adfebc6a4d0c"
         ), DP2_ED25519_PUBKEY),
        (RC_SYMKEY,
         bytes.fromhex(
             "371357b506a5b19e1f616a0c45fd7cbd029d735b07adf95fb913d3db651b65dc"
             "d6ccceed4e3bd6bc6d23f80f22e17020ac7586b7eeebcd007c8131179aa86f03"
         ), RC_ED25519_PUBKEY)
    ]

    for (msg, sig, pubkey) in test_sigs:
        assert verify(msg, sig, pubkey) == msg
