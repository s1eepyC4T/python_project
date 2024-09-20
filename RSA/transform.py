# Message Transformation File
import math

# Decimal -> Binary for Encryption and Decryption
def decimalToBinary(m, bit_size):
    return format(int(m), f'0{bit_size}b')

# Decimal -> Binary for modulo calculation
def decimalToBinaryCalMod(m):
    return "{0:b}".format(int(m))

# Binary -> Decimal
def binaryToDecimal(m):
    return int(str(m), 2)

# String -> Binary
def textToBinary(a):
  l,m=[],[]
  ans=""
  for i in a:
    l.append(ord(i))
  for i in l:
    m.append(str(bin(i)[2:]))
    ans=ans+str(bin(i)[2:])
    #ans=int(ans)
  return ans

# String -> Decimal
def textToDecimal(a):
    l=[]
    for i in a:
        l.append(ord(i))
    return l

# Decimal -> String
def decToText(n):
    return chr(n)
