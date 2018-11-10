
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

"""function to determine open arguments"""
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


"""function to read an audit record and extract data"""
def read_record(data,fh_to_fn_and_p):
    timeflag = 0
    time = ""
    for token in data:
        if "time->" in token:
            time += (token.split("->")[1]+' ')
            timeflag = 4
        elif timeflag:
            time += (token+' ')
            timeflag -= 1
        # read
        elif "syscall=0" == token:
            read_write_args(data,0,fh_to_fn_and_p,time)
        # write
        elif "syscall=1" == token:
            read_write_args(data,1,fh_to_fn_and_p,time)
        # open
        elif "syscall=2" == token:
            open_args(data,fh_to_fn_and_p,time)
        # close
        elif "syscall=3" == token:
            close_args(data,fh_to_fn_and_p,time)
        # lseek
        elif "syscall=8" == token:
            lseek_args(data,fh_to_fn_and_p,time)

    #print data, " \\\\\ "

def main():
    useful = []
    record = ""

    fh_to_fn_and_p = [] # list with a pid, a file handler, a file name and a file pointer

    with open ("report2.txt", "r") as myfile:
        for line in myfile:
            if "----" not in line:
                useful.append(line)
            else:   # new record
                if record:  # if there has been data, store them
                    read_record(record.split(),fh_to_fn_and_p)
                useful = []
            record = "".join(useful)
    print fh_to_fn_and_p

if __name__ == "__main__":
    main()
