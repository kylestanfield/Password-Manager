"""Provide functions for encryption/decryption with AES."""

from Crypto.Cipher import AES

def encrypt_text(plain_text, secret_key, initialization_vector):
    """Encrypt the plaintext string."""
    plain_text = pad(plain_text)
    cipher = AES.new(secret_key, AES_MODE.CBC, initialization_vector)
    return cipher.encrypt(plain_text)

def encrypt_then_MAC(plain_text, secret_key, initialization_vector):
    """Encrypt the plaintext with key and I.V. and then add a MAC."""
    #The I.V. must be 16 bytes.
    cipher_text = encrypt_text(plain_text, secret_key, initialization_vector)
    #TODO implement a MAC
    
def generate_initialization_vector():
    """Generate and return a 16 byte I.V."""
    #You should not use the same I.V. to encrypt two different plain_text strings
    return os.urandom(16)

def pad(unpadded):
    """Pad the string to have size a multiple of 16 bytes."""
    string_sz = len(unpadded.encode('utf-8'))
    if string_sz % 16 != 0:
        unpadded += ' ' * (16 - (string_sz % 16))
    return unpadded
