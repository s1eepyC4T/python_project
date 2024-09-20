# Key Generation File
import random as r
import json
import os
from cal_Math import gcd, ExtEuclid, calMod,totient

# Find n value 
def findN(p,q): #return int n 
    n=p*q
    return n

# Miller-Rabin Test for Probable Prime
def shouldBePrime(n, k=40):
    # n is what we want to check
    # k is the number of rounds. The higher k, the higher chance it's a prime
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # n - 1 = 2^s * d
    # We want to check if n is prime, starting by assuming n is prime
    # In order to find s and d, we need to factor 2^s from n
    # The factor we'll get is 2^s and an odd number d
    s = 0
    d = n - 1 
    # d%2 continuously to find s
    while d % 2 == 0:
        d //= 2
        s += 1

    # Loop to validate prime n
    # Randomly choose a that in the range 2 < a < n - 1
    # The higher k, the higher chance it's prime
    # k = 40 is good for security reason
    # To check, if the result of modulo is 1 or -1, we continue checking for "liar"
    # If there is just one "a" that makes a^d mod n not equal to 1 or -1, n is composite
    # But if the loop is done k times, it's probably prime 
    for _ in range(k):
        a = r.randint(2, n - 2) # n - 2 is inclusive
        x = calMod(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = calMod(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# Generate Prime Number
def generatePrime(bits):
    while True:
        # Generate a random odd number
        candidate = r.getrandbits(bits) | 1
        if shouldBePrime(candidate):
            return int(candidate)

# Find e value  
def findE(phi) :#phi = totient
    upBound = phi-1
    while True:
        e = r.randint(1, upBound)
        if gcd(e, phi) == 1 :
           return e

# Find d value
def findD(e, phi) : #phi = totient, e = public
    a = e
    b = phi
    (c, d, y) = ExtEuclid(a, b)
    return d % phi

# Generate Key
def genKeyPair(user, bits):
    bits = int(bits)
    p = generatePrime(bits)
    q = generatePrime(bits)
    n = findN(p, q)
    phi = totient(p, q)
    e = findE(phi)
    d = findD(e, phi)

    publicKey = {
        "e": e,
        "n": n
    }

    privateKey = {
        "d": d,
        "n": n
    }

    pubFileName = "publicKey.json"
    priFileName = "privateKey.json"
    directory = os.path.join(user, user)
    pubPath = os.path.join(directory, pubFileName)
    priPath = os.path.join(directory, priFileName)

    os.makedirs(directory, exist_ok=True)

    with open(pubPath, "w") as pubfile:
        json.dump(publicKey, pubfile, indent=2)

    with open(priPath, "w") as prifile:
        json.dump(privateKey, prifile, indent=2)

def givePublicKeyFrom_to(sender,receiver):	
    #copy publicKey
    folder = os.path.join(sender, sender)
    fileName = "publickey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'r') as file:
        data = json.load(file)
    e=data["e"]
    n=data["n"]
    publicKeyDict={"e":e, "n":n}
    #send publicKey to receiver
    folder = os.path.join(receiver, sender)
    fileName = "publickey.json"
    directory = os.path.join(folder, fileName)
    with open(directory, 'w') as file:
        json.dump(publicKeyDict,file,indent=2)