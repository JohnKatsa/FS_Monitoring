from all_args import *

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
        # dup, dup2, dup3
        elif "syscall=32" == token or "syscall=33" == token or "syscall=292" == token:
            dup_args(data,fh_to_fn_and_p,time)
        # fork, clone, vfork
        elif "syscall=57" == token or "syscall=58" == token:
            fork_args(data,fh_to_fn_and_p,time)
        # pread
        elif "syscall=17" == token:
            pread_pwrite_args(data,0,fh_to_fn_and_p,time)
        # pwrite
        elif "syscall=18" == token:
            pread_pwrite_args(data,1,fh_to_fn_and_p,time)

    #print data, " \\\\\ "

def main():
    useful = []
    record = ""

    fh_to_fn_and_p = [] # list with a pid, a file handler, a file name and a file pointer

    with open ("report3.txt", "r") as myfile:
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
