"simple anonymization function"
def anonymize(name):
    retname = ""

    #load mapping file
    lettersMap = {}
    with open ("mapping.txt", "r") as myfile:
        for line in myfile:
            key = line.split("\t")[0]
            value = line.split("\t")[1]
            lettersMap[key] = value

    for c in name:
        if c in lettersMap:
            retname += lettersMap[c]
        else:   # eg greek
            retname += c

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

    for c in name:
        if c in lettersMap:
            retname += lettersMap[c]
        else:
            retname += c

    return retname