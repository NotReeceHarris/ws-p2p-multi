from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import json
import random
import string
import datetime

def generate_rsa_keypair():
    # Generate a new RSA key pair with 2048 bit key size
    key = RSA.generate(4096)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def rsa_encrypt(public_key, message):
    # Import the public key
    key = RSA.import_key(public_key)
    # Set up the cipher for encryption
    cipher = PKCS1_OAEP.new(key)
    
    # Encrypt the message
    # Note: RSA has a limit on the size of the data that can be encrypted at once
    # We'll assume 'message' is small enough or handle it in chunks if needed
    encrypted_msg = cipher.encrypt(message.encode())
    return encrypted_msg

def rsa_decrypt(private_key, encrypted_msg):
    # Import the private key
    key = RSA.import_key(private_key)
    # Set up the cipher for decryption
    cipher = PKCS1_OAEP.new(key)
    
    # Decrypt the message
    decrypted_msg = cipher.decrypt(encrypted_msg)
    return decrypted_msg.decode()

def encrypt(plain_text, key):
    # Key must be 16, 24, or 32 bytes long for AES-128, AES-192, or AES-256 respectively
    if len(key) not in (16, 24, 32):
        raise ValueError("Key length must be 16, 24, or 32 bytes")

    # Generate a random IV (Initialization Vector)
    iv = get_random_bytes(AES.block_size)

    # Pad the plain text to be a multiple of 16 bytes (AES block size)
    pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
    padded_text = pad(plain_text).encode()

    # Create AES cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Encrypt the padded plain text
    encrypted_text = cipher.encrypt(padded_text)

    # Combine IV and encrypted data, then encode to base64 for easier handling
    return base64.b64encode(iv + encrypted_text).decode('utf-8')

def decrypt(encrypted_text, key):
    # Decode from base64
    data = base64.b64decode(encrypted_text)

    # Extract IV from the beginning of the data
    iv = data[:AES.block_size]
    encrypted_text = data[AES.block_size:]

    # Create AES cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the data
    decrypted_padded_text = cipher.decrypt(encrypted_text)

    # Unpad the text
    unpad = lambda s: s[:-ord(s[len(s)-1:])]
    return unpad(decrypted_padded_text).decode('utf-8')

private_key, our_public_key = generate_rsa_keypair()
there_public_key = None
key = base64.b64decode("PwkkEJLCxpdnOG5mEhXcHMKW8g6UxJZ3DbkSF7naYFI=")
message_size = 1 * 1024 * 1024 # 1 MiB

print(f"Private key: {private_key}")
print(f"Public key: {our_public_key}")

def send_public_key():
    return our_public_key

def clear_there_public_key():
    global there_public_key
    there_public_key = None

def send(data):
    print(f"Sending: {data}")

    return rsa_encrypt(there_public_key, data)

    """ obj = {
        'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'message': data
    }

    obj_string = json.dumps(obj)

    message_len = len(obj_string)
    random_bytes = message_size - message_len
    padding_len = int(random_bytes/2)

    list = [
        ''.join(random.choices(string.ascii_letters + string.digits, k=padding_len)),
        obj,
        ''.join(random.choices(string.ascii_letters + string.digits, k=padding_len))
    ]

    return encrypt(json.dumps(list), key) """

def recv(data):
    print(f"Received: {data}")
    try:

        global there_public_key
        if there_public_key is None:
            if data.decode("utf-8").startswith('-----BEGIN PUBLIC KEY-----'):
                there_public_key = data
                return f"Public key received: {there_public_key.decode("utf-8")}"

        return rsa_decrypt(private_key, data)

        """ list = json.loads(decrypt(data, key)) 
        obj = list[1]

        return obj['message'] """

    except Exception as e:
        return f"Failed to decrypt message: {str(e)}"