from all_args import *
from anonymize import *
from parse_audit import *
from traverse_files import *

import os
import pwd
import sys
import platform
import time
import subprocess
import getpass

def main():

    # configure audit
    res = subprocess.run(['auditctl', '-D'], stdout=subprocess.PIPE)                                        # clear old rules
    res = subprocess.run(['auditctl', '-b', '30000'], stdout=subprocess.PIPE)                               # increase backlog buffer
    res = subprocess.run(['auditctl', '--backlog_wait_time', '0'], stdout=subprocess.PIPE)                  # minimize waiting time
    res = subprocess.run(['auditctl', '-a', 'always,exclude', '-F', 'msgtype=CWD'], stdout=subprocess.PIPE) # exclude unnecessary info
    if(platform.architecture()[0] == '64bit'):                                                              # determine architecture
        res = subprocess.run(['auditctl', '-a', 'always,exit', '-F', 'arch=b64', '-F', 'success=1', '-S', 'open,close,read,write,dup,dup2,fork,vfork,clone,lseek,mkdir,rmdir'], stdout=subprocess.PIPE)
    else:
        res = subprocess.run(['auditctl', '-a', 'always,exit', '-F', 'arch=b32', '-F', 'success=1', '-S', 'open,close,read,write,dup,dup2,fork,vfork,clone,lseek,mkdir,rmdir'], stdout=subprocess.PIPE)
    
    # at the beginning we find file sizes
    filesMap = {}
    filesMap = makeFilesMap(os.environ['HOME']+'/')
    #filesMap = makeFilesMap("/home/"+getpass.getuser()+"/")   # e.g. "/home/"

    currMap = {}

    # do it for ever
    i = 0
    while(1):
        filename = "./ftp/log" + str(i) + ".log"
        filenameout = "./ftp/log" + str(i) + "out.log"

        # then we sleep until its time to parse and upload
        time.sleep(180)
        
        # ausearch with file
        result = subprocess.run(['ausearch', '--checkpoint', 'temp.txt', '-i'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        if not result:   #(stdout is null in case of error) run ausearch -ts
            result = subprocess.run(['ausearch', '--start', 'checkpoint', 'temp.txt', '-i'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        

        file = open(filename,"a+")
        file.write(result)
        file.close()

        # parse and upload
        currMap = parse(filename,filenameout,filesMap,currMap)

        # immediately delete /var/log/audit/*
        #subprocess.run(['rm', '/var/log/audit/*'])
        #subprocess.run(['rm', 'log.log'])

        # FTP log transfer 
        # https://www.pythonforbeginners.com/code-snippets-source-code/how-to-use-ftp-in-python

if __name__ == "__main__":
    main()
