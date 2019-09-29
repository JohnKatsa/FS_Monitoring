import re
import datetime
import supportLib

class record:

    def __init__(self,date):
        self.date = supportLib.auditToPythonTime(date)

    def getFields(self):
        return "date : " + self.date

    def isFileAccess(self):
        return False

    def isEditFile(self):
        return False
    
    def getFileName(self):
        return None

    def isRead(self):
        return False

    def isWrite(self):
        return False
    
    def isOpen(self):
        return False
    
    def getDate(self):
        return self.date

class readRecord(record):

    def __init__(self, date, fileName, position, numberOfBytes, processID):
        record.__init__(self, date)
        self.fileName = fileName
        self.position = position
        self.numberOfBytes = numberOfBytes
        self.processID = processID
    
    def getFields(self):
        return record.getFields(self)\
        + ", fileName : " + self.fileName + ", position : " + self.position\
        + ", numberOfBytes : " + self.numberOfBytes + ", processID : " + self.processID

    def isFileAccess(self):
        return True

    def getFileName(self):
        return self.fileName

    def isRead(self):
        return True

class writeRecord(record):

    def __init__(self, date, fileName, position, numberOfBytes, processID):
        record.__init__(self, date)
        self.fileName = fileName
        self.position = position
        self.numberOfBytes = numberOfBytes
        self.processID = processID
    
    def getFields(self):
        return record.getFields(self)\
        + ", fileName : " + self.fileName + ", position : " + self.position\
        + ", numberOfBytes : " + self.numberOfBytes + ", processID : " + self.processID

    def isFileAccess(self):
        return True

    def isEditFile(self):
        return True

    def getFileName(self):
        return self.fileName

    def isWrite(self):
        return True

class openDirRecord(record):

    def __init__(self, date, fileName):
        record.__init__(self, date)
        self.fileName = fileName

    def getFields(self):
        return record.getFields(self) + ", fileName : " + self.fileName

    def getFileName(self):
        return self.fileName

class openRecord(record):

    def __init__(self, date, fileName, processID, fileHandler):
        record.__init__(self, date)
        self.fileName = fileName
        self.processID = processID
        self.fileHandler = fileHandler

    def isFileAccess(self):
        return True

    def getFileName(self):
        return self.fileName

    def isOpen(self):
        return True

class closeRecord(record):

    def __init__(self, date, fileName):
        record.__init__(self, date)
        self.fileName = fileName

    def isFileAccess(self):
        return True

    def getFileName(self):
        return self.fileName

class lseekRecord(record):

    def __init__(self, date, processID, fileHandler, fileName, position):
        record.__init__(self, date)
        self.processID = processID
        self.fileHandler = fileHandler
        self.fileName = fileName
        self.position = position

    def isFileAccess(self):
        return True

    def getFileName(self):
        return self.fileName

class dupRecord(record):

    def __init__(self, date, oldFileHandler, newFileHandler):
        record.__init__(self, date)
        self.oldFileHandler = oldFileHandler
        self.newFileHandler = newFileHandler

class forkRecord(record):

    def __init__(self, date, parent, child):
        record.__init__(self, date)
        self.parent = parent
        self.child = child

class preadRecord(record):

    def __init__(self, date, fileName, position, numberOfBytes, processID):
        record.__init__(self, date)
        self.fileName = fileName
        self.position = position
        self.numberOfBytes = numberOfBytes
        self.processID = processID

    def isFileAccess(self):
        return True

    def getFileName(self):
        return self.fileName

    def isRead(self):
        return True

class pwriteRecord(record):

    def __init__(self, date, fileName, position, numberOfBytes, processID):
        record.__init__(self, date)
        self.fileName = fileName
        self.position = position
        self.numberOfBytes = numberOfBytes
        self.processID = processID

    def isFileAccess(self):
        return True

    def isEditFile(self):
        return True

    def getFileName(self):
        return self.fileName

    def isWrite(self):
        return True