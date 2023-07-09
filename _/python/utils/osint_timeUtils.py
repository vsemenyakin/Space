import datetime 

def parseTime_tryParseWithDelimiter(string, delimiter):

  members = string.split(delimiter)

  membersNum = len(members)  
  if membersNum <= 1:
     return None
  elif membersNum <= 3:
    try: # Catch "float" from "strings" casting problems 
      members.reverse()
       
      resultTime = datetime.timedelta(\
        seconds = float(members[0]),\
        minutes = float(members[1]),\
        hours = float(members[2]) if membersNum == 3 else 0)
        
      return resultTime
        
    except:      
      pass


def parseTime(string):

  # Special case for seconds single value

  try:
    seconds__float = float(string)
    return datetime.timedelta(seconds = seconds__float)
  except:
    # No return here - because this may be other format
    pass

  # Parse using time patterns  
  result = parseTime_tryParseWithDelimiter(string, ":")
  if result != None:
    return result
  
  result = parseTime_tryParseWithDelimiter(string, "_")
  
  return result  

def timeDeltaToString(timeDelta, timeFormat = None):
  if timeFormat == None:
    return str(math.floor(timeDelta.total_seconds()))

  timeFromZero = datetime.datetime.min + timeDelta
  
  if timeFormat[-2:] == "%f":
    # Trim last three symbols for miliseconds
    return timeFromZero.strftime(timeFormat)[:-3]
  else:
    return timeFromZero.strftime(timeFormat)

