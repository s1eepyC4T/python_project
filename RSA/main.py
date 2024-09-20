from cryptography import encrypt,decrypt,encryptCA,decryptCA
import key_gen as kg
from SSL import clientHello,serverHello,clientKeyExchange,ServerVerification,ClientVerification
from send_Message import sendMessage,readMessage
import key_gen as kg

#Scenario 1: Generate user "Z" and it's own privateKey and publicKey

#kg.genKeyPair("Z", 763)

#Scenario 2: Show that encryption and decryption work

#text  = str(input("Enter message: "))
#et = encrypt(text, "A")
#dt = decrypt(et, "A") 
#print(f'encrypt: {et}, decrypt: {dt}')

#Scenario 3: Show SSL step by step

#clientHello("A", "B")
#serverHello("B", "A")
#clientKeyExchange("A", "B")
#ServerVerification("B","A")
#ClientVerification("A","B")

#Scenario 4: Show message sending

#send message
#sendMessage(m, sender, receiver)
#read message
#readMessage("A", "B")

#Scenario 5: Wrong people come to read message

#text  = str(input("Enter message: "))
#et = encrypt(text, "A")
#dt = decrypt(et, "B") 
#print(f'encrypt: {et}, decrypt: {dt}')