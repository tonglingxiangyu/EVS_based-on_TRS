# -*- coding: utf-8 -*-
'''
# Created on Feb-20-20 15:05
# main.py
# @author: ss
'''

'''
应用窗口主程序
'''
import sys
import socket
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit,
                        QGridLayout, QVBoxLayout, QHBoxLayout,
                        QFrame, QMessageBox, QPushButton,
                        QAction,
                        QApplication)
from PyQt5.QtGui import QFont, QIcon

import login
import register
import util
from util import dirpath
import os 
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/'+'..'))
from Launch.launch import LaunchWindow
from Vote.vote import VoteWindow
from View.view import ViewWindow
from RingSignature.RingSignature import *
from RingSignature.RSA import *
from util import write_log_to_Text

global threshold
signer_num=5 #签名者的数量
threshold=2 #门限环签名的门限值
nonSignerKeyPair = []


class CenterWidget(QWidget):
    
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.initUI(parent)
        self.keyGenWindows = []
        self.launchWindows = []
        self.voteWindows = []
        self.viewWindows = []
    
    def initUI(self, parent):
        keyGenButton = QPushButton('密钥生成', self)
        keyGenButton.setIcon(QIcon(dirpath + '/../image/keyGen.png'))
        keyGenButton.setStyleSheet("QPushButton{color:black}"
                                   "QPushButton:hover{color:red}")
        keyGenButton.clicked.connect(lambda: self.onkeyGen(parent))

        launchButton = QPushButton('发起投票', self)
        launchButton.setIcon(QIcon(dirpath+'/../image/launch.png'))
        launchButton.setStyleSheet("QPushButton{color:black}"
                                "QPushButton:hover{color:red}")
        launchButton.clicked.connect(lambda: self.onLaunch(parent))

        SignButton = QPushButton('签名者生成', self)
        SignButton.setIcon(QIcon(dirpath + '/../image/keyGen.png'))
        SignButton.setStyleSheet("QPushButton{color:black}"
                                   "QPushButton:hover{color:red}")
        SignButton.clicked.connect(lambda: self.onSign(parent))

        viewButton = QPushButton('查看投票', self)
        viewButton.setIcon(QIcon(dirpath + '/../image/view.png'))
        viewButton.setStyleSheet("QPushButton{color:black}"
                                 "QPushButton:hover{color:red}")
        viewButton.clicked.connect(lambda: self.onView(parent))

        vbox = QVBoxLayout()
        vbox.addWidget(keyGenButton)
        vbox.addWidget(launchButton)
        vbox.addWidget(viewButton)
        vbox.addWidget(SignButton)

        midhobx = QHBoxLayout()
        midhobx.addStretch(1)
        midhobx.addLayout(vbox)
        midhobx.addStretch(1)

        centerFrame = QFrame(self)
        centerFrame.setFrameShape(QFrame.WinPanel)
        centerFrame.setLayout(midhobx)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(centerFrame)
        hbox.addStretch(1)
        hbox.setStretchFactor(centerFrame, 6)
        self.setLayout(hbox)

    def onkeyGen(self, parent):
        SM2_PRIVATE_KEY = util.PrivateKey()
        SM2_PUBLIC_KEY = SM2_PRIVATE_KEY.publicKey()
        private_key = SM2_PRIVATE_KEY.toString()
        public_key = SM2_PUBLIC_KEY.toString(compressed=False)

        with open(dirpath+"/../server_key/"+parent.usr+"_pub.txt", "w") as f:
            f.write(public_key)
        with open(dirpath+"/../server_key/"+parent.usr+"_pri.txt", "w") as f:
            f.write(private_key)
        write_log_to_Text('用户' + parent.usr + '秘钥生成成功')
        QMessageBox.information(self, 'congratulation', '秘钥保存成功', QMessageBox.Yes)
        util.write_log_to_Text(parent.usr + "的公私钥生成成功！")

    def onLaunch(self, parent):
        if parent is not None:
            self.launchWindows.append(LaunchWindow(parent.usr))
            self.launchWindows[-1].show()
            parent.showMinimized()

    def onSign(self, parent):
        if parent is not None:
            signerkeyPair = rsa.generateKeyPair()
            for i in range(signer_num):
                p = signerkeyPair
                with open(dirpath+'/../signer_key/' + 'signer' + str(i) + '.txt', 'w', encoding='utf-8') as fp:
                    for x in p:
                        fp.write(str(x))
            write_log_to_Text('签名者秘钥生成成功')
            QMessageBox.information(self, 'congratulation', '签名者秘钥保存成功', QMessageBox.Yes)


    def onView(self, parent):
        if parent is not None:
            self.viewWindows.append(ViewWindow(parent.usr))
            self.viewWindows[-1].show()
            parent.showMinimized()

class MainWindow(QMainWindow):

    def __init__(self, usr=None):
        super().__init__()
        self.usr = usr
        self.loginWindow = None 
        self.initUI()
    
    def initUI(self):
        
        #中心布局
        self.setCentralWidget(CenterWidget(self))

        #菜单栏设置
        menu = self.menuBar().addMenu('账号中心')

        signoutAct = QAction('注销', self) 
        signoutAct.triggered.connect(self.onSignout)
        menu.addAction(signoutAct)

        exitAct = QAction('退出', self)
        exitAct.triggered.connect(self.onExit)
        menu.addAction(exitAct)

        #整体布局
        self.resize(450, 300)
        util.center(self)
        self.setFont(QFont("Microsoft YaHei", 11))
        self.setWindowTitle('电子投票系统')
        self.setWindowIcon(QIcon(dirpath+'/../image/user.png'))
        
        self.bottomlbl = QLabel()
        self.bottomlbl.setFont(QFont("宋体"))
        self.statusBar().addPermanentWidget(self.bottomlbl)
        self.showbottom()

    def showbottom(self):
        #设置底部状态栏, 显示当前登录的用户
        if self.usr is not None:
            s = "欢迎你: " + self.usr + "  身份：" + self.role
            self.bottomlbl.setText(s)
        
    #注销重新登录
    def onSignout(self):
        if self.loginWindow is not None:
            self.close()
            self.loginWindow.show()
    
    def onExit(self):
        self.close()

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    loginWindow = login.LoginWindow()
    registerWindow = register.RegisterWindow()
    mainWindow = MainWindow()
    mainWindow.loginWindow = loginWindow
    registerWindow.loginWindow = loginWindow
    loginWindow.registerWindow = registerWindow
    loginWindow.mainWindow = mainWindow
    loginWindow.show()
    sys.exit(app.exec_())