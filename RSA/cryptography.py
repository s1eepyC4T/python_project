# Encryption and Decryption File
import math
from transform import binaryToDecimal,decimalToBinary,decToText,textToDecimal
from cal_Math import calMod
import json, os

# div block for encrypt
def divBlockEncrypt(cipherBin,n): # n = blockSize
    ans = []
    numCipherBin = len(str(cipherBin)) #length of message
    numOfBlock=math.floor(numCipherBin/n) #number of block
    tempCipher=str(cipherBin) #Temporary Message
    numTempCipher = len(tempCipher) #length of temp messg
    # reminder=int(numTempCipher%n)
    for i in range(0,numOfBlock+1):
        if numTempCipher>=n:
            ans.append(tempCipher[0:n])
            tempCipher=tempCipher[n:]
            numTempCipher=len(tempCipher)
        elif numTempCipher < n : #padding
            for i in range(0,n-numTempCipher):
                if i==0:
                    tempCipher=tempCipher+"1"
                else: tempCipher=tempCipher+"0"
            ans.append(tempCipher[0:n])
            tempCipher=tempCipher[n:]
            numTempCipher=len(tempCipher)
    return ans

# encryption
def encrypt(plaintxt, user):
    plaintxt=str(plaintxt)
    folder = os.path.join(user, user)
    fileName = "publicKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        publicKey = json.load(file)

    e = publicKey["e"]
    n = publicKey["n"]
    
    cipherBlock,plainNum,cipherNum,plainDeci =[],[],[],[]
    ans,plainBin="",""
    plainDeci = textToDecimal(plaintxt)
    for i in plainDeci:
        plainBin += decimalToBinary(i,8)
    blockSize = math.floor(math.log2(n))
    plainBlock = divBlockEncrypt(plainBin,blockSize)
    for i in plainBlock: #convert plain blockfrom bin to dec 
        plainNum.append(binaryToDecimal(i))
        
    for i in plainNum:
        cipherNum.append(calMod(i,e,n))
    for i in cipherNum:
        cipherBlock.append(decimalToBinary(i, blockSize+1))

    for i in cipherBlock:
        ans=ans+i[:]
    return ans

# div block for decrypt
def divBlockDecrypt(cipherTxt,n):
    ans = []
    tempCipherTxt = str(cipherTxt)
    while len(tempCipherTxt) > 0:
        s=tempCipherTxt[:n]
        ans.append(s)
        tempCipherTxt=tempCipherTxt[n:]
    return ans

# div block for answer (text after decryption)
def divBlockAns(ansBin,n): # n = blockSize
    ans = []
    numAnsBin = len(str(ansBin)) #length of message
    numOfBlock=math.ceil(numAnsBin/n) #number of block
    tempAns=str(ansBin) #Temporary Message
    for i in range(0,numOfBlock):
        ans.append(tempAns[0:n])
        tempAns=tempAns[n:]
    return ans

# decryption
def decrypt(ciphertxt, user):
    ciphertxt=str(ciphertxt)
    folder = os.path.join(user, user)
    fileName = "privateKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        publicKey = json.load(file)

    d = publicKey["d"]
    n = publicKey["n"]
    
    cipherNum,plainNum,plainBlock= [],[],[]
    ansBin=""
    ansDeci,ansBlock=[],[]

    ans=""
    blockSize = math.floor(math.log2(n))+1
    cipherBlock = divBlockDecrypt(ciphertxt,blockSize)
    for i in cipherBlock:
        cipherNum.append(binaryToDecimal(i))

    for i in cipherNum:
        plainNum.append(calMod(i,d,n))

    for i in plainNum:
        plainBlock.append(decimalToBinary(i, blockSize-1))
        
    for i in plainBlock:
        ansBin=ansBin+i

    cur = len(ansBin)-1 #last index of ans
    while True :
        if ansBin[cur] == '0':
            cur-=1
        elif ansBin[cur] == '1':
            ansBin = ansBin[:cur] 
            break
    ansBlock=divBlockAns(ansBin,8)
    for i in ansBlock:
        ansDeci.append(binaryToDecimal(i))

    for i in ansDeci:
        ans+=decToText(i)

    return ans

# CA encryption
def encryptCA(plaintxt, user):
    plaintxt=str(plaintxt)
    folder = os.path.join(user, user)
    fileName = "privateKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        publicKey = json.load(file)

    d = publicKey["d"]
    n = publicKey["n"]
    
    cipherBlock,plainNum,cipherNum,plainDeci =[],[],[],[]
    ans,plainBin="",""
    plainDeci = textToDecimal(plaintxt)
    for i in plainDeci:
        plainBin += decimalToBinary(i,8)
    blockSize = math.floor(math.log2(n))
    plainBlock = divBlockEncrypt(plainBin,blockSize)
    for i in plainBlock: #convert plain blockfrom bin to dec 
        plainNum.append(binaryToDecimal(i))
        
    for i in plainNum:
        cipherNum.append(calMod(i,d,n))
    for i in cipherNum:
        cipherBlock.append(decimalToBinary(i, blockSize+1))

    for i in cipherBlock:
        ans=ans+i[:]
    return ans

# CA decryption
def decryptCA(ciphertxt, user):
    ciphertxt=str(ciphertxt)
    folder = os.path.join(user, user)
    fileName = "publicKey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        publicKey = json.load(file)

    e = publicKey["e"]
    n = publicKey["n"]
    
    cipherNum,plainNum,plainBlock= [],[],[]
    ansBin=""
    ansDeci,ansBlock=[],[]

    ans=""
    blockSize = math.floor(math.log2(n))+1
    cipherBlock = divBlockDecrypt(ciphertxt,blockSize)
    for i in cipherBlock:
        cipherNum.append(binaryToDecimal(i))

    for i in cipherNum:
        plainNum.append(calMod(i,e,n))

    for i in plainNum:
        plainBlock.append(decimalToBinary(i, blockSize-1))
        
    for i in plainBlock:
        ansBin=ansBin+i

    cur = len(ansBin)-1 #last index of ans
    while True :
        if ansBin[cur] == '0':
            cur-=1
        elif ansBin[cur] == '1':
            ansBin = ansBin[:cur] 
            break
    ansBlock=divBlockAns(ansBin,8)
    for i in ansBlock:
        ansDeci.append(binaryToDecimal(i))

    for i in ansDeci:
        ans+=decToText(i)

    return ans