from ftplib import FTP

ftp = FTP('127.0.0.1:2121')

ftp.login(user='john',passwd='john')

ftp.retrlines('LIST')

uploadFile()

def uploadFile():
    filename = 'log.log' #replace with your file in your home folder
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))
    ftp.quit()