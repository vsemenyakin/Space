
import os
import re #for getNumberFromFSItemName

def getFSItemName(fsItem__path, withExtension = True):

  fsItemName = os.path.basename(fsItem__path)
  
  if os.path.isdir(fsItem__path):
    # We assume that dirs have no "extension"
    return fsItemName
  
  if withExtension:
    return fsItemName

  return os.path.splitext(fsItemName)[0]


def getFileNameWithoutExtension(file_in_path):
  return os.path.basename(file_in_path).split('.')[0]

def getPathFromWhichProcessIsCalled():
  return os.getcwd()

def getPathWithoutLastMember(fsItem__path):
  return os.path.split(fsItem__path)[0]

def splitPathAndLastMember(fsItem__path):
  pathElements = os.path.split(fsItem__path)
  return (pathElements[0], pathElements[1])

def getIntNumbersFromFSItemName(fsItem_name):
  
  #Based on [https://stackoverflow.com/a/4289348]
  
  try:
    numbers = re.findall(r'\d+', fsItem_name)

    if numbers == None or len(numbers) == 0:
      return None
    
    return int(numbers[0])

  except:
    return None
