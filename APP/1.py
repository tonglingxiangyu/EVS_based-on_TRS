import random
import sys
from RingSignature.RingSignature import *
from RingSignature.RSA import *
signer_ok = []
for i in range(5):

    t = 0
    while (t in signer_ok):
        t = random.randint(0, 9)
    signer_ok.append(t)
print(signer_ok)

# dirpath = sys.path[0]
# signer=[1,2,3,4,5]
# t=(1,2)
# with open(dirpath+'/../signer_key/signer0.txt', 'r') as fp:
#     content = fp.read()
#     str = content.split('}')
#     str1 = str[0]
#     str1 = str1 + '}'
#     str1 = str1.replace('\n', '')
#     print(str1)
#     d = eval(str1)
#     t=list(t)
#     t[0]=d
#     t=tuple(t)
#
#     str2=str[1]
#     str2 = str2 + '}'
#     str2 = str2.replace('\n', '')
#     print(str2)
#     e = eval(str2)
#     t = list(t)
#     t[1] = e
#     t = tuple(t)
