"""Provide tools for encryption/decryption with AES."""
#TODO: implement rigorous testing, why not try out fuzzing??
# or any testing at all, for that matter.

from Crypto.Cipher import AES
import hashlib
import hmac
import os

def compare(hash1, hash2):
    """Compare hashes. Helps prevent timing attacks."""

    hashlib.compare_digest(hash1, hash2)

def generate_key(password, salt, iterations = 500000):
    """Derive key using PBKDF2 with sha_512. Password and salt are bytes.
    We want a 32 byte key for use with AES.
    piece of shit hashlib does not support sha3 for pbkdf2 currently.
    """

    return hashlib.pbkdf2_hmac('sha512', password, salt, iterations, 32)

def generate_salt(size = 32):
    """Generates a salt of size bytes. type bytes."""

    return os.urandom(32)

def generate_mac(mac_key, cipher):
    """Generates an HMAC for cipher text using sha512."""

    return hmac.digest(mac_key, cipher, 'sha512')

def generate_initialization_vector():
    """Generate and return a 16 byte I.V."""

    #You should not use the same I.V. to encrypt two different plain_text strings
    return os.urandom(16)

def encrypt_text(plain_text, secret_key, initialization_vector):
    """Encrypt the plaintext string, return the cipher text."""

    plain_text = pad(plain_text)
    cipher = AES.new(secret_key, AES.MODE_CBC, initialization_vector)
    return cipher.encrypt(plain_text)

def decrypt_text(cipher_text, secret_key, initialization_vector):
    """Decrypt the cipher text and return plaintext."""

    cipher = AES.new(secret_key, AES.MODE_CBC, initialization_vector)
    return unpad(cipher.decrypt(cipher_text))

def verify_mac(mac_key, cipher_text, mac):
    """Check whether the calculated mac and stored mac are identical."""

    calculated_mac = generate_mac(mac_key, cipher_text)
    return hmac.compare_digest(calculated_mac, mac)
    
def pad(unpadded): #SHOULD be keeping track of the size before adding padding
    """Pad the string to have size a multiple of 16 bytes."""

    string_sz = len(unpadded)
    m = string_sz % 16
    ps = ''
    ps = (chr(16-m) * (16 - m)).encode('utf-8')
    return unpadded + ps

def unpad(padded):
    """Remove the padding bytes."""

    sz = len(padded)
    to_remove = padded[sz-1]
    return padded[:sz-to_remove]
