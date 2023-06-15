import datetime 

def parseTime(string):

  # Special case for seconds single value

  try:
    seconds__int = int(string)
    return datetime.timedelta(seconds = seconds__int)
  except:
    # No return here - because this may be other format
    pass

  # Parse using time patterns
  members = string.split(":")
  
  membersNum = len(members)  
  if membersNum <= 1:
     return None
  elif membersNum <= 3:
    try: # Catch int casting problems 
      members.reverse()
       
      return datetime.timedelta(\
        seconds = int(members[0]),\
        minutes = int(members[1]),\
        hours = int(members[2]) if membersNum == 3 else 0)
    except:      
      pass  
  
  return None    


def timeDeltaToString(timeDelta, timeFormat = None):
  if timeFormat == None:
    return str(math.floor(timeDelta.total_seconds()))

  timeFromZero = datetime.datetime.min + timeDelta
  return timeFromZero.strftime(timeFormat)

