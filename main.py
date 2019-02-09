from all_args import *
from anonymize import *
from parse_audit import *
from traverse_files import *

import time
import subprocess
import getpass

def main():
    
    # at the beginning we fid file sizes
    filesMap = {}
    filesMap = makeFilesMap("/home/"+getpass.getuser()+"/")   # e.g. "/home/"

    currMap = {}

    # do it for ever
    i = 0
    while i<1:
        # then we sleep until its time to parse and upload
        #if(i == 1):
        #    time.sleep(3)
                                
        result = subprocess.run(['ausearch', '--checkpoint', 'temp.txt', '-i'], stdout=subprocess.PIPE)

        file = open("log.log","a+")
        file.write(result.stdout.decode('utf-8'))
        file.close()

        # parse and upload
        currMap = parse("log.log",filesMap,currMap)

        # immediately delete /var/log/audit/*
        #subprocess.run(['rm', '/var/log/audit/*'])
        #subprocess.run(['rm', 'log.log'])

        # FTP log transfer 
        # https://www.pythonforbeginners.com/code-snippets-source-code/how-to-use-ftp-in-python
        

        i+=1


if __name__ == "__main__":
    main()