import json

"""
    Date retrieval supporting functions
"""
"Convert date time from audit framework format, to python format"
def auditToPythonTime(date):
    day = date[0:2]
    month = date[3:5]
    year = date[6:10]

    return year + '-' + month + '-' + day + date[10:]

"Check if 2 given python timedates are in the same day"
def getDay(time):
    return time[:10]

"Returns hour in 24h format"
def getHour(date):
    return date[10:12]

"Returns minutes"
def getMinute(date):
    return date[13:15]

"Returns seconds"
def getSecond(date):
    return date[16:18]

"Returns closest even hour to given date"
def getClosestEvenHour(date):
    time = int(getHour(date)) + float(getMinute(date))/60 + float(getSecond(date))/3600
    l = ["0", "2", "4", "6", "8", "10", "12", "14", "16", "18", "20", "22", "24"]
    m = min(l, key=lambda x:abs(float(x)-time))
    return m if m != "24" else "0"

"Json configuration parser"
"Returns dictionary"
def parseConfigurationFile(fileName):
    json_file = open(fileName)
    json_string = json_file.read()
    json_data = json.loads(json_string)
    return json_data


"Takes 3 days(in yyy-mm-dd format) and returns if the 3rd is inside the first two"
def isDateInside(startDay, endDay, day):
    if startDay:
        if endDay:
            return day >= startDay and day <= endDay
        else:
            return day >= startDay
    else:
        if endDay:
            return day <= endDay
        else:
            return True