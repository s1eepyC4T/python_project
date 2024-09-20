# SSL Protocol
import random as r
import os, base64, hashlib, json
from cryptography import encryptCA, encrypt, decrypt, decryptCA
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

#client introduce to server
def clientHello(sender,receiver):
    nameSender=str(sender)
    N =r.getrandbits(64)
    N = int(N)
    #Set path and name to file
    fileName1 = "clientHello.json"
    fileName2 = "clientHelloCopy.json"
    directory1 = os.path.join(receiver, "SSLMessage")
    directory2 = os.path.join(sender, "SSLMessage")
    filePath1 = os.path.join(directory1, fileName1)
    filePath2 = os.path.join(directory2, fileName2)

    #data in dict
    dict = {"User": nameSender,
            "Ver": base64.b64encode(b'\x03\x00').decode('utf-8'),
            "Suite": base64.b64encode(b'\x00\x2F').decode('utf-8'),
            "N": N }
    
    # Ensure the directory exists
    os.makedirs(directory1, exist_ok=True)#real message
    os.makedirs(directory2, exist_ok=True)#copy message
    
    #send(create file) message to receiver
    with open(filePath1, "w") as file:
        json.dump(dict, file, indent=4)

    #send(create file) the copy message to sender
    with open(filePath2, "w") as file:
        json.dump(dict, file, indent=4)
        
#server respond
def serverHello(sender, receiver):
    # set data in dict
    nameSender = str(sender)
    VerS = base64.b64encode(b'\x03\x00').decode('utf-8')  # sender version SSL 3.0
    SuiteS = base64.b64encode(b'\x00\x2F').decode('utf-8')  # Example Cipher Suite
    N = int(r.getrandbits(64))
    
    # get sender public key
    folder = os.path.join(sender, sender)
    fileName = "publicKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        publicKey = json.load(file)
    
    # send dict to CA to ask for signature (skip sending to CA)
        
    e = publicKey["e"]
    e = str(e)
    n = publicKey["n"]
    n = str(n)
    signCA = {
            "PublicKey": publicKey,
            "Message":nameSender+e+n,
            "HashedMessage": encryptCA(hashlib.sha256((nameSender+e+n).encode()).digest(), "CA")
            }
    
    # Send files
    fileName1 = "serverHelloCopy.json"
    fileName2 = "serverHello.json"
    directory1 = os.path.join(sender, "SSLMessage")#copy message
    directory2 = os.path.join(receiver, "SSLMessage")#real message
    filePath1 = os.path.join(directory1, fileName1)
    filePath2 = os.path.join(directory2, fileName2)
    
    # Ensure the directory exists
    os.makedirs(directory1, exist_ok=True)
    os.makedirs(directory2, exist_ok=True)
    
    # Construct the ServerHello message
    senderHelloDict = {
        "Sender": nameSender,
        "Ver": VerS,
        "Suite": SuiteS,
        "N": N,
        "signCA": signCA
    }
    
    # Write the ServerHello message to a JSON file
    with open(filePath1, "w") as file:
        json.dump(senderHelloDict, file, indent=5)

    with open(filePath2, "w") as file:
        json.dump(senderHelloDict, file, indent=5)


def generateSecret():
    # Generate 32 bytes of random data
    secretBytes = os.urandom(32)
    # Encode the bytes as a base64 string for easy handling
    secretBase64 = base64.b64encode(secretBytes).decode('utf-8')
    return secretBase64

def deriveKey(secret, owner, target):
    # Derive a 256-bit AES key from the shared secret using a SHA-256 hash function
    key = hashlib.sha256(secret.encode()).hexdigest()
    
    # Session Key
    sskey = {
        "Owner": owner,
        "TalkWith": target,
        "key": key
    }

    # Store the session key
    folder = os.path.join(owner, target)
    fileName = "sessionKey.json"
    os.makedirs(folder, exist_ok=True)
    directory = os.path.join(folder, fileName)
    with open(directory, "w") as file:
        json.dump(sskey, file, indent=3)

#client to server: client send certificate, encrypt message
def clientKeyExchange(sender, receiver):
    nameSender=str(sender)
    #get data from serverHello
    folder = os.path.join(sender, "SSLMessage")
    fileName = "serverHello.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        data = json.load(file)
    
    #check secretKey
    M=data["signCA"]["Message"]
    HM=decryptCA(data["signCA"]["HashedMessage"],"CA")
    #if attacked
    if str(hashlib.sha256(M.encode()).digest())!=str(HM):
        return print("Fail")
    #if not attacked
    else: 
    #create publicKey
        e=data["signCA"]["PublicKey"]["e"]
        n=data["signCA"]["PublicKey"]["n"]
        publicKey={
                "e":e,
                "n":n
                    }
        #save publicKey in JSON file 
        folder = os.path.join(sender, receiver)
        fileName = "publicKey.json"
        directory = os.path.join(folder, fileName)
        with open(directory, 'w') as file:
            json.dump(publicKey, file, indent=2)
    #get data from publicKey
    folder = os.path.join(sender, sender)
    fileName = "publicKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        publicKey = json.load(file)
    e = publicKey["e"]
    e = str(e)
    n = publicKey["n"]
    n = str(n)
    #create the first element of message: signCA{C,PUc}
    signCA = {
            "SenderName": nameSender,
            "PublicKey": publicKey,
            "Message":nameSender+e+n,
            "HashedMessage": encryptCA(hashlib.sha256((nameSender+e+n).encode()).digest(), "CA")
            }
    
    #generate sessionKey of sender
    secret=str(generateSecret())
    deriveKey(secret, sender, receiver)

    #create the second element of message: {secret of sender}PUs
    encryptSecret=encrypt(secret,receiver)

    #create the third element of message: signSender{hash(secret of sender)}
    sign=encryptCA(hashlib.sha256(secret.encode()).digest(), sender)
    dict={
        "signCA": signCA,
        "Secret":encryptSecret,
        "Sign": sign
    }

    #Send (create file) message to receiver
    fileName="ClientKeyExchange.json"
    folder=os.path.join(receiver,"SSLMessage")
    filePath=os.path.join(folder,fileName)
    os.makedirs(folder, exist_ok=True)
    with open(filePath, "w") as file:
        json.dump(dict, file, indent=3)

#server verifies received    
def ServerVerification(sender,receiver):
    #check received message
    folder = os.path.join(sender, "SSLMessage")
    fileName = "ClientKeyExchange.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        data = json.load(file)

    #check first element in message
    M=data["signCA"]["Message"]
    HM=decryptCA(data["signCA"]["HashedMessage"],"CA")
    if str(hashlib.sha256(M.encode()).digest())!=str(HM):
        return print("Fail again")
    
    #keep secret (second element of messsage)
    secret=decrypt(data["Secret"],sender)
    deriveKey(secret,sender,receiver)

    #check third element in message
    hashSecret=decryptCA(data["Sign"],receiver)
    if str(hashlib.sha256(secret.encode()).digest())!=str(hashSecret):
        return print("Fail again and again")
    
    #get data from clientHello and serverHello and hash each of them
    folder = os.path.join(sender, "SSLMessage")
    fileName = "serverHelloCopy.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        data1 = json.load(file)

    verSender=str(hashlib.sha256((data1["Ver"]).encode()).digest())
    suiteSender=str(hashlib.sha256((data1["Suite"]).encode()).digest())
    NServer=str(hashlib.sha256((str(data1["N"])).encode()).digest())

    folder = os.path.join(sender, "SSLMessage")
    fileName = "clientHello.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        data2 = json.load(file)

    verReceiver=str(hashlib.sha256((data2["Ver"]).encode()).digest())
    suiteReceiver=str(hashlib.sha256((data2["Suite"]).encode()).digest())
    NReceiver=str(hashlib.sha256((str(data2["N"])).encode()).digest())
    
    #concat them all
    ConcatOfhashMessage=verSender+suiteSender+NServer+verReceiver+suiteReceiver+NReceiver

    #get key from sessionKey
    folder = os.path.join(sender, receiver)
    fileName = "sessionKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        keyDict = json.load(file)
    keyhex = keyDict["key"]
    key = bytes.fromhex(keyhex)
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(ConcatOfhashMessage.encode(), AES.block_size))
    text = base64.b64encode(ciphertext).decode('utf-8')
    iv = base64.b64encode(cipher.iv).decode('utf-8')

    #Encrypt data by using sessionKey
    dict={
        "hashMessage":text,
        "iv": iv
        }
    
    #send message
    fileName = "ServerVerification.json"
    directory = os.path.join(receiver, "SSLMessage")
    filePath = os.path.join(directory, fileName)
    os.makedirs(directory, exist_ok=True)
    with open(filePath, "w") as file:
        json.dump(dict, file, indent=1)

#client verifies responds
def ClientVerification(sender,receiver):
    folder = os.path.join(sender, "SSLMessage")
    fileName = "serverHello.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        data1 = json.load(file)

    verSender=str(hashlib.sha256((data1["Ver"]).encode()).digest())
    suiteSender=str(hashlib.sha256((data1["Suite"]).encode()).digest())
    NServer=str(hashlib.sha256((str(data1["N"])).encode()).digest())

    folder = os.path.join(sender, "SSLMessage")
    fileName = "clientHelloCopy.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        data2 = json.load(file)

    verReceiver=str(hashlib.sha256((data2["Ver"]).encode()).digest())
    suiteReceiver=str(hashlib.sha256((data2["Suite"]).encode()).digest())
    NReceiver=str(hashlib.sha256((str(data2["N"])).encode()).digest())
    
    ConcatOfhashMessage=verSender+suiteSender+NServer+verReceiver+suiteReceiver+NReceiver
    
    #encrypt
    folder = os.path.join(sender, receiver)
    fileName = "sessionKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        keyDict = json.load(file)
    keyhex = keyDict["key"]
    key = bytes.fromhex(keyhex)
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(ConcatOfhashMessage.encode(), AES.block_size))
    text = base64.b64encode(ciphertext).decode('utf-8')
    iv = base64.b64encode(cipher.iv).decode('utf-8')

    dict={
        "hashMessage":text,
        "iv": iv
        }
    
    #send back
    fileName = "ClientVerification.json"
    directory = os.path.join(receiver, "SSLMessage")
    filePath = os.path.join(directory, fileName)
    os.makedirs(directory, exist_ok=True)
    with open(filePath, "w") as file:
        json.dump(dict, file, indent=1)


