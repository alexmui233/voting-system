total = 100
def func():
    # refer to global variable 'total' inside function
    global total
    if total > 10:
        total = 15
print('Total = ', total)
func()
print('Total = ', total)

# https://asecuritysite.com/encryption/ring_sig
import os, hashlib, random, Crypto.PublicKey.RSA
import sys
from functools import reduce

class ring:
    def __init__(self, k, L=1024):
        self.k = k
        self.l = L
        self.n = len(list(k))
        self.q = 1 << (L - 1)

    def sign(self, m, z):
        self.permut(m)
        #print("self.permut(m)", self.permut(m))
        s = [None] * self.n
        ''' print("self.n:", self.n)
        print("s:", s) '''
        u = random.randint(0, self.q)
        ''' print("self.q:", self.q)
        print("u:", u) '''
        c = v = self.E(u) 
        ''' print("self.E(u):", self.E(u) )
        print("v:", v)
        print("c:", c) '''
        for i in (list(range(z+1, self.n)) + list(range(z))):
            ''' print("list(range(z+1, self.n)):", list(range(z+1, self.n)), "\n")
            print("list(range(z)):", list(range(z)), "\n") '''
            s[i] = random.randint(0, self.q)
            #print("s[i]:", s[i], "\n")
            e = self.g(s[i], self.k[i].e, self.k[i].n)
            ''' print("self.k[i].e", self.k[i].e, "\n")
            print("self.k[i].n", self.k[i].n, "\n")
            print("e", e, "\n") '''
            v = self.E(v^e) 
            ''' print("v^e:",  v^e, "\n")
            print("self.E(v^e):",  self.E(v^e), "\n")
            print("v:",  v, "\n")
            print("i+1:", i+1, "\n")
            print("self.n:", self.n, "\n") '''
            if (i+1) % self.n == 0:
                c = v
                #print("c:", c, "\n")
        s[z] = self.g(v^u, self.k[z].d, self.k[z].n)
        ''' print("v^u:", v^u, "\n")
        print("self.k[z].d:", self.k[z].d, "\n")
        print("self.k[z].n:", self.k[z].n, "\n")
        print("self.g(v^u, self.k[z].d, self.k[z].n):", self.g(v^u, self.k[z].d, self.k[z].n), "\n")
        print("s[z]:", s[z], "\n")
        print("[c]:", [c], "\n")
        print("s:", s, "\n")
        print("[c] + s:", [c] + s, "\n") '''
        return [c] + s

    def verify(self, m, X):
        self.permut(m)
        def f1(i):
            ''' print("f1:X:", X, "\n")
            print("f1:X[i+1]:", X[i+1], "\n")
            print("f1:self.k[i].e:", self.k[i].e, "\n")
            print("f1:self.k[i].n:", self.k[i].n, "\n")
            print("f1:self.g(X[i+1], self.k[i].e, self.k[i].n):", self.g(X[i+1], self.k[i].e, self.k[i].n), "\n") '''
            return self.g(X[i+1], self.k[i].e, self.k[i].n)
        y = list(map(f1, list(range(len(X)-1))))
        #print("f1:y:", y, "\n")
        def g1(x, i):
            ''' print("g1: x:", x, "\n")
            print("g1: y[i]:", y[i], "\n")
            print("g1: self.E(x^y[i]):", self.E(x^y[i]), "\n") '''
            return self.E(x^y[i])
        r = reduce(g1, list(range(self.n)), X[0])
        ''' print("list(range(self.n)):", list(range(self.n)), "\n")
        print("X[0]:", X[0], "\n")
        print("reduce(g1, list(range(self.n)), X[0]):", reduce(g1, list(range(self.n)), X[0]), "\n")
        print("r:", r, "\n") '''
        return r == X[0]

    def permut(self, m):
        self.p = int(hashlib.sha256(m.encode()).hexdigest(),16)

    def E(self, x): 
        msg = '%s%s' % (x, self.p)
        ''' print("E:msg: ", msg)
        print("E: int(hashlib.sha256(msg.encode()).hexdigest(),16):", int(hashlib.sha256(msg.encode()).hexdigest(),16), "\n") '''
        return  int(hashlib.sha256(msg.encode()).hexdigest(),16)

    def g(self, x, e, n):
        q, r = divmod(x, n)
        ''' print("q:", q, "\n")
        print("r:", r, "\n")
        print("divmod(x, n):", divmod(x, n), "\n")
        print("(q + 1) * n:", (q + 1) * n, "\n")
        print("(1 << self.l) - 1:", (1 << self.l) - 1, "\n") '''
        if ((q + 1) * n) <= ((1 << self.l) - 1):
            ''' print("q * n", q * n, "\n")
            print("pow(r, e, n)", pow(r, e, n), "\n") '''
            result = q * n + pow(r, e, n)
        else:
            #print("g:x:", x)
            result = x
        #print("result", result, "\n")
        return result

size = 4
msg1="Hello"
msg2="Hello2"

def rn(_):
  return Crypto.PublicKey.RSA.generate(1024, os.urandom)

print(("Message is:",msg1))
key = list(map(rn, list(range(size))))
''' print("rn:", rn)
print("range(size):", range(size))
print("list(range(size)):", list(range(size)))
print("map(rn, list(range(size))):", map(rn, list(range(size))))
print("list(map(rn, list(range(size)))):", list(map(rn, list(range(size)))))
print() '''
r = ring(key)
s1 = r.sign(msg1, 0)
s2 = r.sign(msg2, 0)
print(("Signature is", s1))
print(("Signature verified:",r.verify(msg1, s1)))
print(("Signature verified (will fail):",r.verify(msg2, s1)))
for i in range(size):
    s1 = r.sign(msg1, i)
    s2 = r.sign(msg2, i)
    if (i==1):
      print(("Signature is", s1))
      print(("Signature verified:",r.verify(msg1, s1)))
      print(("Signature verified (will fail):",r.verify(msg2, s1)))
