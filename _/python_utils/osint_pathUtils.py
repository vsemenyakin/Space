
import os

def getFSItemName(fsItem__path, withExtension = True):

  fsItemName = os.path.basename(fsItem__path)
  
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
