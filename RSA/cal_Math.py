# Calculation Method File
from transform import decimalToBinaryCalMod
import sys

sys.setrecursionlimit(2000)

# Calculate Modulus
def calMod(a, m, n):
    d = 1
    b = decimalToBinaryCalMod(m)
    for i in b:
        d = (d*d)%n
        if i != "0" :
            d = (d*a)%n
    return d

#Greatest Common Divisor
def gcd(m, n) :
    if m < n :
        (m, n) = (n, m)
    if (m%n) == 0 :
        return n 
    else:
        return (gcd(n, m % n))

#Totient Function
def totient(p, q) :
    return (p-1)*(q-1)

#ExtEuclid Function (for use in inverse)
def ExtEuclid(a, b) : # process for find e
    if b == 0 :
        return(a, 1, 0)
    else:
        (c1, x1, y1) = ExtEuclid(b, a%b)
        c = c1
        x = y1
        y = x1 - (a//b)*y1
        return (c, x, y)