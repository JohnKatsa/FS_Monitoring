"simple anonymization function"
def anonymize(name):
    retname = ""
    for c in name:
        if ord(c) <= 33 + 31:
            retname += chr(ord(c) + 31)
        elif ord(c) <= 33 + 62:
            retname += chr(ord(c) + 31)
        else:
            retname += chr(ord(c) - 62)

    return retname

def deanonymize(name):
    retname = ""
    for c in name:
        if ord(c) <= 33 + 31:
            retname += chr(ord(c) + 62)
        elif ord(c) <= 33 + 62:
            retname += chr(ord(c) - 31)
        else:
            retname += chr(ord(c) - 31)

    return retname
