from all_args import *
from anonymize import *

"""function to read an audit record and extract data"""
def read_record(data,fh_to_fn_and_p,filesMap,fileNameOut):
    for token in data:
        # read
        if "syscall=read" == token:
            read_write_args(data,0,fh_to_fn_and_p,filesMap,fileNameOut)
        # write
        elif "syscall=write" == token:
            read_write_args(data,1,fh_to_fn_and_p,filesMap,fileNameOut)
        # open
        elif "syscall=open" == token:
            open_args(data,fh_to_fn_and_p,filesMap,fileNameOut)
        # close
        elif "syscall=close" == token:
            close_args(data,fh_to_fn_and_p,filesMap,fileNameOut)
        # lseek
        elif "syscall=lseek" == token:
            lseek_args(data,fh_to_fn_and_p,filesMap,fileNameOut)
        # dup, dup2, dup3
        elif "syscall=dup" == token or "syscall=dup2" == token or "syscall=dup3" == token:
            dup_args(data,fh_to_fn_and_p,filesMap,fileNameOut)
        # fork, clone, vfork
        elif "syscall=fork" == token or "syscall=clone" == token:
            fork_args(data,fh_to_fn_and_p,filesMap,fileNameOut)
        # pread
        elif "syscall=pread" == token:
            pread_pwrite_args(data,0,fh_to_fn_and_p,filesMap,fileNameOut)
        # pwrite
        elif "syscall=pwrite" == token:
            pread_pwrite_args(data,1,fh_to_fn_and_p,filesMap,fileNameOut)

# give file to parse, fh_to_fn_and_p: udateable from previous audit
def parse(fileName,fileNameOut,filesMap,fh_to_fn_and_p):
    useful = []
    record = ""

    #fh_to_fn_and_p = {} # list with a pid, a file handler, a file name and a file pointer
    #print ("OPERATION \t FILENAME \t POSITION \t PROCESS_ID")

    with open (fileName, "r") as myfile:
        for line in myfile:
            if "----" not in line:
                useful.append(line)
            else:   # new record
                if record:  # if there has been data, store them
                    read_record(record.split(),fh_to_fn_and_p,filesMap,fileNameOut)
                useful = []
            record = "".join(useful)

    #print(fh_to_fn_and_p)
    return fh_to_fn_and_p
