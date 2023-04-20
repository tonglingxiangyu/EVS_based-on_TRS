from RingSignature import RingSignature
from RSA import RSA
from Crypto.Hash import SHA256
import random
import array

#setup
rsa = RSA()
ringSig = RingSignature()

#TestSignature
signerkeyPair = rsa.generateKeyPair()
print("signer ")
print(signerkeyPair)


print("nonsigners ")
nonSignerKeyPair = []
nonSignerKeyPair.append(rsa.generateKeyPair()[0]) #p0
nonSignerKeyPair.append(rsa.generateKeyPair()[0]) #p0
nonSignerKeyPair.append(rsa.generateKeyPair()[0]) #p0
nonSignerKeyPair.append(rsa.generateKeyPair()[0]) #p0
print('Number of nonsigner: '+str(len(nonSignerKeyPair)))
print(nonSignerKeyPair)

msg = "meu queijo frsco jjjjjjjjjjjjjjjj"
signature = ringSig.ringSign(msg, nonSignerKeyPair, signerkeyPair)
print('signature glue')
#print(signature)
print(signature['glue'])
print('confirming... the signature')
print(ringSig.ringSigVerify(msg, signature))