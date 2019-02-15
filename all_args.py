from anonymize import *

"""function to determine read/write arguments"""
def read_write_args(data,sys_id,fh_to_fn_and_p,filesMap,fileNameOut):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "exit=" in token:
            bytes_num = token.split("=")[1]

    pid = int(pid)
    fh = int(fh,16)
    bytes_num = int(bytes_num)

    # check if open audited
    if (pid,fh) in fh_to_fn_and_p:
        # also move file pointer
        name, pos = fh_to_fn_and_p[(pid,fh)]
        fh_to_fn_and_p[(pid,fh)] = [name,pos+bytes_num]
        #filesMap[] # move file pointer if &gt

        f = open(fileNameOut,"a+")
        if sys_id == 0: # read
            print("READ\t", name, "\t", pos, "\t", bytes_num, pid, file=f)
        elif sys_id == 1:   # write
            print("WRITE\t", name, "\t", pos, "\t", bytes_num, pid, file=f)
        f.close()

"""function to determine open arguments"""
def open_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    name = ""
    flag = 1
    flags = ""
    fh = 0
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "name=" in token and flag:
            name = token.split("=")[1]
            flag = 0
        elif "name=" in token:
            f = open(fileNameOut,"a+")
            print("OPENDIR \t", anonymize(token.split("=")[1]), file=f)
            f.close()
        elif "exit=" in token:
            fh = token.split("=")[1]
        elif "a1=" in token:
            flags = token.split("=")[1]

    # anonymize file name
    anonymizedName = anonymize(name)
    #anonymizedName = name
    pid = int(pid)
    fh = int(fh)

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
    print ("OPEN\t", anonymizedName, pid, fh, file=f)
    f.close()

"""function to determine close arguments"""
def close_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]

    pid = int(pid)
    fh = int(fh,16)

    #search for pid
    if fh_to_fn_and_p.get((pid,fh)):
        name, pos = fh_to_fn_and_p[(pid,fh)]
        #print(pid,fh,name,pos)
        del fh_to_fn_and_p[(pid,fh)]

        f = open(fileNameOut,"a+")
        print("CLOSE\t", name, file=f)
        f.close()

"""function to determine lseek arguments"""
def lseek_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "a1=" in token:
            offset = token.split("=")[1]
        elif "a2=" in token:
            flags = token.split("=")[1]

    pid = int(pid)
    fh = int(fh,16)
    offset = int(offset,16)

    f = open(fileNameOut,"a+")
    if (pid,fh) in fh_to_fn_and_p:
        # SEEK_SET set position to constant value
        if "SEEK_SET" in flags:
            [name, pos] = fh_to_fn_and_p[(pid,fh)]
            fh_to_fn_and_p[(pid,fh)] = [name,offset]
            print("LSEEK \t", pid, fh, name, offset, file=f)
        # SEEK_CUR set position from current position
        elif "SEEK_CUR" in flags:
            [name, pos] = fh_to_fn_and_p[(pid,fh)]
            fh_to_fn_and_p[(pid,fh)] = [name,pos+offset]
            print("LSEEK \t", pid, fh, name, pos+offset, file=f)
    f.close()

"""function to determine dup/dup2/dup3 arguments"""
def dup_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            oldfh = token.split("=")[1]
        elif "exit=" in token:
            newfh = token.split("=")[1]

    pid = int(pid)
    oldfh = int(oldfh,16)
    newfh = int(newfh)

    if fh_to_fn_and_p.get((pid,oldfh)):
        # copy old fd data to new fd record
        fh_to_fn_and_p[(pid,newfh)] = fh_to_fn_and_p.get((pid,oldfh))

        f = open(fileNameOut,"a+")
        print("DUP\t", "old fd = ", oldfh, "\t new fd = ", newfh, file=f)
        f.close()

    #print(fh_to_fn_and_p)

"""function to determine fork/clone/vfork arguments"""
def fork_args(data,fh_to_fn_and_p,filesMap,fileNameOut):
    for token in data:
        if "pid=" in token:
            ppid = token.split("=")[1]
        elif "exit=" in token:
            pid = token.split("=")[1]

    pid = int(pid)
    ppid = int(ppid)

    tmp_dict = {}   # dict changed size error solution
    for key in fh_to_fn_and_p:
        #print(key[0])
        if key[0] == ppid:
            tmp_dict[(pid,key[1])] = fh_to_fn_and_p.get(key).copy()

    #print(tmp_dict)

    fh_to_fn_and_p.update(tmp_dict)

    #print(fh_to_fn_and_p)

    f = open(fileNameOut,"a+")
    print("FORK \t", "parent = ", ppid, "\t child = ", pid, file=f)
    f.close()

"""function to determine pread/pwrite arguments"""
def pread_pwrite_args(data,sys_id,fh_to_fn_and_p,filesMap,fileNameOut):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "exit=" in token:
            bytes_num = token.split("=")[1]
        elif "a3=" in token:
            pos = token.split("=")[1]

    pid = int(pid)
    fh = int(fh,16)
    bytes_num = int(bytes_num)
    pos == int(pos,16)

    # write the results to map
    var = fh_to_fn_and_p.get((pid,fh))
    if var:
        name, pos = var
        fh_to_fn_and_p[(pid,fh)] = [name,pos+bytes_num]

        f = open(fileNameOut,"a+")
        if sys_id == 0: # read
            print ("PREAD\t", name, "\t", pos, "\t", bytes_num, pid, file=f)
        elif sys_id == 1:   # write
            print ("PWRITE\t", name, "\t", pos, "\t", bytes_num, pid, file=f)
        f.close()