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
    hour = int(getHour(date))
    if hour <= 2:
        return "2"
    elif hour <= 4:
        return "4"
    elif hour <= 6:
        return "6"
    elif hour <= 8:
        return "8"
    elif hour <= 10:
        return "10"
    elif hour <= 12:
        return "12"
    elif hour <= 14:
        return "14"
    elif hour <= 16:
        return "16"
    elif hour <= 18:
        return "18"
    elif hour <= 20:
        return "20"
    elif hour <= 22:
        return "22"
    elif hour <= 24:
        return "24"

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