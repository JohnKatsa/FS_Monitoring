from recordTypes import *
import supportLib
import anonymize
import operator
import sys
import os
import json

class statsCalculator:

    recordsList = []

    def printrecordsList(self):
        
        for record in self.recordsList:
            print(record.getFields())

    def parseLogFile(self, fileName):

        with open (fileName, "r") as myfile:
            
            for line in myfile:
                
                """
                For the stats, all the file names will be without space
                """
                lineTokens = line.split("\t")
                for i in range(len(lineTokens)):
                    lineTokens[i] = re.sub(' ','',lineTokens[i])

                # dummy record initializer
                rec = record(lineTokens[0])
                syscallType = lineTokens[1]
                lineTokens.remove(lineTokens[1])

                if syscallType == "READ":
                    rec = readRecord(*lineTokens)
                elif syscallType == "WRITE":
                    rec = writeRecord(*lineTokens)
                elif syscallType == "OPENDIR":
                    rec = openDirRecord(*lineTokens)
                elif syscallType == "OPEN":
                    rec = openRecord(*lineTokens)
                elif syscallType == "CLOSE":
                    rec = closeRecord(*lineTokens)
                elif syscallType == "LSEEK":
                    rec = lseekRecord(*lineTokens)
                elif syscallType == "DUP":
                    rec = dupRecord(*lineTokens)
                elif syscallType == "FORK":
                    rec = forkRecord(*lineTokens)
                elif syscallType == "PREAD":
                    rec = preadRecord(*lineTokens)
                elif syscallType == "PWRITE":
                    rec = pwriteRecord(*lineTokens)

                self.recordsList.append(rec)

            print("Size in memory: ", sys.getsizeof(self.recordsList))
		 
    # . File system usage of opening a file (read or write)
    # returns a dictionary that contains the read and write numbers
    def fileUsage(self, startDay=None, endDay=None):

        reads = 0
        writes = 0

        for record in self.recordsList:
            if not supportLib.isDateInside(startDay=startDay, endDay=endDay, day=record.getDate()):
                continue
            reads += 1 if record.isRead() else 0
            writes += 1 if record.isWrite() else 0

        return {"reads" : reads, "writes" : writes}

    # . Time of day that contributes the most in file system traffic in hour classes (e.g. 11.00-13.00) 
    # returns a dictionary with key the starting hour and value the number of operations
    def timeOfDayTraffics(self, startDay=None, endDay=None):

        dayOperations_dict = {"0" : 0, "2" : 0, "4" : 0, "6" : 0, "8" : 0, "10" : 0,\
                              "12" : 0, "14" : 0, "16" : 0, "18" : 0, "20" : 0, "22" : 0}

        for record in self.recordsList:
            if not supportLib.isDateInside(startDay=startDay, endDay=endDay, day=record.getDate()):
                continue
            dayOperations_dict[supportLib.getClosestEvenHour(record.date)] = \
                dayOperations_dict.get(supportLib.getClosestEvenHour(record.date)) + 1\
                     if dayOperations_dict.get(supportLib.getClosestEvenHour(record.date))\
                          else 1

        return dayOperations_dict

    # . Size (in bytes) of read/write operations
    # returns 2 dictionaries of the two operations with keys the size and values the appearances
    def sizeOfReadWrite(self, startDay=None, endDay=None):

        readSizes = {}
        writeSizes = {}

        for record in self.recordsList:
            if not supportLib.isDateInside(startDay=startDay, endDay=endDay, day=record.getDate()):
                continue
            if record.isRead():
                bytes = record.numberOfBytes
                readSizes[bytes] = readSizes[bytes] + 1 if readSizes.get(bytes) else 1
            elif record.isWrite():
                bytes = record.numberOfBytes
                writeSizes[bytes] = writeSizes[bytes] + 1 if writeSizes.get(bytes) else 1

        return [dict(sorted(readSizes.items(), key=operator.itemgetter(1))), dict(sorted(writeSizes.items(), key=operator.itemgetter(1)))]
            

    # 2. Hot (used frequently) vs cold percentage of files.
    # returns map of file names and operations, in ascending order
    def hotVsColdFilesPercentage(self, startDay=None, endDay=None):
        
        filenameAccessesMap = {}

        for record in self.recordsList:
            if not supportLib.isDateInside(startDay=startDay, endDay=endDay, day=record.getDate()):
                continue
            fName = record.getFileName()
            if fName:
                filenameAccessesMap[fName] = filenameAccessesMap[fName] + 1 if filenameAccessesMap.get(fName) else 1

        return dict(sorted(filenameAccessesMap.items(), key=operator.itemgetter(1)))

    # 6. Average depth of file path.
    # returns the sum of file path and the count of files counted
    def avgDepthOfFPath(self, startDay=None, endDay=None):

        sumPathDepth = 0
        countPathDepth = 0

        for record in self.recordsList:
            if not supportLib.isDateInside(startDay=startDay, endDay=endDay, day=record.getDate()):
                continue
            fName = record.getFileName()
            if fName:
                sumPathDepth += fName.count("/")
                countPathDepth += 1

        return [sumPathDepth, countPathDepth]

    # 7. Number of file accesses during a day period.
    # returns map of file accesses and the date
    def numOfFileAccessInDay(self, startDay=None, endDay=None):
        
        dayMap = {}
        for record in self.recordsList:
            if not supportLib.isDateInside(startDay=startDay, endDay=endDay, day=record.getDate()):
                continue
            if record.isFileAccess():
                day = supportLib.getDay(record.date)
                entry = dayMap.get(day)
                if entry is None:
                    dayMap[day] = 1
                else:
                    dayMap[day] += 1
        return dayMap

    # 8. Percent of read only files. (e.g. never edited, only read for a time period)
    # returns list of read and writen files in two sets
    def percentOfReadOnlyFiles(self, startDay=None, endDay=None):

        # initializing set in python...
        editedFiles = {"dummy data"}
        editedFiles.remove("dummy data")
        unEditedFiles = {"dummy data"}
        unEditedFiles.remove("dummy data")

        for record in self.recordsList:
            if not supportLib.isDateInside(startDay=startDay, endDay=endDay, day=record.getDate()):
                continue
            if record.isEditFile():
                editedFiles.add(record.getFileName())
            else:
                fName = record.getFileName()
                if fName != None:
                    unEditedFiles.add(fName)

        unEditedFiles = unEditedFiles - editedFiles
        return [unEditedFiles, editedFiles]

    # Number of files replicated to cloud
    # returns number
    def numberOfFilesReplicatedToCloud(self, cloudNames, startDay=None, endDay=None):

        mapOfCloudNamesAndNumberOfFilesInCloud = {k : 0 for k in cloudNames}

        for record in self.recordsList:
            if not supportLib.isDateInside(startDay=startDay, endDay=endDay, day=record.getDate()):
                continue
            if record.getFileName():
                pathInList = record.getFileName().split('/',2)
                if len(pathInList) >= 2:
                    if pathInList[1] in cloudNames:
                        cloud = pathInList[1]
                        mapOfCloudNamesAndNumberOfFilesInCloud[cloud] = mapOfCloudNamesAndNumberOfFilesInCloud[cloud] + 1 if mapOfCloudNamesAndNumberOfFilesInCloud.get(cloud) else 1

        return mapOfCloudNamesAndNumberOfFilesInCloud

# merges 2 dictionaries, if one key exists in both 
# dictionaries, we add the values
def dictionary_merge(dictA, dictB):
    
    dict = {}

    for key, valueA in dictA.items():
        valueB = dictB.get(key)
        if valueB:
            dict[key] = valueA + valueB
            del dictB[key]
        else:
            dict[key] = valueA

    for key, value in dictB.items():
        dict[key] = value

    return dict

# merges 2 sets, if one key exists in both 
# sets, we only keep it at second (used for edited/unedited stat)
def set_merge(setA1, setA2, setB1 , setB2):
    
    set = {"dummy data"}

    setA1.update(setA2)
    setB1.update(setB2)
    setA1 = setA1 - setB1

    return [setA1, setB1]

def add_ints_for_median(sumA,sumB,countA,countB):
    return sumA+sumB, countA+countB

def printHotVsColdFilesPercentage(var_hotVsColdFilesPercentage, limitForHotVsCold, outDirectory="stats/"):
    lis = []
    {lis.append(v) for k, v in var_hotVsColdFilesPercentage.items() if v > limitForHotVsCold}
    hotFiles = len(lis)
    coldFiles = len(var_hotVsColdFilesPercentage) - hotFiles
    print("Hot Files: " + str(hotFiles) + "\nCold Files: " + str(coldFiles), file=open(outDirectory + "HotVsColdFilesPercentage", "w+"))
    print("Hot Percentage: " + str('%.3f' % (hotFiles*100.0/(hotFiles+coldFiles) if hotFiles > 0 or coldFiles > 0 else 0)) + " %"\
         + "\nCold Percentage: " + str('%.3f' % (coldFiles*100.0/(hotFiles+coldFiles) if hotFiles>0 or coldFiles > 0 else 0)) + " %", file=open(outDirectory + "HotVsColdFilesPercentage", "a"))

def printNumOfFileAccessInDay(var_numOfFileAccessInDay, startDay=None, endDay=None, outDirectory="stats/"):
    GreaterThanStartDaysDict = {}
    requestedDaysDict = {}
    if startDay:
        {GreaterThanStartDaysDict.update({day : accesses}) for day, accesses in var_numOfFileAccessInDay.items() if day >= startDay}
    else:
        GreaterThanStartDaysDict = var_numOfFileAccessInDay
    
    if endDay:
        {requestedDaysDict.update({day : accesses}) for day, accesses in GreaterThanStartDaysDict.items() if day <= endDay}
    else:
        requestedDaysDict = GreaterThanStartDaysDict

    print(file=open(outDirectory + "NumOfFileAccessInDay", "w+"))
    for day, accesses in requestedDaysDict.items():
        print("On " + day + " happened " + str(accesses) + " file accesses.", file=open(outDirectory + "NumOfFileAccessInDay", "w+"))

def printPercentOfReadOnlyFiles(var_percentOfReadOnlyFiles, outDirectory="stats/"):
    print("Read only file percentage: " + str('%.3f' % (len(var_percentOfReadOnlyFiles[0])/(len(var_percentOfReadOnlyFiles[1]) if len(var_percentOfReadOnlyFiles[1]) > 0 else 1  + len(var_percentOfReadOnlyFiles[0]) if len(var_percentOfReadOnlyFiles[0]) > 0 else 1))), file=open(outDirectory + "PercentOfReadOnlyFiles", "w+"))

def printAvgDepthOfFPath(l, outDirectory="stats/"):
    sum = l[0]
    count = l[1]
    if(count > 0):
        print("Average depth of file paths is " + str('%0.3f' % (sum/count)), file=open(outDirectory + "AvgDepthOfFPath", "w+"))
    else:
        print("Average depth of file paths is 0", file=open(outDirectory + "AvgDepthOfFPath", "w+"))

def printFileUsage(readsWritesDict, outDirectory="stats/"):
    print("Number of reads: " + str(readsWritesDict["reads"]) + "\nNumber of writes: " + str(readsWritesDict["writes"]), file=open(outDirectory + "FileUsage", "w+"))

def printSizeOfReadWrite(var_sizeOfReadWrite, outDirectory="stats/"):
    print("File Size \t Bytes Read", file=open(outDirectory + "SizeOfReadWrite", "w+"))
    for fileSize, readSize in var_sizeOfReadWrite[0].items():
        print(str(fileSize) + " \t " + str(readSize), file=open(outDirectory + "SizeOfReadWrite", "a"))

def printTimeOfDayTraffics(var_timeOfDayTraffics, outDirectory="stats/"):
    # for printing purposes
    for time, num in var_timeOfDayTraffics.items():
        if time in ["2", "4", "6", "8"]:
            var_timeOfDayTraffics["0"+time] = var_timeOfDayTraffics[time]
            del var_timeOfDayTraffics[time]

    print(file=open(outDirectory + "TimeOfDayTraffics", "w+"))
    for time, num in sorted(var_timeOfDayTraffics.items()):
        print("In time " + time + "-" + str(int(time)+2) + ", there were " + str(num) + " operations.", file=open(outDirectory + "TimeOfDayTraffics", "a"))

def printNumberOfFilesReplicatedToCloud(var_numberOfFilesReplicatedToCloud, outDirectory="stats/"):
    print("Number of files replicated to cloud:", file=open(outDirectory + "NumberOfFilesReplicatedToCloud", "w+"))
    for cloudName, number in var_numberOfFilesReplicatedToCloud.items():
        print("\tCloud Name = " + cloudName + ", number of files = " + str(number), file=open(outDirectory + "NumberOfFilesReplicatedToCloud", "a"))    

if __name__ == "__main__":
    configuration = supportLib.parseConfigurationFile('statsconfig.json')
    startDay = configuration["startDay"]
    endDay = configuration["endDay"]
    directory = configuration["directory"]
    outputFolder = configuration["outFolder"]
    HotVsColdFilesPercentageLimit = configuration["HotVsColdFilesPercentage"]["limit"]
    cloudNames = configuration["cloudNames"]
    if not os.path.isdir(outputFolder):
        os.makedirs(outputFolder)

    var = statsCalculator()

    var_hotVsColdFilesPercentage = {}
    var_numOfFileAccessInDay = {}
    
    # initilize a set..
    set1 = {"dummy"}
    set2 = {"dummy"}
    set1.remove("dummy")
    set2.remove("dummy")
    var_percentOfReadOnlyFiles = [set1, set2]     # list of 2 sets
    
    var_avgDepthOfFPath = [0,0]
    var_fileUsage = {}
    var_sizeOfReadWrite = [{}, {}]    # list of 2 dictionaries
    var_timeOfDayTraffics = {}
    var_numberOfFilesReplicatedToCloud = {}

    directory = configuration["directory"]
    
    # calculate forearch file
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            var.parseLogFile(directory+filename)
            
            #
            var_hotVsColdFilesPercentage = dictionary_merge(var_hotVsColdFilesPercentage, var.hotVsColdFilesPercentage(startDay=startDay, endDay=endDay))
            ##############

            #
            var_numOfFileAccessInDay = dictionary_merge(var_numOfFileAccessInDay,var.numOfFileAccessInDay(startDay=startDay, endDay=endDay))
            ##############

            #
            porof = var.percentOfReadOnlyFiles(startDay=startDay, endDay=endDay)
            var_percentOfReadOnlyFiles = set_merge(var_percentOfReadOnlyFiles[0]\
                ,porof[0]\
                ,var_percentOfReadOnlyFiles[1]\
                ,porof[1])
            ##############

            #
            adop = var.avgDepthOfFPath(startDay=startDay, endDay=endDay)
            var_avgDepthOfFPath = add_ints_for_median(var_avgDepthOfFPath[0]\
                ,adop[0]\
                ,var_avgDepthOfFPath[1]\
                ,adop[1])
            ##############

            #
            var_fileUsage = dictionary_merge(var_fileUsage,var.fileUsage(startDay=startDay, endDay=endDay))
            ##############
            
            #
            sorw = var.sizeOfReadWrite(startDay=startDay, endDay=endDay)
            var_sizeOfReadWrite[0] = dictionary_merge(var_sizeOfReadWrite[0], sorw[0])
            var_sizeOfReadWrite[1] = dictionary_merge(var_sizeOfReadWrite[1], sorw[1])
            ##############
            
            #
            var_timeOfDayTraffics = dictionary_merge(var_timeOfDayTraffics,var.timeOfDayTraffics(startDay=startDay, endDay=endDay))
            ##############

            #
            var_numberOfFilesReplicatedToCloud = dictionary_merge(var_numberOfFilesReplicatedToCloud, var.numberOfFilesReplicatedToCloud(cloudNames=cloudNames, startDay=startDay, endDay=endDay))
            ##############

    printHotVsColdFilesPercentage(var_hotVsColdFilesPercentage, 2)
    printNumOfFileAccessInDay(var_numOfFileAccessInDay, startDay=startDay, endDay=endDay)
    printPercentOfReadOnlyFiles(var_percentOfReadOnlyFiles)
    printAvgDepthOfFPath(var_avgDepthOfFPath)
    printFileUsage(var_fileUsage)
    printSizeOfReadWrite(var_sizeOfReadWrite)
    printTimeOfDayTraffics(var_timeOfDayTraffics)
    printNumberOfFilesReplicatedToCloud(var_numberOfFilesReplicatedToCloud)
    
