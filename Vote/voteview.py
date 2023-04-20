# -*- coding: utf-8 -*-
'''
# Created on Feb-21-20 14:30
# voteview.py
# @author: ss
投票窗口动态演示
'''

import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit,
                        QVBoxLayout, QHBoxLayout,
                        QFrame, QMessageBox, QPushButton,
                        QCheckBox, 
                        QApplication)
from PyQt5.QtGui import QFont, QIcon

import os 
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/'+'..'))
import hashlib
from APP.util import center
from Database.vote import getVotenum, getVoteData, updataUsrRecord
from Database.launch import updateTotal, updatevote
from gmssl import sm2
from RingSignature.RingSignature import *
from RingSignature.RSA import *
from util import write_log_to_Text

dirpath = sys.path[0]
threshold=2 #门限值
signer_num=5 #签名者数量

class Voteview(QWidget):
    '''
    usr: 当前用户
    title（str): 活动标题
    data(choice(str), tag(int)): 投票活动数据
    votelimt(int): 一个人最多可以投多少票
    '''
    def __init__(self, usr, title, data, votelimit=1, captcha=None):
        super().__init__()
        self.usr = usr 
        self.votelimit = votelimit
        self.captcha = captcha
        self.initUI(title, data)

    def initUI(self, title, data):

        title = QLabel(title)
        title.setFont(QFont('微软雅黑', 15))
        
        tophbox = QHBoxLayout()
        tophbox.addStretch(1)
        tophbox.addWidget(title)
        tophbox.addStretch(1)

        self.checkBox = []
        self.num = len(data)
        self.createCheckBox(data)
        
        midvbox = QVBoxLayout()
        for x in self.checkBox:
            midvbox.addWidget(x)
        
        midhbox = QHBoxLayout()
        midhbox.addStretch(1)
        midhbox.addLayout(midvbox)
        midhbox.addStretch(1)
        midhbox.setStretchFactor(midhbox, 2)

        midFrame = QFrame()
        midFrame.setFrameShape(QFrame.WinPanel)
        midFrame.setLayout(midhbox)

        voteuse = QLabel('当前可投票数: ')
        self.voteuseLine = QLineEdit()
        self.voteuseLine.setReadOnly(True)
        self.getVotenum()

        downhbox = QHBoxLayout()
        downhbox.addStretch(1)
        downhbox.addWidget(voteuse)
        downhbox.addWidget(self.voteuseLine)
        downhbox.addStretch(1)

        self.confirmButton = QPushButton('投票')
        self.confirmButton.setFont(QFont('黑体', 12))
        self.confirmButton.setIcon(QIcon(dirpath+'/../image/ok.png'))
        self.confirmButton.clicked.connect(self.onConfirm)

        bottomhbox = QHBoxLayout()
        bottomhbox.addStretch(1)
        bottomhbox.addWidget(self.confirmButton)
        bottomhbox.addStretch(1)

        totalLayout = QVBoxLayout()
        totalLayout.addLayout(tophbox)
        totalLayout.addWidget(midFrame)
        totalLayout.addLayout(downhbox)
        totalLayout.addLayout(bottomhbox)

        self.setLayout(totalLayout)

        center(self)
        self.resize(400, 300)
        self.setWindowTitle('投票')
        self.setWindowIcon(QIcon(dirpath+'/../image/voteview.png'))

    def createCheckBox(self, data):
        for x in data:
            text = x[0] + '-' + str(x[1])
            checkBox = QCheckBox(text)
            checkBox.setFont(QFont('宋体', 16))
            self.checkBox.append(checkBox)

    def getVotenum(self):
        if self.captcha is None:
            self.voteuseLine.setText(str(self.votelimit))
        else:
            votenum = getVotenum(self.captcha, self.usr, self.votelimit)
            self.voteuseLine.setText(str(votenum))

    def onConfirm(self):
        if self.captcha is None:
            QMessageBox.warning(self, 'warning', '这只是一个预览效果', QMessageBox.Yes)
            return 
        if int(self.voteuseLine.text()) == 0:
            QMessageBox.information(self, 'sorry', '您的投票次数已经用光', QMessageBox.Yes)
            return None
        cnt = 0

        for x in self.checkBox:
            if x.isChecked() == True:
                cnt = cnt + 1
                if cnt > int(self.voteuseLine.text()):
                    QMessageBox.warning(self, 'warning', '您的票数不足够, 请重新勾选', QMessageBox.Yes)
                    return None
                text = x.text()
                data = text.split('-')
                m=data[0]
                abstract1 = hashlib.md5(m.encode()).hexdigest()  # 对摘要进行签名

                #使用sm2加密
                with open(dirpath+'/../server_key/admin_pub.txt', encoding='utf-8') as fp:
                    public_key = fp.read()
                with open(dirpath+'/../server_key/admin_pri.txt', encoding='utf-8') as fp:
                    private_key = fp.read()
                sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)
                enc_data = sm2_crypt.encrypt(m.encode())
                write_log_to_Text('接受用户' + self.usr + '加密数据：'+str(enc_data))
                # n = str(enc_data)
                # n = n.replace("b'", '')
                # enc_data = n.replace("'", '')

                # 签名者对摘要进行签名
                rsa = RSA()
                ringSig = RingSignature()
                signerkeyPair = rsa.generateKeyPair()
                nonSignerKeyPair=[]
                # 添加门限特征，达到门限的环成员才可以签名
                signer_ok = []
                for i in range(threshold):
                    t=0
                    while(t in signer_ok):
                        t = random.randint(0, signer_num-1)
                    signer_ok.append(t)
                    write_log_to_Text('signer'+str(t)+'参与签名')

                # 从同意签名的签名者中随机选取一个作为真正的签名者
                i=random.choice(signer_ok)
                t=(1,2)
                with open(dirpath + '/../signer_key/signer' + str(i) + '.txt', 'r') as fp:
                    content = fp.read()
                    str0 = content.split('}')
                    str1 = str0[0]
                    str1 = str1 + '}'
                    str1 = str1.replace('\n', '')
                    print(str1)
                    d = eval(str1)
                    t = list(t)
                    t[0] = d
                    t = tuple(t)

                    str2 = str0[1]
                    str2 = str2 + '}'
                    str2 = str2.replace('\n', '')
                    print(str2)
                    e = eval(str2)
                    t = list(t)
                    t[1] = e
                    t = tuple(t)
                    signerkeyPair = t

                # 加入签名者的公钥，实现不可追踪性
                for i in range(signer_num):
                    with open(dirpath+'/../signer_key/signer'+str(i)+'.txt', 'r') as fp:
                        content = fp.read()
                        str1 = content.split('}')
                        str1 = str1[0]
                        str1 = str1 + '}'
                        str1 = str1.replace('\n', '')
                        print(str1)
                        d = eval(str1)
                        nonSignerKeyPair.append(d)

                signature = ringSig.ringSign(abstract1, nonSignerKeyPair, signerkeyPair)
                write_log_to_Text(self.usr+'的投票环签名结果：'+ str(signature))

                #解密消息
                dec_data = sm2_crypt.decrypt(enc_data)
                dec_data = dec_data.decode()
                write_log_to_Text('用户' + self.usr + '数据解密结果：' + dec_data)
                abstract2=hashlib.md5(dec_data.encode()).hexdigest()
                #验证签名者签名并解密得到投票结果

                flag = ringSig.ringSigVerify(abstract2, signature)

                if flag==True:
                    QMessageBox.information(self, 'congratulation','环签名验证成功，投票有效！', QMessageBox.Yes)
                    write_log_to_Text(self.usr + '的投票环签名验证成功')
                    updatevote(self.captcha, dec_data) #更新投票结果
                    write_log_to_Text('用户' + self.usr + '投票成功')
                else :
                    write_log_to_Text(self.usr+'的投票环签名验证失败')
                    QMessageBox.information(self, 'sorry','环签名验证失败，投票无效！', QMessageBox.Yes)
        if cnt == 0:
            QMessageBox.warning(self, 'warning', '您选选择任何选项进行投票', QMessageBox.Yes)
            return None
        votenum = int(self.voteuseLine.text()) - cnt
        updataUsrRecord(self.captcha, self.usr, votenum)
        self.getVotenum()
        QMessageBox.information(self, '提示', '投票成功', QMessageBox.Yes)

if __name__ == "__main__":
    
    usr = 'ss'
    title = 'vote'
    data = [['ss', 2], ['ff', 3], ['zz', 5], ['yy', '7']]
    votelimit = 3
    captcha = 'c3d509ebd011c4428abad04c1f171ac0'
    data = getVoteData(captcha)

    app = QApplication(sys.argv)
    voteview = Voteview(usr=usr, title=title, data=data, votelimit=votelimit, captcha=captcha)
    voteview.show()
    sys.exit(app.exec_())
