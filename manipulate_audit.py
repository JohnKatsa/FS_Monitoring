from all_args import *
from anonymize import *

"""function to read an audit record and extract data"""
def read_record(data,fh_to_fn_and_p):
    for token in data:
        # read
        if "syscall=read" == token:
            read_write_args(data,0,fh_to_fn_and_p)
        # write
        elif "syscall=write" == token:
            read_write_args(data,1,fh_to_fn_and_p)
        # open
        elif "syscall=open" == token:
            open_args(data,fh_to_fn_and_p)
        # close
        elif "syscall=close" == token:
            close_args(data,fh_to_fn_and_p)
        # lseek
        elif "syscall=lseek" == token:
            lseek_args(data,fh_to_fn_and_p)
        # dup, dup2, dup3
        elif "syscall=dup" == token or "syscall=dup2" == token or "syscall=dup3" == token:
            dup_args(data,fh_to_fn_and_p)
        # fork, clone, vfork
        elif "syscall=fork" == token or "syscall=clone" == token:
            fork_args(data,fh_to_fn_and_p)
        # pread
        elif "syscall=pread" == token:
            pread_pwrite_args(data,0,fh_to_fn_and_p)
        # pwrite
        elif "syscall=pwrite" == token:
            pread_pwrite_args(data,1,fh_to_fn_and_p)

def main():
    useful = []
    record = ""

    fh_to_fn_and_p = {} # list with a pid, a file handler, a file name and a file pointer
    print ("DATE \t OPERATION \t FILENAME \t POSITION \t PROCESS_ID")

    with open ("/home/katsanis/Desktop/input3", "r") as myfile:
        for line in myfile:
            if "----" not in line:
                useful.append(line)
            else:   # new record
                if record:  # if there has been data, store them
                    read_record(record.split(),fh_to_fn_and_p)
                useful = []
            record = "".join(useful)

if __name__ == "__main__":
    main()
