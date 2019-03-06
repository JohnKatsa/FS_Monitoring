"simple anonymization function"

"encrypt only english letters"

def anonymize(name):
    retname = ""

    #load mapping file
    lettersMap = {}
    with open ("mapping.txt", "r") as myfile:
        for line in myfile:
            key = line.split("\t")[0]
            value = line.split("\t")[1]
            lettersMap[key] = value

    # identify file ending and don't encrypt it
    limit = len(name)
    for i in range(len(name)-1,-1,-1):
        # no special ending
        if name[i] == '/':
            break

        # found special ending
        if name[i] == '.':
            limit = i+1
            break


    # change everything before ending
    for i in range(limit):
        if name[i] in lettersMap:
            retname += lettersMap[name[i]]
        else:   # eg greek
            retname += name[i]
    # copy ending as it is
    for i in range(limit,len(name)):
        retname += name[i]

    return retname  

def deanonymize(name):
    retname = ""

    #load unmapping file
    lettersMap = {}
    with open ("unmapping.txt", "r") as myfile:
        for line in myfile:
            key = line.split("\t")[0]
            value = line.split("\t")[1]
            lettersMap[key] = value

    # identify file ending and don't encrypt it
    limit = len(name)
    for i in range(len(name)-1,-1,-1):
        # no special ending
        if name[i] == '/':
            break

        # found special ending
        if name[i] == '.':
            limit = i+1
            break

    for i in range(limit):
        if name[i] in lettersMap:
            retname += lettersMap[name[i]]
        else:
            retname += name[i]
    for i in range(limit,len(name)):
        retname += name[i]

    return retname
