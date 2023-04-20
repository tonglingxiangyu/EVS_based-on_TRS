# -*- coding: utf-8 -*-
'''
# Created on Feb-20-20 13:26
# util.py
# @author: ss
'''

'''
一些公用函数
包括：
窗口居中
'''
import sys
import random
from PyQt5.QtWidgets import QDesktopWidget
from random import SystemRandom
import datetime


dirpath = sys.path[0]

def write_log_to_Text(log):
    """
    记录日志
    """
    now = datetime.datetime.now()
    s2 = now.strftime("%Y/%m/%d %H:%M:%S ")
    with open(dirpath+'/../log.txt','a',encoding='utf-8') as fp:
        fp.write(s2+log+'\n')

def center(model):
    '''
    实现窗口居中
    '''
    qr = model.frameGeometry() #获得主窗口所在的框架。
    cp = QDesktopWidget().availableGeometry().center() # 获取显示器的分辨率，然后得到屏幕中间点的位置。
    qr.moveCenter(cp) # 然后把主窗口框架的中心点放置到屏幕的中心位置。
    model.move(qr.topLeft()) # 然后通过move函数把主窗口的左上角移动到其框架的左上角，这样就把窗口居中了

def rabinMiller(num):
	s = num - 1
	t = 0
	while s % 2 == 0:
		s //= 2
		t += 1
	for trials in range(5):
		a = random.randrange(2,num-1)
		v = pow(a,s,num)
		if v!=1:
			i = 0
			while v!=(num-1):
				if i == t-1:
					return False
				else:
					i += 1
					v = (v**2)%num
	return True

lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

def isPrime(num):
	if num < 2:
		return False

	if num in lowPrimes:
		return True
	for prime in lowPrimes:
		if num % prime==0:
			return False

	return rabinMiller(num)

def create_primes(num=2):
    '''
    从2开始生成num个连续的素数的列表
    [2, 3, 5, ...]
    '''
    primes = []
    x = 2
    while len(primes) < num:
        if isPrime(x) == True:
            primes.append(x)
        x = x + 1
    return primes


class CurveFp:
    def __init__(self, A, B, P, N, Gx, Gy, name):
        self.A = A
        self.B = B
        self.P = P
        self.N = N
        self.Gx = Gx
        self.Gy = Gy
        self.name = name

sm2p256v1 = CurveFp(
	name="sm2p256v1",
	A=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC,
	B=0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93,
	P=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF,
	N=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123,
	Gx=0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7,
	Gy=0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
)

def multiply(a, n, N, A, P):
    return fromJacobian(jacobianMultiply(toJacobian(a), n, N, A, P), P)

def add(a, b, A, P):
    return fromJacobian(jacobianAdd(toJacobian(a), toJacobian(b), A, P), P)

def inv(a, n):
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % n

def toJacobian(Xp_Yp):
    Xp, Yp = Xp_Yp
    return (Xp, Yp, 1)

def fromJacobian(Xp_Yp_Zp, P):
    Xp, Yp, Zp = Xp_Yp_Zp
    z = inv(Zp, P)
    return ((Xp * z ** 2) % P, (Yp * z ** 3) % P)

def jacobianDouble(Xp_Yp_Zp, A, P):
    Xp, Yp, Zp = Xp_Yp_Zp
    if not Yp:
        return (0, 0, 0)
    ysq = (Yp ** 2) % P
    S = (4 * Xp * ysq) % P
    M = (3 * Xp ** 2 + A * Zp ** 4) % P
    nx = (M ** 2 - 2 * S) % P
    ny = (M * (S - nx) - 8 * ysq ** 2) % P
    nz = (2 * Yp * Zp) % P
    return (nx, ny, nz)

def jacobianAdd(Xp_Yp_Zp, Xq_Yq_Zq, A, P):
    Xp, Yp, Zp = Xp_Yp_Zp
    Xq, Yq, Zq = Xq_Yq_Zq
    if not Yp:
        return (Xq, Yq, Zq)
    if not Yq:
        return (Xp, Yp, Zp)
    U1 = (Xp * Zq ** 2) % P
    U2 = (Xq * Zp ** 2) % P
    S1 = (Yp * Zq ** 3) % P
    S2 = (Yq * Zp ** 3) % P
    if U1 == U2:
        if S1 != S2:
            return (0, 0, 1)
        return jacobianDouble((Xp, Yp, Zp), A, P)
    H = U2 - U1
    R = S2 - S1
    H2 = (H * H) % P
    H3 = (H * H2) % P
    U1H2 = (U1 * H2) % P
    nx = (R ** 2 - H3 - 2 * U1H2) % P
    ny = (R * (U1H2 - nx) - S1 * H3) % P
    nz = (H * Zp * Zq) % P
    return (nx, ny, nz)

def jacobianMultiply(Xp_Yp_Zp, n, N, A, P):
    Xp, Yp, Zp = Xp_Yp_Zp
    if Yp == 0 or n == 0:
        return (0, 0, 1)
    if n == 1:
        return (Xp, Yp, Zp)
    if n < 0 or n >= N:
        return jacobianMultiply((Xp, Yp, Zp), n % N, N, A, P)
    if (n % 2) == 0:
        return jacobianDouble(jacobianMultiply((Xp, Yp, Zp), n // 2, N, A, P), A, P)
    if (n % 2) == 1:
        return jacobianAdd(jacobianDouble(jacobianMultiply((Xp, Yp, Zp), n // 2, N, A, P), A, P), (Xp, Yp, Zp), A, P)


class PrivateKey:
    def __init__(self, curve=sm2p256v1, secret=None):
        self.curve = curve
        self.secret = secret or SystemRandom().randrange(1, curve.N)

    def publicKey(self):
        curve = self.curve
        xPublicKey, yPublicKey = multiply((curve.Gx, curve.Gy), self.secret, A=curve.A, P=curve.P, N=curve.N)
        return PublicKey(xPublicKey, yPublicKey, curve)

    def toString(self):
        return "{}".format(str(hex(self.secret))[2:].zfill(64))

class PublicKey:
    def __init__(self, x, y, curve):
        self.x = x
        self.y = y
        self.curve = curve

    def toString(self, compressed=True):
        return {
            True: str(hex(self.x))[2:],
            False: "{}{}".format(str(hex(self.x))[2:].zfill(64), str(hex(self.y))[2:].zfill(64))
        }.get(compressed)



