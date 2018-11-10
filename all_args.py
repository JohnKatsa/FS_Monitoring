"""function to determine read/write arguments"""
def read_write_args(data,sys_id,fh_to_fn_and_p,time):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "exit=" in token:
            bytes_num = int(token.split("=")[1])

    name = ""
    # write the results to map
    for x in fh_to_fn_and_p:
        # found record in map
        if x[0] == pid and x[1] == fh:
            pos = x[3]
            x[3] += bytes_num
            name = x[2]


    if sys_id == 0 and name: # read
        print time, "\t", "READ\t", name, "\t", pos, "\t", bytes_num, pid
    elif sys_id == 1 and name:   # write
        print time, "\t", "WRITE\t", name, "\t", pos, "\t", bytes_num, pid

"""function to determine open arguments"""
def open_args(data,fh_to_fn_and_p,time):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "name=" in token:
            name = token.split("=")[1]
        elif "exit=" in token:
            fh = token.split("=")[1]

    # check if same pid with same fh does it more than once
    for x in fh_to_fn_and_p:
        if x[0] == pid and x[1] == fh:
            return
    fh_to_fn_and_p.append([pid,fh,name,0])

    print time, "\t", "OPEN\t", name, pid, fh

"""function to determine close arguments"""
def close_args(data,fh_to_fn_and_p,time):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]

    #search for pid
    for p in fh_to_fn_and_p:
        #found it
        if p[0] == pid and p[1] == fh:
            print time, "\t", "CLOSE\t", p[2], pid
            fh_to_fn_and_p.remove(p)

"""function to determine lseek arguments"""
def lseek_args(data,fh_to_fn_and_p,time):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "a1=" in token:
            offset = token.split("=")[1]

    for x in fh_to_fn_and_p:
        if x[0] == pid and x[1] == fh:
            x[3] += offset

"""function to determine dup/dup2/dup3 arguments"""
def dup_args(data,fh_to_fn_and_p,time):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            oldfh = token.split("=")[1]
        elif "exit=" in token:
            newfh = token.split("=")[1]

    success = 0
    for x in fh_to_fn_and_p:
        if x[0] == pid and x[1] == oldfh:
            temp = x[:]
            success = 1

    if success:
        fh_to_fn_and_p.append(temp)

"""function to determine fork/clone/vfork arguments"""
def fork_args(data,fh_to_fn_and_p,time):
    for token in data:
        if "ppid=" in token:
            ppid = token.split("=")[1]
        elif "pid=" in token:
            pid = token.split("=")[1]

    temp = []
    for x in fh_to_fn_and_p:
        if x[0] == ppid:
            temp.append([pid,x[1],x[2],x[3]])
    fh_to_fn_and_p.append(x for x in temp)

"""function to determine pread/pwrite arguments"""
def pread_pwrite_args(data,sys_id,fh_to_fn_and_p,time):
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
    for x in fh_to_fn_and_p:
        # found record in map
        if x[0] == pid and x[1] == fh:
            name = x[2]


    if sys_id == 0 and name: # read
        print time, "\t", "PREAD\t", name, "\t", pos, "\t", bytes_num, pid
    elif sys_id == 1 and name:   # write
        print time, "\t", "PWRITE\t", name, "\t", pos, "\t", bytes_num, pid
