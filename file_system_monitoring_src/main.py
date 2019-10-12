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
import signal

def signal_handler(sig, frame):
        subprocess.run(['auditctl', '-D'], stdout=subprocess.PIPE)
        print('Exiting audit program..')
        sys.exit(0)

def readConfiguration(configuration):
    file = open(configuration,"r")
    content = file.read()

    # get if first time
    first_time = content.split(":")[1]
    first_time = first_time.split("\n")[0]
    first_time = int(first_time)

    folder = content.split("\n")[1]
    folder = folder.split(":")[1]

    file.close()

    return first_time, folder

# first time run system
def assignFolder(configuration):
    # make explicit folder name in server (mac address)
    result = os.popen("ip link | grep ether | awk '{print $2}'").read()
    result = result.split("\n")[0]      # name of folder is its unique mac-address
    result = result.replace(':','')     # remove ':'
    folder = "./" + result

    subprocess.run(["mkdir", folder])

    return folder

def rewriteConfiguration(configuration,folder):
    file = open(configuration,"w")

    file.write("first time:0\nfolder:"+folder)

    file.close()

# function to remember where we are with log number
def readIterator(iterator):

    file = open(iterator,"r")

    i = file.read()

    file.close()

    return int(i)

# function to remember where we are with log number
def addplusplusIterator(iterator):

    file = open(iterator,"r")
    i = file.read()
    file.close()

    file = open(iterator,"w")
    file.write(str(int(i)+1))
    file.close()

    return int(i)+1

def configureAudit():

    # configure audit
    res = subprocess.run(['auditctl', '-D'], stdout=subprocess.PIPE)                                        # clear old rules
    res = subprocess.run(['auditctl', '-b', '30000'], stdout=subprocess.PIPE)                               # increase backlog buffer
    res = subprocess.run(['auditctl', '--backlog_wait_time', '0'], stdout=subprocess.PIPE)                  # minimize waiting time
    res = subprocess.run(['auditctl', '-a', 'always,exclude', '-F', 'msgtype=CWD'], stdout=subprocess.PIPE) # exclude unnecessary info
    res = subprocess.run(['auditctl', '-a', 'never,exit', '-F', 'dir='+os.getcwd()], stdout=subprocess.PIPE) # exclude current directory
    if(platform.architecture()[0] == '64bit'):                                                              # determine architecture
        res = subprocess.run(['auditctl', '-a', 'always,exit', '-F', 'arch=b64', '-F', 'success=1', '-S', 'open,close,read,write,dup,dup2,fork,vfork,clone,lseek,mkdir,rmdir'], stdout=subprocess.PIPE)
    else:
        res = subprocess.run(['auditctl', '-a', 'always,exit', '-F', 'arch=b32', '-F', 'success=1', '-S', 'open,close,read,write,dup,dup2,fork,vfork,clone,lseek,mkdir,rmdir'], stdout=subprocess.PIPE)

def rsyncLogs(folder):
    res = subprocess.run(["rsync", "--remove-source-files", "-av", "./"+folder+"/", "-e", "ssh", "filemonitor@dsgserver1.di.uoa.gr:/home/filemonitor/storage/"+folder+"/"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while res.returncode != 0: # while an error occured repeat
        res = subprocess.run(["rsync", "--remove-source-files", "-av", "./"+folder+"/", "-e", "ssh", "filemonitor@dsgserver1.di.uoa.gr:/home/filemonitor/storage/"+folder+"/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Rsync: Correct Password")


def main():
    
    # catch SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    # start audit daemon
    runAuditd = subprocess.run(['service', 'auditd', 'start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if runAuditd.returncode != 0:
        print("Cannot start audit daemon. Please run manually \'sudo service auditd start\'")
        return -1

    # set configuration file name
    configuration = "configuration"
    iterator = "iterator"
    subprocess.run(['rm', 'checkfile.txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    #configure audit
    configureAudit()

    currMap = {}

    # assign/make folder or find already made
    first_time, folder = readConfiguration(configuration)
    if first_time == 1:
        folder = assignFolder(configuration)
    else:
        # user messages
        print("Clean audit logs:")
        # (transfer via rsync) (check if exists log stacked from previous sessions) (rsync only at beginning)
        rsyncLogs(folder)


    # user messages
    print("Audit Configured. \nPreparing system..")

    filesMap = {}
    filesMap = makeFilesMap(os.environ['HOME']+'/')     # get user's file sizes

    # user messages
    print("System prepared.")
    print("The Audit Project successfully started!")


    rewriteConfiguration(configuration,folder)

    # do it for ever
    i = readIterator(iterator)
    while(1):
        filename = folder + "/log" + str(i) + "in.log"
        filenameout = folder + "/log" + str(i) + ".log"

        # then we sleep until its time to parse and upload
        time.sleep(180)
            
        # ausearch with file
        resultFull = subprocess.run(['ausearch', '--checkpoint', 'checkfile.txt', '-i'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = resultFull.stdout.decode('utf-8')

        if resultFull.returncode in [11,12,13]:   # run ausearch -ts in invalid timestamp
            result = subprocess.run(['ausearch', '--checkpoint', 'checkfile.txt', '--start', 'checkpoint', '-i'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        file = open(filename,"a+")
        file.write(result)
        file.close()

        # parse and upload
        currMap = parse(filename,filenameout,filesMap,currMap)

        # remove unparsed data
        subprocess.run(['rm', filename])

        i += 1
        addplusplusIterator(iterator)


if __name__ == "__main__":
    main()
