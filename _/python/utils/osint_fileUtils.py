import os
import shutil
from enum import Enum

import osint_pathUtils

from osint_stringUtils import findMatchedSubstring

#For isLink
import pylnk3

# -------------------------------------

def mkDirSafe(dir__path):
  try:
    os.mkdir(dir__path)
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
  except Exception as exception:
    return False
  
def rmFileSafe(dir__path):
  try:
    shutil.remove(dir__path)
    return True
  except:
    return False

# -------------------------------------

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
    rmFileSafe(file__path)
  
    possibleResult = open(file__path, "tw", encoding = encodings)
    return possibleResult
  
  except Exception as exception:
    return None

# ------------------------------

class ListDir_SortRule(Enum):
  DontSort = 0
  Lexicographic = 1
  FirstNumberThenLexicographic = 2

#NB: If files are started from number - 
def listDir(dir__path,\
  sortRule = ListDir_SortRule.FirstNumberThenLexicographic,\
  returnPaths = True):

  result = os.listdir(dir__path)

  if sortRule == ListDir_SortRule.DontSort:
    pass
  elif sortRule == ListDir_SortRule.Lexicographic:
    result = sorted(result)
  elif sortRule == ListDir_SortRule.FirstNumberThenLexicographic:

    pathAndNumbers = []
    otherPathsWithoutNumbers = []

    for resultElement in result:
      numberInName = osint_pathUtils.getIntNumbersFromFSItemName(resultElement)
      if numberInName != None:
        pathAndNumbers.append((numberInName, resultElement))
      else:
        otherPathsWithoutNumbers.append(resultElement)
  
    #Sorting by first tuple element. Based on [https://learnpython.com/blog/sort-tuples-in-python/]
    result = [pathAndNumber[1] for pathAndNumber in sorted(pathAndNumbers)]
    result.extend(sorted(otherPathsWithoutNumbers))

  else:
    #ERROR: Unknown sort rule passed
    return None

  if returnPaths:
    result = [os.path.join(dir__path, resultElement) for resultElement in result]

  return result
  
# ------------------------------

def getLinkPath(path):

  try:
    lnk = pylnk3.Lnk(path)
    return lnk.path
  
  except Exception as exception:
    return None

def isLink(path):
  #Based on [https://github.com/strayge/pylnk]
  
  try:
    lnk = pylnk3.Lnk(path)
    return True
    
  except Exception as exception:
    print(exception)
    return False

# ------------------------------

def findDirMember(dir__path, possibleNames, matchCase = False, returnPath = True):

  for fsItem__dir_item__name in listDir(dir__path, ListDir_SortRule.DontSort, returnPaths = False):
    if findMatchedSubstring(fsItem__dir_item__name, possibleNames):
      return os.path.join(dir__path, fsItem__dir_item__name) if returnPath else fsItem__dir_item__name

  return None
