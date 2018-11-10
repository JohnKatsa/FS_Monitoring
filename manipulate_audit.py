
"""function to determine read/write arguments"""
def read_write_args(data,sys_id,pid_to_fhs,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]
        elif "exit=" in token:
            bytes_num = int(token.split("=")[1])

    pos = 0
    # write the results to map
    for x in fh_to_fn_and_p:
        # found record in map
        if x[0] == fh:
            pos = x[2]
            x[2] += bytes_num

    # find name
    name = ""
    for x in fh_to_fn_and_p:
        if x[0] == fh:
            name = x[1]
    if sys_id == 0 and name: # read
        print "READ\t", name, "\t", pos, "\t", bytes_num
    elif sys_id == 1 and name:   # write
        print "WRITE\t", name, "\t", pos, "\t", bytes_num


"""function to determine open arguments"""
def open_args(data,pid_to_fhs,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "name=" in token:
            name = token.split("=")[1]
        elif "exit=" in token:
            fh = token.split("=")[1]

    #search for pid
    flag = 0
    for p in pid_to_fhs:
        #found it
        if p[0] == pid:
            flag = 1
            p[1].append(fh)
    if flag == 0:   # first time this pid occured
        pid_to_fhs.append([pid,[fh]])

    # store file handler
    fh_to_fn_and_p.append([fh,name,0])

    print "OPEN\t", name

"""function to determine open arguments"""
def close_args(data,pid_to_fhs,fh_to_fn_and_p):
    for token in data:
        if "pid=" in token:
            pid = token.split("=")[1]  # take second arg (collision with ppid, but pid is second so it keeps correct value)
        elif "a0=" in token:
            fh = token.split("=")[1]

    #search for pid
    for p in pid_to_fhs:
        #found it
        if p[0] == pid:
            if len(p[1]) == 1:  # last item
                del p
            else:
                del p[1]

    # store file handler
    for x in fh_to_fn_and_p:
        if x[0] == fh:
            del x

    print "CLOSE\t", name


"""function to read an audit record and extract data"""
def read_record(data,pid_to_fhs,fh_to_fn_and_p):
    for token in data:
        # read
        if "syscall=0" in token:
            read_write_args(data,0,pid_to_fhs,fh_to_fn_and_p)
        # write
        if "syscall=1" in token:
            read_write_args(data,1,pid_to_fhs,fh_to_fn_and_p)
        # open
        if "syscall=2" in token:
            open_args(data,pid_to_fhs,fh_to_fn_and_p)
        # close
        if "syscall=3" in token:
            close_args(data,pid_to_fhs,fh_to_fn_and_p)

    #print data, " \\\\\ "

def main():
    useful = []
    record = ""

    pid_to_fhs = []  # list with an process id and a list of fhs as an item
    fh_to_fn_and_p = [] # list with a file handler, a file name and a file pointer

    with open ("report.txt", "r") as myfile:
        for line in myfile:
            if "----" not in line:
                useful.append(line)
            else:   # new record
                if record:  # if there has been data, store them
                    read_record(record.split(),pid_to_fhs,fh_to_fn_and_p)
                useful = []
            record = "".join(useful)

        print pid_to_fhs
        print "----------"
        print fh_to_fn_and_p

if __name__ == "__main__":
    main()
