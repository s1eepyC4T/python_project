# Send message to the inbox of the receiver
import hashlib, os, json, base64
from cryptography import encryptCA, decryptCA
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def sendMessage(m, sender, receiver):

    # Get session key
    folder = os.path.join(sender, receiver)
    fileName = "sessionKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        keyDict = json.load(file)
    keyhex = keyDict["key"]
    key = bytes.fromhex(keyhex)

    # Certificate
    mhash = hashlib.sha256((m).encode()).hexdigest()
    cert = encryptCA(mhash, sender)
    signM = {
        "senderName": sender,
        "HashMessage": cert
    }

    # Encrypt m
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(m.encode(), AES.block_size))
    text = base64.b64encode(ciphertext).decode('utf-8')
    iv = base64.b64encode(cipher.iv).decode('utf-8')

    # The Message
    message = {
        "m": text,
        "iv": iv,
        "certificate": signM
    }

    # Send
    folder = os.path.join(receiver, "Inbox")
    fileName = "encryptedMessage.json"
    os.makedirs(folder, exist_ok=True)
    directory = os.path.join(folder, fileName)
    with open(directory, "w") as file:
        json.dump(message, file, indent=3)

def readMessage(sender, receiver):

    # Get session key
    folder = os.path.join(receiver, sender)
    fileName = "sessionKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        keyDict = json.load(file)
    keyhex = keyDict["key"]
    key = bytes.fromhex(keyhex)

    #Get message
    folder = os.path.join(receiver, "Inbox")
    fileName = "encryptedMessage.json"
    directory = os.path.join(folder, fileName)
    with open(directory, "r") as file:
        message = json.load(file)
    
    # symmetric decryption
    iv = base64.b64decode(message["iv"])
    ciphertext = base64.b64decode(message["m"])

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')

    # Check cert
    certSender = message["certificate"]["senderName"]
    certM = message["certificate"]["HashMessage"]
    MH = decryptCA(certM, sender)
    if str(certSender) == sender:
        print("The sender is correct.")
        if str(MH) == str(hashlib.sha256((decrypted_message).encode()).hexdigest()):
            print("Message is OK.")
            print(sender + " says: ", decrypted_message)
        else:
            print("Message checking fail.")
    else:
        return print("Sender checking fail.") 