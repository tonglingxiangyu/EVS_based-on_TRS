import random
import hashlib
import base64
import array
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Hash import SHA1
from Crypto import Random
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Utils import  bytesWithPadding
from Crypto.Random import get_random_bytes
from array import *


class RingSignature:

   # def ringSign(self, message, nonSignerPublickeys, signerKeyPair):
       # return self.ringSign([ord(char) for char in message], nonSignerPublickeys, signerKeyPair)

    def ringSign(self, message, nonSignerPublickeys, signerKeyPair):
        signerPubK = signerKeyPair[0]
        publicKeys  = nonSignerPublickeys

        publicKeys.append(signerPubK)

        random.shuffle(publicKeys)
        signerIndex = publicKeys.index(signerPubK)
        #print('signer_index: '+str(signerIndex))

        #0.为所有计算选择一个足够好的模量
        commonModulus = self.commonB(publicKeys)

        #1.用哈希函数计算对称秘钥k=h(m)
        k = self.calculateDigest(message)

        #2.选择一个随机的粘合值v
        glue = random.getrandbits(commonModulus.bit_length())

        #3.为非签名者选择随机值xi，并计算yi
        xValues = list(map(lambda x: random.getrandbits(commonModulus.bit_length()), publicKeys))

        yValues =  list(map(lambda x: self.g(x, publicKeys[xValues.index(x)], commonModulus) if xValues.index(x) != signerIndex else None, xValues))

        #4.求解签名者ys=Ck,v(y1，…，yn)=z=v的y_u的环方程，E(k)为对称加密算法如AES
        yS = self.solve(yValues, k, glue, commonModulus)

        #5.签名者使用自己的私钥
        xValues[signerIndex] = self.gInverse(yS, signerKeyPair)

        return {'publicKeys':publicKeys, 'glue': glue, 'xValues': xValues}

    #返回：“2^b-1”，其中b大于最大“n_i”的宽度并且是128的倍数
    def commonB(self, publicKeys):
        nMax = 0
        for pk in publicKeys:
            if pk['n'] > nMax:
                nMax = pk['n']

        sufficientBits = nMax.bit_length()+160
        if(sufficientBits % 128 >0):
            sufficientBits +=128 - (sufficientBits %128)
        return pow(2, sufficientBits) -1

    #返回g（x）=q*n+f（r），其中x=q*n+r，f（r）是RSA加密操作r^e mod n
    def g(self, x, publicKey, commonModulus):
        q = x//publicKey['n']

        result = x
        if(q + 1)*publicKey['n'] <= commonModulus:
            r = x - q*publicKey['n']
            #key=e
            fr = pow(r, publicKey['key'], publicKey['n'])
            result = q*publicKey['n']+fr
        return result

    def gInverse(self, y, keyPair):
        pub = keyPair[0]
        priv = keyPair[1]

        q = y//pub['n']

        fr = y -q*pub['n']
        #key=d
        r = pow(fr, priv['key'], pub['n'])

        return q*pub['n']+r


    #def ringSigVerity(self, message, signature):
       #return self.ringSigVerify([ord(char) for char in message] , signature)

    def ringSigVerify(self, message, signature):
        if(len(signature['publicKeys']) == len(signature['xValues'])):
            #1.计算yi
            commonModulus = self.commonB(signature['publicKeys'])
            pubkeys = signature['publicKeys']
            xValues = signature['xValues']
            yValue = list(map(lambda x: self.g(x, pubkeys[xValues.index(x)], commonModulus), xValues))

            #2.计算对称秘钥k
            k = self.calculateDigest(message)

            #3.验证者检查Ck,v(y1，…，yn)=v
            result = self.C(yValue, k, signature['glue'], commonModulus)
            print('signature_verifier')
            print(result)

            return  result == signature['glue']
        else:
            return False

    def calculateDigest(self, message):
        m = hashlib.sha256()
        m.update(message.encode("utf-8"))
        return  m.digest()



    def encrypt(self, key, source):
        obj = AES.new(key, AES.MODE_CBC, 'This is an IV456'.encode("utf8"))
        return obj.encrypt(source)


    def decrypt(self, key, source):
        obj = AES.new(key, AES.MODE_CBC, 'This is an IV456'.encode("utf8"))
        return obj.decrypt(source)


    def C(self, yValues, k, glue, commonModulus):
        result = glue

        for y in yValues:
            plaintext = y^result
            result = self.encrypt(k, bytesWithPadding(plaintext, commonModulus))
            result = int.from_bytes(result, "big")

        return result

    def solve(self, yValue, k, glue, commonModulus):
        remainingArguments = yValue
        temp = glue
        while len(remainingArguments) != 0:

            temp = self.decrypt(k, bytesWithPadding(temp, commonModulus))
            temp = int.from_bytes(temp, "big") #十六进制转换为十进制
            nextArgument = remainingArguments.pop(len(remainingArguments) - 1)

            if nextArgument:
                temp ^=nextArgument #y1^v

            else:
                #y_i of a non-signer
                temp ^= self.C(remainingArguments, k, glue, commonModulus)

                break
        return temp


