"""Ed25519 signing/verification delegated to the system OpenSSL CLI.

No cryptographic code is implemented here. All key handling and signature
math is done by openssl(1):

  sign   : openssl pkeyutl -sign   -inkey PRIV -rawin -in MSG -out SIG
  verify : openssl pkeyutl -verify -pubin -inkey PUB -rawin -in MSG -sigfile SIG

Per the OpenSSL 3.6 pkeyutl documentation, Ed25519 (a one-shot algorithm)
requires -rawin and takes the message via -in; messages and signatures are
exchanged through temporary files, not stdin. The private key is read by
openssl directly from the caller-supplied path and never copied, printed, or
embedded in any output.

Key-type enforcement: pkeyutl selects the algorithm from the supplied key, so
a non-Ed25519 key would silently sign/verify under its own algorithm. Before
any pkeyutl call, the key's SubjectPublicKeyInfo is exported as DER by
openssl and compared against the fixed Ed25519 SPKI shape (OID 1.3.101.112,
32-byte key, 44 bytes total). This is a documented constant comparison, not
hand-written cryptography. Non-Ed25519 keys raise UnsupportedKeyError.
"""
import os
import subprocess
import tempfile

ED25519_OID = '1.3.101.112'
# DER of a fixed-shape Ed25519 SubjectPublicKeyInfo:
# SEQUENCE(44) { SEQUENCE(5) { OID 1.3.101.112 }, BIT STRING(32-byte key) }
ED25519_SPKI_PREFIX = bytes.fromhex('302a300506032b6570032100')
ED25519_SPKI_LENGTH = 44


class CryptoError(RuntimeError):
    pass


class UnsupportedKeyError(CryptoError):
    """The supplied key is not an Ed25519 key."""


def _openssl(args):
    try:
        return subprocess.run(args, capture_output=True)
    except FileNotFoundError as exc:
        raise CryptoError('openssl executable not found on PATH') from exc


def _spki_der(key_path, pubin):
    """Export the key's SubjectPublicKeyInfo as DER via openssl pkey."""
    with tempfile.TemporaryDirectory() as tmp:
        der_path = os.path.join(tmp, 'spki.der')
        args = ['openssl', 'pkey']
        if pubin:
            args.append('-pubin')
        args += ['-in', str(key_path), '-pubout', '-outform', 'DER',
                 '-out', der_path]
        result = _openssl(args)
        if result.returncode != 0:
            detail = result.stderr.decode('utf-8', 'replace').strip()
            raise CryptoError('openssl pkey failed: %s' % detail)
        with open(der_path, 'rb') as handle:
            return handle.read()


def _assert_ed25519(key_path, pubin, label):
    der = _spki_der(key_path, pubin)
    if (len(der) != ED25519_SPKI_LENGTH
            or not der.startswith(ED25519_SPKI_PREFIX)):
        raise UnsupportedKeyError(
            '%s is not an Ed25519 key (SPKI OID %s expected)' % (label, ED25519_OID))


def sign_ed25519(private_key_path, message):
    """Sign message bytes with Ed25519; returns the raw signature bytes."""
    _assert_ed25519(private_key_path, pubin=False, label='private key')
    with tempfile.TemporaryDirectory() as tmp:
        msg_path = os.path.join(tmp, 'message.bin')
        sig_path = os.path.join(tmp, 'signature.bin')
        with open(msg_path, 'wb') as handle:
            handle.write(message)
        result = _openssl(['openssl', 'pkeyutl', '-sign',
                           '-inkey', str(private_key_path),
                           '-rawin', '-in', msg_path, '-out', sig_path])
        if result.returncode != 0:
            detail = result.stderr.decode('utf-8', 'replace').strip()
            raise CryptoError('openssl pkeyutl -sign failed: %s' % detail)
        with open(sig_path, 'rb') as handle:
            return handle.read()


def verify_ed25519(public_key_path, message, signature):
    """Return (verified, detail). A bad signature returns (False, detail),
    not an exception; a non-Ed25519 key raises UnsupportedKeyError and
    tool-level failures raise CryptoError."""
    _assert_ed25519(public_key_path, pubin=True, label='public key')
    with tempfile.TemporaryDirectory() as tmp:
        msg_path = os.path.join(tmp, 'message.bin')
        sig_path = os.path.join(tmp, 'signature.bin')
        with open(msg_path, 'wb') as handle:
            handle.write(message)
        with open(sig_path, 'wb') as handle:
            handle.write(signature)
        result = _openssl(['openssl', 'pkeyutl', '-verify', '-pubin',
                           '-inkey', str(public_key_path),
                           '-rawin', '-in', msg_path, '-sigfile', sig_path])
        detail = result.stderr.decode('utf-8', 'replace').strip()
        return result.returncode == 0, detail or ('exit %d' % result.returncode)
