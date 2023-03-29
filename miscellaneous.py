from math import gcd
import hashlib


def Hash(issue, publicKeys, g, p, q):
    s = issue
    for keys in publicKeys:
        s.join(keys)
    binary = ''.join(format(ord(x), 'b') for x in s)
    hashed = int(hashlib.sha1(binary.encode()).hexdigest(), 16)
    hashed = pow(g, pow(hashed, 1, q), p)
    return hashed

def HashPrime(issue, publicKeys, g, p, q, m):
    s = issue
    for keys in publicKeys:
        s.join(keys)
    s = s+m
    binary = ''.join(format(ord(x), 'b') for x in s)
    hashed = int(hashlib.sha1(binary.encode()).hexdigest(), 16)
    hashed = pow(g, pow(hashed, 1, q), p)
    return hashed

def HashPrimePrime(issue, message,  publicKeys, g, p, q, A_0, A_1, a, b):
    s = issue
    for keys in publicKeys:
        s.join(keys)
    s = s + str(A_0)
    s = s + str(A_1)
    s = s + message
    for n in a + b:
        s = s + str(n)
    binary = ''.join(format(ord(x), 'b') for x in s)
    hashed = int(hashlib.sha1(binary.encode()).hexdigest(), 16)
    hashed = pow(hashed, 1, q)
    return hashed

def findCoprimeList(n):
    coprimeList = []
    for i in range(2, n):
        if(gcd(i, n) == 1):
            coprimeList.append(i)
    return coprimeList