#EVS_based-on_TRS
基于门限环签名的电子投票系统（Electronic Voting System Based on Threshold Ring Signature）
#First
打开mysql，配置好数据库账号密码；
#Second
运行APP目录下server.py登录admin账号，
	第一步，生成sm2公私钥；
	第二步，发起投票；
	第三步，生成签名者的公私钥；
	第四步，随时可以查看投票情况。
#Then
运行APP目录下client.py登录账号，
	第一步，投票；
	第二步，随时可以查看投票情况。
#Last
每一步操作都会被记录在日志文件log.txt中。