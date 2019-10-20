from anonymize import *

"""function to determine date of log record"""
def get_record_date(date):
    readable_date = ""
    flag = False
    for letter in date:
        if letter == "(":
            flag = True
        elif letter == ".":
            flag = False
        elif flag:
            readable_date += letter
    return readable_date

"""function to determine read/write arguments"""
def read_write_args(data,sys_id,fh_to_fn_and_p,filesMap,fileNameOut):
    date = ""
    flag = False
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "exit=" in token:
            bytes_num = token.split("=")[1]
        elif "msg=" in token:
            date = token.split("=")[1]
            flag = True
        elif flag:
            date += " " + token
            date = get_record_date(date)
            flag = False

    pid = int(pid)              # this is the process id
    fh = int(fh,16)             # this is the file descriptor
    bytes_num = int(bytes_num)  # this is the number of bytes read or written

    # check if open audited
    if (pid,fh) in fh_to_fn_and_p:
        # also move file pointer
        name, pos = fh_to_fn_and_p[(pid,fh)]
        fh_to_fn_and_p[(pid,fh)] = [name,pos+bytes_num]
        #filesMap[] # move file pointer if &gt

        f = open(fileNameOut,"a+")
        if sys_id == 0: # read
            print(date + "\t" + "READ\t", name, "\t", pos, "\t", bytes_num, pid, file=f)
        elif sys_id == 1:   # write
            print(date + "\t" + "WRITE\t", name, "\t", pos, "\t", bytes_num, pid, file=f)
        f.close()

"""function to determine open arguments"""
def open_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    # if seccomp ignore
    if "SECCOMP" in data:
        return
    
    date = ""
    name = ""
    flag = 1
    flags = ""
    fh = 0
    dateflag = False
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "name=" in token and flag:
            name = token.split("=")[1]
            flag = 0
        elif "name=" in token:
            f = open(fileNameOut,"a+")
            print(date + "\t" + "OPENDIR \t", anonymize(token.split("=")[1]), file=f)
            f.close()
        elif "exit=" in token:
            fh = token.split("=")[1]
        elif "a1=" in token:
            flags = token.split("=")[1]
        elif "msg=" in token:
            date = token.split("=")[1]
            dateflag = True
        elif dateflag:
            date += " " + token
            date = get_record_date(date)
            dateflag = False

    # anonymize file name
    anonymizedName = anonymize(name)    # anonymize name to store
    pid = int(pid)                      # process id
    fh = int(fh)                        # file descriptor

    if "O_CREAT" in flags:
        filesMap[anonymizedName] = 0 # check at which point we should start

    if "O_APPEND" in flags:
        if anonymizedName in filesMap:
            pos = filesMap[anonymizedName] # check at which point we should start
        else:
            pos = 0
        fh_to_fn_and_p[(pid,fh)] = [anonymizedName,pos]
    else:
        fh_to_fn_and_p[(pid,fh)] = [anonymizedName,0]

    f = open(fileNameOut,"a+")
    print (date + "\t" + "OPEN\t" + anonymizedName, "\t", pid, "\t", fh, file=f)
    f.close()

"""function to determine close arguments"""
def close_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    date = ""
    flag = False
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "msg=" in token:
            date = token.split("=")[1]
            flag = True
        elif flag:
            date += " " + token
            date = get_record_date(date)
            flag = False

    pid = int(pid)      # process id
    fh = int(fh,16)     # file descriptor   

    # search for pid
    # delete (pid,fh) from map
    if fh_to_fn_and_p.get((pid,fh)):
        name, pos = fh_to_fn_and_p[(pid,fh)]
        del fh_to_fn_and_p[(pid,fh)]

        f = open(fileNameOut,"a+")
        print(date + "\t" + "CLOSE\t", name, file=f)
        f.close()

"""function to determine lseek arguments"""
def lseek_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    date = ""
    flag = False
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "a1=" in token:
            offset = token.split("=")[1]
        elif "a2=" in token:
            flags = token.split("=")[1]
        elif "msg=" in token:
            date = token.split("=")[1]
            flag = True
        elif flag:
            date += " " + token
            date = get_record_date(date)
            flag = False

    pid = int(pid)              # process id
    fh = int(fh,16)             # file descriptor
    offset = int(offset,16)     # number of bytes to move file pointer

    f = open(fileNameOut,"a+")
    if (pid,fh) in fh_to_fn_and_p:
        # SEEK_SET set position to constant value
        if "SEEK_SET" in flags:
            [name, pos] = fh_to_fn_and_p[(pid,fh)]
            fh_to_fn_and_p[(pid,fh)] = [name,offset]
            print(date + "\t" + "LSEEK \t", pid, "\t", fh, "\t", name, "\t", offset, file=f)
        # SEEK_CUR set position from current position
        elif "SEEK_CUR" in flags:
            [name, pos] = fh_to_fn_and_p[(pid,fh)]
            fh_to_fn_and_p[(pid,fh)] = [name,pos+offset]
            print(date + "\t" + "LSEEK \t", pid, "\t", fh, "\t", name, "\t", pos+offset, file=f)
    f.close()

"""function to determine dup/dup2/dup3 arguments"""
def dup_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    date = ""
    flag = False
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            oldfh = token.split("=")[1]
        elif "exit=" in token:
            newfh = token.split("=")[1]
        elif "msg=" in token:
            date = token.split("=")[1]
            flag = True
        elif flag:
            date += " " + token
            date = get_record_date(date)
            flag = False

    pid = int(pid)          # process id 
    oldfh = int(oldfh,16)   # old file descriptor
    newfh = int(newfh)      # new file descriptor 

    # change mapping value
    if fh_to_fn_and_p.get((pid,oldfh)):
        # copy old fd data to new fd record
        fh_to_fn_and_p[(pid,newfh)] = fh_to_fn_and_p.get((pid,oldfh))

        f = open(fileNameOut,"a+")
        print(date + "\t" + "DUP\t", "old fd = ", oldfh, "\t new fd = ", newfh, file=f)
        f.close()

"""function to determine fork/clone/vfork arguments"""
def fork_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    date = ""
    flag = False
    for token in data:
        if "pid=" in token:
            ppid = token.split("=")[1]
        elif "exit=" in token:
            pid = token.split("=")[1]
        elif "msg=" in token:
            date = token.split("=")[1]
            flag = True
        elif flag:
            date += " " + token
            date = get_record_date(date)
            flag = False

    pid = int(pid)      # process id
    ppid = int(ppid)    # parent process id

    tmp_dict = {}   # dict changed size error solution
    for key in fh_to_fn_and_p:
        if key[0] == ppid:
            tmp_dict[(pid,key[1])] = fh_to_fn_and_p.get(key).copy()

    fh_to_fn_and_p.update(tmp_dict)

    f = open(fileNameOut,"a+")
    print(date + "\t" + "FORK \t", "parent = ", ppid, "\t child = ", pid, file=f)
    f.close()

"""function to determine pread/pwrite arguments"""
def pread_pwrite_args(data,sys_id,fh_to_fn_and_p,filesMap,fileNameOut):
    date = ""
    flag = False
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "exit=" in token:
            bytes_num = token.split("=")[1]
        elif "a3=" in token:
            pos = token.split("=")[1]
        elif "msg=" in token:
            date = token.split("=")[1]
            flag = True
        elif flag:
            date += " " + token
            date = get_record_date(date)
            flag = False

    pid = int(pid)                  # process id
    fh = int(fh,16)                 # file descriptor
    bytes_num = int(bytes_num)      # number of bytes read or written
    pos = int(pos,16)               # position in file

    # write the results to map
    var = fh_to_fn_and_p.get((pid,fh))
    if var:
        name, pos = var
        fh_to_fn_and_p[(pid,fh)] = [name,pos+bytes_num]

        f = open(fileNameOut,"a+")
        if sys_id == 0: # read
            print(date + "\t" + "PREAD\t", name, "\t", pos, "\t", bytes_num, "\t", pid, file=f)
        elif sys_id == 1:   # write
            print(date + "\t" + "PWRITE\t", name, "\t", pos, "\t", bytes_num, "\t", pid, file=f)
        f.close()
