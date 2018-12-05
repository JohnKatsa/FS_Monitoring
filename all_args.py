"""function to determine read/write arguments"""
def read_write_args(data,sys_id,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = int(token.split("=")[1],16)
        elif "exit=" in token:
            bytes_num = int(token.split("=")[1],16)

    # check if open audited
    if (pid,fh) in fh_to_fn_and_p:
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
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "name=" in token and flag:
            name = token.split("=")[1]
            flag = 0
        elif "name=" in token:
            print("OPENDIR \t", token.split("=")[1])
        elif "exit=" in token:
            fh = int(token.split("=")[1])
        elif "success=" in token:
            success = token.split("=")[1]

    # check if same pid with same fh does it more than once
    fh_to_fn_and_p[(pid,fh)] = [name,0]

    print ("OPEN\t", name, pid, fh)

"""function to determine close arguments"""
def close_args(data,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]

    #search for pid
    if (pid,fh) in fh_to_fn_and_p:
        del fh_to_fn_and_p[(pid,fh)]

"""function to determine lseek arguments"""
def lseek_args(data,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "a1=" in token:
            offset = token.split("=")[1]

    if (pid,fh) in fh_to_fn_and_p:
        [name, pos] = fh_to_fn_and_p[(pid,fh)]
        fh_to_fn_and_p[(pid,fh)] = [name,pos+bytes_num]

"""function to determine dup/dup2/dup3 arguments"""
def dup_args(data,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            oldfh = token.split("=")[1]
        elif "exit=" in token:
            newfh = token.split("=")[1]
        elif "success=" in token:
            success = token.split("=")[1]

    if success:
        fh_to_fn_and_p[(pid,newfh)] = fh_to_fn_and_p.get((pid,oldfh))

"""function to determine fork/clone/vfork arguments"""
def fork_args(data,fh_to_fn_and_p):
    for token in data:
        if "ppid=" in token:
            ppid = token.split("=")[1]
        elif "pid=" in token:
            pid = token.split("=")[1]
        elif "success=" in token:
            success = token.split("=")[1]

    if success:
        for key, value in fh_to_fn_and_p.items():
            if key[0] == ppid:
                fh_to_fn_and_p[(pid,key[1])] = fh_to_fn_and_p.get(key).copy()

"""function to determine pread/pwrite arguments"""
def pread_pwrite_args(data,sys_id,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "exit=" in token:
            bytes_num = int(token.split("=")[1])
        elif "a3=" in token:
            pos = int(token.split("=")[1])

    name = ""
    # write the results to map
    if name:
        name, pos = fh_to_fn_and_p[(pid,fh)]
        fh_to_fn_and_p[(pid,fh)] = [name,pos+bytes_num]

    if sys_id == 0 and name: # read
        print ("PREAD\t", name, "\t", pos, "\t", bytes_num, pid)
    elif sys_id == 1 and name:   # write
        print ("PWRITE\t", name, "\t", pos, "\t", bytes_num, pid)
