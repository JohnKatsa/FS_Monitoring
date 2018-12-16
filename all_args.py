from anonymize import *

"""function to determine read/write arguments"""
def read_write_args(data,sys_id,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = int(token.split("=")[1])  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = int(token.split("=")[1],16)
        elif "exit=" in token:
            bytes_num = int(token.split("=")[1])

    # check if open audited
    if (pid,fh) in fh_to_fn_and_p:
        # also move file pointer
        name, pos = fh_to_fn_and_p[(pid,fh)]
        fh_to_fn_and_p[(pid,fh)] = [name,pos+bytes_num]

        if sys_id == 0: # read
            print ("READ\t", name, "\t", pos, "\t", bytes_num, pid)
        elif sys_id == 1:   # write
            print ("WRITE\t", name, "\t", pos, "\t", bytes_num, pid)

"""function to determine open arguments"""
def open_args(data,fh_to_fn_and_p):
    name = ""
    flag = 1
    for token in data:
        if "pid=" in token:
            pid = int(token.split("=")[1])  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "name=" in token and flag:
            name = token.split("=")[1]
            flag = 0
        elif "name=" in token:
            print("OPENDIR \t", anonymize(token.split("=")[1]))
        elif "exit=" in token:
            fh = int(token.split("=")[1])
        elif "a1=" in token:
            flags = token.split("=")[1]

    # anonymize file name
    #anonymizedName = anonymize(name)
    anonymizedName = name

    if "O_APPEND" in flags:
        pos = 0 # !!!! HOW TO DETERMINE THIS VALUE ???
        fh_to_fn_and_p[(pid,fh)] = [anonymizedName,pos]
    else:
        fh_to_fn_and_p[(pid,fh)] = [anonymizedName,0]

    print ("OPEN\t", anonymizedName, pid, fh)

"""function to determine close arguments"""
def close_args(data,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = int(token.split("=")[1])  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = int(token.split("=")[1],16)

    #search for pid
    if fh_to_fn_and_p.get((pid,fh)):
        name, pos = fh_to_fn_and_p[(pid,fh)]
        #print(pid,fh,name,pos)
        del fh_to_fn_and_p[(pid,fh)]
        print("CLOSE\t", name)

"""function to determine lseek arguments"""
def lseek_args(data,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = int(token.split("=")[1])  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = int(token.split("=")[1],16)
        elif "a1=" in token:
            offset = int(token.split("=")[1],16)
        elif "a2=" in token:
            flags = token.split("=")[1]

    if (pid,fh) in fh_to_fn_and_p:
        # SEEK_SET set position to constant value
        if "SEEK_SET" in flags:
            [name, pos] = fh_to_fn_and_p[(pid,fh)]
            fh_to_fn_and_p[(pid,fh)] = [name,offset]
            print("LSEEK \t", pid, fh, name, offset)
        # SEEK_CUR set position from current position
        elif "SEEK_CUR" in flags:
            [name, pos] = fh_to_fn_and_p[(pid,fh)]
            fh_to_fn_and_p[(pid,fh)] = [name,pos+offset]
            print("LSEEK \t", pid, fh, name, pos+offset)

"""function to determine dup/dup2/dup3 arguments"""
def dup_args(data,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = int(token.split("=")[1])  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            oldfh = int(token.split("=")[1],16)
        elif "exit=" in token:
            newfh = int(token.split("=")[1])
        elif "success=" in token:
            success = token.split("=")[1]

    if fh_to_fn_and_p.get((pid,oldfh)):
        # copy old fd data to new fd record
        fh_to_fn_and_p[(pid,newfh)] = fh_to_fn_and_p.get((pid,oldfh))
        print("DUP\t", oldfh, "\t", newfh)

    #print(fh_to_fn_and_p)

"""function to determine fork/clone/vfork arguments"""
def fork_args(data,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            ppid = int(token.split("=")[1])
        elif "exit=" in token:
            pid = int(token.split("=")[1])
        elif "success=" in token:
            success = token.split("=")[1]

    tmp_dict = {}   # dict changed size error solution
    for key in fh_to_fn_and_p:
        #print(key[0])
        if key[0] == ppid:
            tmp_dict[(pid,key[1])] = fh_to_fn_and_p.get(key).copy()

    #print(tmp_dict)

    fh_to_fn_and_p.update(tmp_dict)

    #print(fh_to_fn_and_p)

    print("FORK \t", ppid, "\t", pid)

"""function to determine pread/pwrite arguments"""
def pread_pwrite_args(data,sys_id,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = int(token.split("=")[1])  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = int(token.split("=")[1],16)
        elif "exit=" in token:
            bytes_num = int(token.split("=")[1])
        elif "a3=" in token:
            pos = int(token.split("=")[1],16)

    # write the results to map
    var = fh_to_fn_and_p.get((pid,fh))
    if var:
        name, pos = var
        fh_to_fn_and_p[(pid,fh)] = [name,pos+bytes_num]

        if sys_id == 0: # read
            print ("PREAD\t", name, "\t", pos, "\t", bytes_num, pid)
        elif sys_id == 1:   # write
            print ("PWRITE\t", name, "\t", pos, "\t", bytes_num, pid)
