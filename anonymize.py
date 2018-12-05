"simple anonymization function"
def anonymize(name):
    retname = ""
    for c in name:
        retname += chr((ord(c)-17)%(126-33) + 34)

    return retname
