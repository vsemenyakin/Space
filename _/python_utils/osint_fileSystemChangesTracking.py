import os
from enum import Enum
import hashlib

from osint_fileUtils import openTextFileForRead
from osint_fileUtils import mkDirsSafe
from osint_fileUtils import rmFileSafe

from osint_pathUtils import getFSItemName
from osint_pathUtils import splitPathAndLastMember

class FSMetaConst:
  metaFileName = "meta.txt"
  
  #Parsing
  propertyDelimiter = ":"
  nestingOffset = "  "

  heading_rootDir = "[RootDirectory]"
  heading_dir = "[Directory]"
  heading_file = "[File]"

class EFSMetaItemStatus(Enum):
  Actual = 1
  Added = 2
  Changed = 3
  Removed = 4

def fsMeta_computeFileHash(file__path):
  file__fileObject = open(file__path, 'rb')

  return hashlib.md5(file__fileObject.read()).hexdigest()

def makeOffsetString(offset):
  result = ""
  
  for unused in range(offset):
    result = FSMetaConst.nestingOffset + result

  return result

# - - - - - - - -  - - 

class FSMeta_fsItem:

  propertyName_name = "name"

  def __init__(self, name, fsMetaDirectory, status):
    self.name = name
    self.fsMetaDirectory = fsMetaDirectory
    
    self.status = status

  def getName(self):
    return self.name

  def getPath(self):
    return os.path.join(self.getParentPath(), self.getName())
    
  def getParentPath(self): #return exptected: path
    raise NotImplementedError()

  def getParentFSMetaDir(self): #return exptected: FSMeta_dir_base
    raise NotImplementedError()

  def propertiesToString(self):
    raise NotImplementedError()
  
  def getStatus():
    raise NotImplementedError()

  def actualize(self):
    raise NotImplementedError()

# === FILE

class FSMeta_file(FSMeta_fsItem):

  propertyName_hashValue = "hashValue"

  def __init__(self, name, hashValue, fsMetaDirectory, status = None):
    super().__init__(name, fsMetaDirectory, status)
    self.hashValue = hashValue
    
    self.fsMetaDirectory = fsMetaDirectory

  def getParentPath(self):  
    return self.fsMetaDirectory.getPath()
    
  def getParentFSMetaDir(self):
    return self.fsMetaDirectory

  def propertiesToString(self):
    return "[File| Name: {name} , Hash: {hashValue}]".format(\
      name = self.name,
      hashValue = self.hashValue)

  def computeStatusIfNeed(self):
    if self.status != None:
      return

    path = self.getPath();
    
    if not os.path.exists(path):
      self.status = EFSMetaItemStatus.Removed
      return
    
    actualHashValue = fsMeta_computeFileHash(path)    
    if self.hashValue != actualHashValue:
      self.status = EFSMetaItemStatus.Changed
      return
      
    self.status = EFSMetaItemStatus.Actual

  def getStatus(self):
    self.computeStatusIfNeed()
  
    return self.status    

  def actualize(self):
    status = self.getStatus();
    
    if status == EFSMetaItemStatus.Actual:
      #Nothing should be done here
      return True
    
    if status == EFSMetaItemStatus.Changed:
      self.hashValue = fsMeta_computeFileHash(path)
      self.status = EFSMetaItemStatus.Actual
      return True
    
    elif status == EFSMetaItemStatus.Removed:
      self.fsMetaDirectory.remove(self)
      self.status = EFSMetaItemStatus.Actual
      return True
    
    elif status == EFSMetaItemStatus.Added:
      # In current implementation correct hash
      # and parent fsDir should be passed
      # during construction - so no additional
      # actions should be performed
      self.status = EFSMetaItemStatus.Actual
      return True
    
    else:
      #ERROR: Unknown status
      return False

# === DIRECTORY

class FSMeta_dir_base(FSMeta_fsItem):

  def __init__(self, name, fsMetaDirectory, status):
    super().__init__(name, fsMetaDirectory, status)
  
    self.items = []  
  
  #NOTE: "self.status" has not final status value for FSMeta_dir
  
  def computeStatusIfNeed(self):    
    
    if self.status != None:
      return
  
    if not os.path.exists(self.getPath()):
      self.status = EFSMetaItemStatus.Removed
      return
    
    self.status = EFSMetaItemStatus.Actual
    
  
  def getStatus(self):
    self.computeStatusIfNeed()
  
    if self.status != EFSMetaItemStatus.Actual:
      return self.status
    
    for item in self.items:
      if item.getStatus() != EFSMetaItemStatus.Actual:
        return EFSMetaItemStatus.Changed
    
    return EFSMetaItemStatus.Actual
  
  def actualize(self):
    status = self.getStatus();
    
    if status == EFSMetaItemStatus.Actual:
      #Nothing should be done here
      return True
    
    if status == EFSMetaItemStatus.Changed:
      # Change status is based on members for dirs
      # so it cannot be fixed by actualize call
      return False

    elif status == EFSMetaItemStatus.Removed:
      if self.fsMetaDirectory != None:
        self.fsMetaDirectory.remove(self)
        return True
      else:
        # No fsMetaDirectory may be for directory
        # We don't need to change status for this case
        return True
    
    elif status == EFSMetaItemStatus.Added:
      
      for item in self.items:
        item.actualize()
      
      # Item was added - so it currently has actual status
      self.status = EFSMetaItemStatus.Actual
      return True
    
    else:
      return False #ERROR: Unknown status
  
  # - - - Private methods  
  def addItem(self, fsItem):
    self.items.append(fsItem)

class FSMeta_dir_root(FSMeta_dir_base):

  propertyName_osRootPath = "osRootPath"

  def __init__(self, name, osRootPath, status = None):
    super().__init__(name, None, status)
  
    self.osRootPath = osRootPath
        
  def getParentPath(self):
    return self.osRootPath

  def getParentFSMetaDir(self):
    return None
    
  def propertiesToString(self):
    return "[Root dir| Name: {name} , OS root path: {osRootPath}]".format(\
      name = self.name,
      osRootPath = self.osRootPath)

class FSMeta_dir(FSMeta_dir_base):

  def __init__(self, name, fsMetaDirectory, status = None):
    super().__init__(name, fsMetaDirectory, status)
    
    self.fsMetaDirectory = fsMetaDirectory

  def getParentPath(self):  
    return self.fsMetaDirectory.getPath()
    
  def getParentFSMetaDir(self):
    return self.fsMetaDirectory

  def propertiesToString(self):
    return "[Dir| Name: {name}]".format(\
      name = self.name)

# =================================================

#TODO: Add debug checking for FS changes:
# - Actual FS should be not changed after forming FS Meta

class FSMeta:

  # - - - - Private API - - - - - 
  
  # Use "makeMeta()", "saveMeta()" and "loadMeta()" instead direct call
  def __init__(self, rootDirs):
    self.rootDirs = rootDirs #FSMeta_dir_root[]

  def isActual(self):
    for rootDir in self.rootDirs:
      if rootDir.getStatus() != EFSMetaItemStatus.Actual:
        return False
        
    return True
  
  # ----------------- Printing
  
  def debugPrint_dir(fsDir, offset):

    print("{offsetString}[dir] {name} | {status}".format(\
      offsetString = makeOffsetString(offset),\
      name = fsDir.getName(),\
      status = fsDir.getStatus()))
      
    for item in fsDir.items:
      if isinstance(item, FSMeta_dir_base):
        FSMeta.debugPrint_dir(item, offset + 1)
      elif isinstance(item, FSMeta_file):
        FSMeta.debugPrint_file(item, offset + 1)
        
  def debugPrint_file(fsFile, offset):

    print("{offsetString}[file] {name} | {status}".format(\
      offsetString = makeOffsetString(offset),\
      name = fsFile.getName(),\
      status = fsFile.getStatus()))
    
  def debugPrint(self):
  
    print("--- FS Meta ---")
    print("{")
  
    for rootDir in self.rootDirs:
      FSMeta.debugPrint_dir(rootDir, 0)
    
    print("}")

# ========================================= Make meta =========================================
# - - - - - - - - - - - - - - - - - - - - Private API - - - - - - - - - - - - - - - - - - - -

def makeMeta_createFile(file__path, fsMetaDirectory):

  if not os.path.exists(file__path):
    #ERROR: Cannot find directory to register
    return None

  name = getFSItemName(file__path)
  hashValue = fsMeta_computeFileHash(file__path)
    
  return FSMeta_file(name, hashValue, fsMetaDirectory, EFSMetaItemStatus.Actual)
  

def makeMeta_createDirectory(dir__path, fsMetaDirectory):
  
  if not os.path.exists(dir__path):
    #ERROR: Cannot find directory to register
    return False

  name = getFSItemName(dir__path)
  
  directory = FSMeta_dir(name, fsMetaDirectory, EFSMetaItemStatus.Actual)

  for fsItem__dir_member__name in os.listdir(dir__path):

    containedItem = None
  
    fsItem__dir_member__path = os.path.join(dir__path, fsItem__dir_member__name)  
    if os.path.isdir(fsItem__dir_member__path):
      containedItem = makeMeta_createDirectory(fsItem__dir_member__path, directory)
    else:
      containedItem = makeMeta_createFile(fsItem__dir_member__path, directory)
  
    directory.addItem(containedItem)
  
  return directory

def makeMeta_createRootDirectory(dir__path):
  
  if not os.path.exists(dir__path):
    #ERROR: Cannot find directory to register
    return False
      
  (osRootPath, name) = splitPathAndLastMember(dir__path)
  
  rootDir = FSMeta_dir_root(name, osRootPath, EFSMetaItemStatus.Actual)

  for fsItem__dir_member__name in os.listdir(dir__path):
  
    containedItem = None

    fsItem__dir_member__path = os.path.join(dir__path, fsItem__dir_member__name)    
        
    if os.path.isdir(fsItem__dir_member__path):
      containedItem = makeMeta_createDirectory(fsItem__dir_member__path, rootDir)
    else:
      containedItem = makeMeta_createFile(fsItem__dir_member__path, rootDir)
        
    rootDir.addItem(containedItem)
  
  return rootDir

# - - - - - - - - - - - - - - - - - - - - Public API - - - - - - - - - - - - - - - - - - - -

def makeFSMeta(dir__root__paths):

  fsRootDirs = []

  for dir__root__path in dir__root__paths:
    fsRootDir = makeMeta_createRootDirectory(dir__root__path)
    if fsRootDir == None:
      #If something went wrong
      continue

    fsRootDirs.append(fsRootDir)

  return FSMeta(fsRootDirs)


# ========================================= Save meta =========================================
# - - - - - - - - - - - - - - - - - - - - Private API - - - - - - - - - - - - - - - - - - - -

def saveMeta_writeWhiteline(file__fileObject):
  file__fileObject.write("\n")

def saveMeta_writeLineWithOffset(file__fileObject, offset, string):

  lineToWrite = "{offsetString}{string}\n".format(\
     offsetString = makeOffsetString(offset),\
     string = string)

  file__fileObject.write(lineToWrite)

def saveMeta_writeProperty(file__fileObject, offset, name, value):

  stringToWrite = "{name}{delimiter} {value}".format(\
     name = name,
     delimiter = FSMetaConst.propertyDelimiter,
     value = value)

  saveMeta_writeLineWithOffset(file__fileObject, offset, stringToWrite)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def saveMeta_file(file__fileObject, offset, fsFile):

  saveMeta_writeLineWithOffset(file__fileObject, offset, FSMetaConst.heading_file)
  saveMeta_writeProperty(file__fileObject, offset, FSMeta_file.propertyName_name, fsFile.name)
  saveMeta_writeProperty(file__fileObject, offset, FSMeta_file.propertyName_hashValue, fsFile.hashValue)
  saveMeta_writeWhiteline(file__fileObject)

def saveMeta_dir(file__fileObject, offset, fsDir):

  saveMeta_writeLineWithOffset(file__fileObject, offset, FSMetaConst.heading_dir)
  saveMeta_writeProperty(file__fileObject, offset, FSMeta_dir.propertyName_name, fsDir.name)
  saveMeta_writeWhiteline(file__fileObject)
  
  itemsOffset = offset + 1

  for item in fsDir.items:
  
    if isinstance(item, FSMeta_file):
      saveMeta_file(file__fileObject, itemsOffset, item)
  
    elif isinstance(item, FSMeta_dir):
      saveMeta_dir(file__fileObject, itemsOffset, item)  
  
    else:
      #ERROR: Unknown item
      continue

def saveMeta_rootDir(file__fileObject, fsRootDir):
  
  rootOffset = 0
  
  saveMeta_writeLineWithOffset(file__fileObject, rootOffset, FSMetaConst.heading_rootDir)
  saveMeta_writeProperty(file__fileObject, rootOffset, FSMeta_dir_root.propertyName_name, fsRootDir.name)
  saveMeta_writeProperty(file__fileObject, rootOffset, FSMeta_dir_root.propertyName_osRootPath, fsRootDir.osRootPath)
  saveMeta_writeWhiteline(file__fileObject)
  
  itemsOffset = rootOffset + 1  

  for item in fsRootDir.items:
        
    if isinstance(item, FSMeta_file):
      saveMeta_file(file__fileObject, itemsOffset, item)
  
    elif isinstance(item, FSMeta_dir):
      saveMeta_dir(file__fileObject, itemsOffset, item)  
  
    else:    
      #ERROR: Unknown item
      continue

# -------------------------------------------------------------------------------------------

def removeFSMeta(dir__metaToRemove__path):

  file__metaToRemove__path = os.path.join(dir__metaToRemove__path, FSMetaConst.metaFileName)
  rmFileSafe(file__metaToRemove__path)

def saveFSMeta(dir__metaToSave__path, fsMeta):

  if not fsMeta.isActual():
    print("ERROR: Trying to save no actualized meta. Currenly it is not allowed")
    return False

  #Remove meta if exist
  removeFSMeta(dir__metaToSave__path)
    
  mkDirsSafe(dir__metaToSave__path)
  
  file__metaToSave__path = os.path.join(dir__metaToSave__path, FSMetaConst.metaFileName)  
  metaToSave__fileObject = open(file__metaToSave__path, 'w' , encoding = "utf-8")
  
  for fsMeta.rootDir in fsMeta.rootDirs:
    saveMeta_rootDir(metaToSave__fileObject, fsMeta.rootDir) 

  return True

# ========================================= Load meta =========================================

# - - - - - - - - - - - - - - - - - - - - Public API - - - - - - - - - - - - - - - - - - - -

def readOffsetFromString(string):

  offset = 0
  
  length = len(string)
  nestingOffsetLength = len(FSMetaConst.nestingOffset)
  
  currentIndex = 0    
  
  while currentIndex < length:
    substringIndex = string.find(FSMetaConst.nestingOffset, currentIndex)
    
    # Second condition - for checking if line is NOT at the begginning of the string
    if substringIndex == -1 or (substringIndex != currentIndex):
      break
    
    currentIndex = substringIndex + nestingOffsetLength
    offset += 1
  
  return offset

def srtingWithoutOffsetAndOffset(string):
  nestingOffsetLength = len(FSMetaConst.nestingOffset)

  offset = readOffsetFromString(string)
  return (offset, string[offset * nestingOffsetLength:].strip())

def loadFSMeta_property(metaToLoad__fileObject, expectedOffset, expectedName):

  string = metaToLoad__fileObject.readline()

  offset = readOffsetFromString(string)
  if offset != expectedOffset:
    #ERROR: Unexpected offset
    return None

  nestingOffsetLength = len(FSMetaConst.nestingOffset)
  string = string[offset * nestingOffsetLength:]
  members = string.split(FSMetaConst.propertyDelimiter, 1)

  if len(members) != 2:
    #ERROR: Unexpected line format
    return None  

  if members[0].strip() != expectedName:
    #ERROR: Unexpected property name
    return None

  propertyValue = members[1].strip()
  return propertyValue

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def loadFSMeta_parseFile(metaToLoad__fileObject, expectedOffset, fsMetaDirectory):
  
  name = loadFSMeta_property(metaToLoad__fileObject, expectedOffset, FSMeta_file.propertyName_name)
  if name == None:
    return None
  
  hashValue = loadFSMeta_property(metaToLoad__fileObject, expectedOffset, FSMeta_file.propertyName_hashValue)
  if hashValue == None:
    return None

  return FSMeta_file(name, hashValue, fsMetaDirectory)
  
def loadFSMeta_parseDir(metaToLoad__fileObject, expectedOffset, fsMetaDirectory):

  name = loadFSMeta_property(metaToLoad__fileObject, expectedOffset, FSMeta_dir.propertyName_name)
  if name == None:
    return None
  
  return FSMeta_dir(name, fsMetaDirectory)

def loadFSMeta_parseRootDir(metaToLoad__fileObject, expectedOffset):

  name = loadFSMeta_property(metaToLoad__fileObject, expectedOffset, FSMeta_dir_root.propertyName_name)
  if name == None:
    return None

  osRootPath = loadFSMeta_property(metaToLoad__fileObject, expectedOffset, FSMeta_dir_root.propertyName_osRootPath)
  if osRootPath == None:
    return None

  return FSMeta_dir_root(name, osRootPath)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#FILE
#fsFile.name
#fsFile.hashValue

#DIR
#fsDir.name

def loadFSMeta_registerAdded_file(name, fsMetaDirectory):

  path = os.path.join(fsMetaDirectory.getPath(), name)
  hashValue = fsMeta_computeFileHash(path)

  return FSMeta_file(name, hashValue, fsMetaDirectory, EFSMetaItemStatus.Added)
  
def loadFSMeta_registerAdded_dir(name, fsMetaDirectory):

  newDir = FSMeta_dir(name, fsMetaDirectory, EFSMetaItemStatus.Added)

  path = os.path.join(fsMetaDirectory.getPath(), name)
  for fsItem__dirMember__name in os.listdir(path):
  
    fsItem__dirMember__path = os.path.join(path, fsItem__dirMember__name)
    fsItemIsFile = os.path.isfile(fsItem__dirMember__path)

    addedItem = None
    if fsItemIsFile:
      addedItem = loadFSMeta_registerAdded_file(fsItem__dirMember__name, newDir)
    else:
      addedItem = loadFSMeta_registerAdded_dir(fsItem__dirMember__name, newDir)

    newDir.addItem(addedItem)

  return newDir

# - - - - - - - - - - - - - - - - - - - - Public API - - - - - - - - - - - - - - - - - - - -

def existsFSMeta(dir__metaToLoad__path):

  file__metaToLoad__path = os.path.join(dir__metaToLoad__path, FSMetaConst.metaFileName)
  return os.path.exists(file__metaToLoad__path)

# [dir__meta__path] - place where meta files are stored
def loadFSMeta(dir__metaToLoad__path):

  if not existsFSMeta(dir__metaToLoad__path):
    #ERROR: Cannot find meta file
    return None

  file__metaToLoad__path = os.path.join(dir__metaToLoad__path, FSMetaConst.metaFileName)
  metaToLoad__fileObject = open(file__metaToLoad__path, 'r' , encoding = "utf-8")

  rootDirs = []
  
  formingDirsStack = []
  currentDir = None

  # --- Load data ---

  for line in metaToLoad__fileObject:
    if line.isspace():
      continue
  
    (offset, string) = srtingWithoutOffsetAndOffset(line)

    # Correct current dirs stack
    if offset == 0:
      if string != FSMetaConst.heading_rootDir:
        print("ERROR: Invalid fsMeta format: File cannot be passed with root offset")
        return None
    else:    
      if offset > len(formingDirsStack):
        print("ERROR: Invalid fsMeta format: File with offset more then current directory")
        return None
      
      if offset < len(formingDirsStack):
        formingDirsStack = formingDirsStack[:offset]
        currentDir = formingDirsStack[-1]

    # Parse arguments
    if string == FSMetaConst.heading_file:      
    
      #FORM STATUS INFO!
      newFile = loadFSMeta_parseFile(metaToLoad__fileObject, offset, currentDir)
      if newFile == None:
        print("ERROR: Error during parsing")
        return None
    
      currentDir.addItem(newFile)
    
    elif string == FSMetaConst.heading_dir:

      #FORM STATUS INFO!
      newDir = loadFSMeta_parseDir(metaToLoad__fileObject, offset, currentDir)
      if newDir == None:
        print("ERROR: Error during parsing")
        return None     

      currentDir.addItem(newDir)
      
      currentDir = newDir      
      formingDirsStack.append(newDir)
            
    elif string == FSMetaConst.heading_rootDir:
        
      if offset != 0:
        print("ERROR: Invalid fsMeta format: root with non-zero offset")
        return None
    
      newRootDir = loadFSMeta_parseRootDir(metaToLoad__fileObject, offset)
      if newRootDir == None:
        print("ERROR: Error during parsing")
        return None

      currentDir = newRootDir
      formingDirsStack = [ newRootDir ]
      
      rootDirs.append(newRootDir)

  # --- Append added items (and make removed status for root dirs)
  
  #for line in metaToSave__fileObject: 
 
  for rootDir in rootDirs:
    
    rootDirPath = rootDir.getPath()
  
    if not os.path.exists(rootDirPath):
      rootDir.status = EFSMetaItemStatus.Removed
      continue
  
    for fsItem__rootDirMember__name in os.listdir(rootDirPath):
      
      fsItem__rootDirMember__path = os.path.join(rootDirPath, fsItem__rootDirMember__name)
      
      if not os.path.exists(fsItem__rootDirMember__path):
        # It's possible that member is not exist. It will have Removed status
        continue
      
      fsItemIsFile = os.path.isfile(fsItem__rootDirMember__path)
      
      # Check if item is actual registered
      #{
      itemIsRegistered = False
      
      for item in rootDir.items:
        if item.name != fsItem__rootDirMember__name:
          continue
      
        if fsItemIsFile:
          if not isinstance(item, FSMeta_file):
            continue
        else:
          if not isinstance(item, FSMeta_dir):
            continue
          
        itemIsRegistered = True
        break
      #}
      
      if itemIsRegistered:
        continue

      addedItem = None
      if fsItemIsFile:
        addedItem = loadFSMeta_registerAdded_file(fsItem__rootDirMember__name, rootDir)
      else:
        addedItem = loadFSMeta_registerAdded_dir(fsItem__rootDirMember__name, rootDir)

      rootDir.addItem(addedItem)
   
  return FSMeta(rootDirs)

# -----------------------------------------------------------

def loadOrMakeFSMeta(dir__metaToLoad__path, rootDirsIfMake_path):
  if existsFSMeta(dir__metaToLoad__path):
    fsMeta = loadFSMeta(dir__metaToLoad__path)
    
    if len(fsMeta.rootDirs) != len(rootDirsIfMake_path):
      #ERROR: Root dirs num if unexpected
      return None

    for rootDir in fsMeta.rootDirs:
      if not rootDir.getPath() in rootDirsIfMake_path:
        #ERROR: Unknown dir in loaded meta
        return None
    
    return fsMeta
    
  else:
    return makeFSMeta(rootDirsIfMake_path)
