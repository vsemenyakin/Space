import os

def openTextFileForRead(file__path):
  
  supportedEncodings = ["utf8"]
  
  for supportedEncoding in supportedEncodings:
    try:
      possibleResult = open(file__path, "tr", encoding = supportedEncoding)
      
      #Current we need to make reading attemp to catch failure
      # if file is not text and so cannot be read.
      #TODO: Find how to optimize this potentialy slow operation
      possibleResult.readline()
      possibleResult.seek(0)
      
      return possibleResult
    except Exception as exception:
      pass

  return None

def isTextFile(file__path):
  return not openTextFileForRead(file__path) == None

# - - - - - - - - - - - - - - - - - -

def openTextFileForWrite(file__path):
  
  encodings = "utf8"
  
  try:
    possibleResult = open(file__path, "tw", encoding = encodings)
    return possibleResult
  
  except Exception as exception:
    return None

# -------------------------------------
    
def mkDirSafe(dir__path):
  try:
    os.mkdir(dir__path, exist_ok = True)
    return True
  except:
    return False

def mkDirsSafe(dir__path):
  try:
    os.makedirs(dir__path, exist_ok = True)
    return True
  except:
    return False

def rmDirSafe(dir__path):
  try:
    shutil.rmtree(dir__path)
    return True
  except:
    return False
  
def rmFileSafe(dir__path):
  try:
    shutil.remove(dir__path)
    return True
  except:
    return False
  