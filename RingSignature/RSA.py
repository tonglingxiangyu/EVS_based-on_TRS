from Utils import generatePrimeNumber
import random

class RSA:

    def gcd(self, a, b): #求最大公因数
        while b != 0:
            a, b = b, a % b
        return a



    def egcd(self, a, b): #求逆元
        if a == 0:
            return (b, 0, 1)
        g, y, x = self.egcd(b % a, a)
        return (g, x - (b // a) * y, y)

    def multiplicative_inverse(self, a, m):
        g, x, y = self.egcd(a, m)
        if g != 1:
            raise Exception('No modular inverse')
        return x % m

    def generateKeyPair(self): #生成RSA公私钥对
        length = 128
        p = generatePrimeNumber(length)
        q = generatePrimeNumber(length)

        while p == q:
            q = generatePrimeNumber(length)

        n = p * q
        phi = (p - 1) * (q - 1)

        e = random.randrange(1, phi) #公钥e
        g = self.gcd(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = self.gcd(e, phi)

        d = self.multiplicative_inverse(e, phi) #私钥d


        #公钥(e, n)，私钥(d, n)

        return ({'key':e,'n':n}, {'key':d,'n':n},)

    def sign(self, plaintext, pk):
        # Convert each letter in the plaintext to numbers based on the character using a^b mod m
        cypher = [pow(ord(char), pk['key'], pk['n']) for char in plaintext]

        return cypher

    def verify(self, plaintext, cypher, pk):
        plain = [chr(pow(char, pk['key'], pk['n'])) for char in cypher]
        return ''.join(plain) == plaintext

rsa = RSA()
keypair = rsa.generateKeyPair()
#print(keypair)
#print("Text_to_cipher")
message = '123'
#print(message)
#print('length: '+str(len(message)))
cypher = rsa.sign(message,keypair[0])
#print("cyphered")
#print(cypher)
#print('length: '+str(len(cypher)))
#print("decipher")
#print(rsa.verify(message, cypher, keypair[1]))