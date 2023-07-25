
import os 

import sys
sys.path.insert(0, '../../_/python_utils')

from osint_fileUtils import isTextFile  
from osint_fileUtils import openTextFileForRead
from osint_fileUtils import listDir
from osint_fileUtils import ListDir_SortRule
from osint_fileUtils import isLink
from osint_fileUtils import getLinkPath
from osint_fileUtils import isFileNamedAs

from osint_argumentsParsing import parseArguments
from osint_argumentsParsing import ArgumentParser_Named
from osint_argumentsParsing import ParseResult

from osint_timeUtils import parseTime

from osint_pathUtils import getFSItemName

from osint_videoUtils import getVideoDuration

from osint_stringUtils import getStringBetween
from osint_stringUtils import findMatchedSubstring

# ==================================

def getMarkedForSkippingPrefix():
  return "#"

def isNameMarkedForSkipping(name):
  position = name.strip().find(getMarkedForSkippingPrefix())
  
  #Skipping if path item is started from skip prefix
  return (position == 0)

# ----------------------------------

def getSkipUpdatePrefix():
  return "@"

def isNameMarkedForSkipping(name):
  position = name.strip().find(getSkipUpdatePrefix())
  
  #Skipping if path item is started from skip prefix
  return (position == 0)

def isPathMarkedForSkipping(path):
  name = getFSItemName(path)
  
  return isNameMarkedForSkipping(name)

# ================================== SETSourceSettings class =======================================

class SETSourceSettings:

  # argument_strings: string[]
  def __init__(self, details, sourceURL, backupURL, cutTimes):
    self.name = None
    self.details = details
    self.contentPath = None
    self.sourceURL = sourceURL
    self.backupURL = backupURL
    self.cutTimes = cutTimes
    
    self.cache_contentDuration = None  

    self.contentStep = 5

    self.skip_sourceTextForming = False
    self.skip_framesForming = False
    
  def getContentDuration(self):
    if self.contentPath == None:
      return None
      
    if self.cache_contentDuration == None:
      self.cache_contentDuration = getVideoDuration(self.contentPath)
    
    return self.cache_contentDuration

# ========================== SETSourceSettings parsing from arguments =============================

def parseSETSourceSettings(arguments):
  
  # Form details parser
  argumentNames_details =\
    ["подробности", "детали", "details"]
  
  parseSETSourceSettings.details = None
  def resultAction_setDetails(value):
    parseSETSourceSettings.details = value
  
  detailsParser = ArgumentParser_Named(argumentNames_details, resultAction_setDetails)
  
  # Form sourceURL parser
  argumentNames_source =\
    ["ссылка", "link",\
     "источник", "source",\
     "адресс", "address", "adress", "adres",\
     "ссылка на источник", "source link",\
     "URL источника", "source URL", "sourceURL"]

  parseSETSourceSettings.sourceURL = None
  def resultAction_setSource(value):
    parseSETSourceSettings.sourceURL = value
  
  sourceParser = ArgumentParser_Named(argumentNames_source, resultAction_setSource)
  
  # Form backupURL parser
  argumentNames_backup =\
    ["бэкап", "бекап", "backup",\
     "ссылка на бэкап", "ссылка на бекап", "backup link"
     "URL бэкапа", "URL бекапа", "backup URL"]
  
  parseSETSourceSettings.backupURL = None
  def resultAction_setBackup(value):
    parseSETSourceSettings.backupURL = value
  
  backupParser = ArgumentParser_Named(argumentNames_backup, resultAction_setBackup)  
  
  # Form cuts parser
  parseSETSourceSettings.cutTimes = []
  def resultAction_setCutTimes(value):
    parseSETSourceSettings.cutTimes = value
  
  sourceCutsParser = ArgumentParser_SETSourceCuts(resultAction_setCutTimes)
    
  # Perform parcing
  parsers = [\
    detailsParser,\
    sourceParser,\
    backupParser,\
    sourceCutsParser]
  
  parseResult = parseArguments(arguments, parsers)

  if parseResult == ParseResult.Failed:
    return None

  # Write result
  return SETSourceSettings(\
    parseSETSourceSettings.details,\
    parseSETSourceSettings.sourceURL,\
    parseSETSourceSettings.backupURL,\
    parseSETSourceSettings.cutTimes)

# - - - - - - - - - - - - - - - - - - - Private details - - - - - - - - - - - - - - - - - - - 

#NOTE: This is statefull parser
class ArgumentParser_SETSourceCuts():

  def __init__(self, resultAction):
    self.resultAction = resultAction
    self.cuts = []

  def parse(self, argument):
    possibleTime = parseTime(argument)
             
    if possibleTime != None:
      self.cuts.append(possibleTime)
      return ParseResult.Continue
  
    # Cases when element parse failed
    if len(self.cuts) != 0:
      self.finish()
      return ParseResult.Finished

    return ParseResult.Failed 
  
  def finish(self):
    self.resultAction(self.cuts)
    
    # Reset for possible next parsing
    self.cuts = []

# ======================== SETSourceSettings forming from file system member =========================

def formSourceSettingsForInputFSItem(fsItem__in_source__path):

  # Get input source members
  file__in_source_settings__path, file__in_source_content__path =\
    getPossibleSourceSettingsAndContentPathsForInputFSItem(fsItem__in_source__path)

  # Exit some members not found
  if file__in_source_settings__path == None:
    #ERROR: Cannot find source path
    return None

  # Parse source settings
  sourceSettings__fileObject = openTextFileForRead(file__in_source_settings__path)
  sourceSettingsLinesAsArguments = [line for line in sourceSettings__fileObject]
  sourceSettings = parseSETSourceSettings(sourceSettingsLinesAsArguments)
  
  if sourceSettings == None:
    #ERROR: Cannot parse source settings
    return None
  
  # Exit if some needed setting members are not parsed
  # --- Currently no actions here ---  

  # Source settings after parse fillings
  
  # Set source content path
  if file__in_source_content__path != None:
    if sourceSettings.contentPath == None:
      sourceSettings.contentPath = file__in_source_content__path
    else:
      #WARNING: Content path specified in source settings
      #  while possible content file exists in source directory
      pass

  # Set name
  if sourceSettings.name == None:
  
    possibleName = getFSItemName(fsItem__in_source__path, False)
    
    if not isNameMarkedForSkipping(possibleName):
      sourceSettings.name = possibleName
  
    if sourceSettings.name == None and file__in_source_content__path != None:
      possibleName = getFSItemName(file__in_source_content__path, False)
      if not isNameMarkedForSkipping(possibleName):
        sourceSettings.name = possibleName
   
    if sourceSettings.name == None:
      possibleName = getFSItemName(file__in_source_settings__path, False)
      if not isNameMarkedForSkipping(possibleName):
        sourceSettings.name = possibleName      
    
  #Skipping
  
  if isPathMarkedForSkipping(fsItem__in_source__path):
    sourceSettings.skip_sourceTextForming = True
  
  if file__in_source_content__path != None and isPathMarkedForSkipping(file__in_source_content__path):
    sourceSettings.skip_framesForming = True
  
  # Return result
  return sourceSettings


# - - - - - - - - - - - - - - - - - - - Private details - - - - - - - - - - - - - - - - - - - 

def getPossibleSourceSettingsAndContentPathsForInputFSItem_file(file__path):
  if not isTextFile(file__path):
    # ERROR: Source file cannot be used as setting
    return (None, None)

  return (file__path, None)

def getPossibleSourceSettingsAndContentPathsForInputFSItem_directory(directory__path):
  file__settings__path = None
  file__content__path = None  

  for directory_member__name in os.listdir(directory__path):
   
    fsItem__directory_member__path = os.path.join(directory__path, directory_member__name)
    
    #Ignore subdirectories with warning: they not make mess for us
    if not os.path.isfile(fsItem__directory_member__path):
      #WARNING: Some unexpected subdirectories in the source directory
      continue
    file__directory_member__path = fsItem__directory_member__path
        
    if isTextFile(file__directory_member__path):
      if file__settings__path == None:
        file__settings__path = file__directory_member__path
      else:
        print(\
          "ERROR| Several possible setting files:",\
          " existing [{current}], one that is try to set [{new}]".format(\
            current = file__settings__path,\
            new = file__directory_member__path))
        return (None, None)
    else:
      if file__content__path == None:
        file__content__path = file__directory_member__path
      else:
        print(\
          "ERROR| Several possible content files:",\
          " existing [{current}], one that is try to set [{new}]".format(\
            current = file__content__path,\
            new = file__directory_member__path))
        return (None, None)

  return (file__settings__path, file__content__path)


def getPossibleSourceSettingsAndContentPathsForInputFSItem(fsItem__in_source__path):

  if os.path.isfile(fsItem__in_source__path):
    return getPossibleSourceSettingsAndContentPathsForInputFSItem_file(fsItem__in_source__path)
  else:
    return getPossibleSourceSettingsAndContentPathsForInputFSItem_directory(fsItem__in_source__path)

  dir__in_source__path = fsItem__in_possibleSource__path



# ======================== SETSourceSettings forming from file system member =========================

class SETMatchingSettings_ContentMoment:

  # "time" is expected as "datetime.timedelta"
  def __init__(self, path, time, captionName):    
    self.path = path
    self.time = time
    
    self.captionName = captionName

class SETMatchingSettings_Link:

  # "time" is expected as "datetime.timedelta"
  def __init__(self, name, URL, captionName): 
    self.name = name
    self.URL = URL
    
    self.captionName = captionName

class SETMatchingSettings:

  # members: { "..._ContentMoment" or "..._URLLink" }[]
  def __init__(self, name, members):
    self.name = name
  
    self.members = members
    
def formMatchingSettingsForInputFSItem_formMember_contentMoment(link__moment__path):
  
  fsItem__matchingLinkedItem__path = getLinkPath(link__moment__path)

  # Get content path
  path = None

  if os.path.isdir(fsItem__matchingLinkedItem__path):
    unused, path =\
      getPossibleSourceSettingsAndContentPathsForInputFSItem(fsItem__matchingLinkedItem__path)
  
  elif os.path.isfile(fsItem__matchingLinkedItem__path):
    path = fsItem__matchingLinkedItem__path
  
  else:
    #ERROR: Unknown fsItem is pointed by link
    pass

  # Get time moment

  fsItem__matchingLinkedItem__name = getFSItemName(link__moment__path)
  
  possibleTimeString = getStringBetween(fsItem__matchingLinkedItem__name, '[' , ']')
  time = parseTime(possibleTimeString)

  return SETMatchingSettings_ContentMoment(path, time, getFSItemName(fsItem__matchingLinkedItem__path))


def formMatchingSettingsForInputFSItem_formMember_link(name, openedFileObject, captionName):
  #NOTE: All lines are concated as URL, concated WITHOUT ant delimiter
  URLString = "".join([line for line in openedFileObject])
  
  return SETMatchingSettings_Link(name, URLString, captionName)

def formMatchingSettingsForInputFSItem_formMember(fsItem__matching_member__path):

  #Constants
  possibleLinkKindNames = ["Ссылка", "Link"]

  #Logic
  if isLink(fsItem__matching_member__path):
    link__matching_member__path = fsItem__matching_member__path  
    return formMatchingSettingsForInputFSItem_formMember_contentMoment(link__matching_member__path)
    
  elif os.path.isfile(fsItem__matching_member__path):
    file__matching_member__path = fsItem__matching_member__path
    file__matching_member__name = getFSItemName(fsItem__matching_member__path, False)
    
    if not isTextFile(file__matching_member__path):
      #WARNING: Only text files may be used as not-link objects
      return None
    
    fileObjectKind = getStringBetween(file__matching_member__name, '[', ']', True)
    if fileObjectKind == None:
      #WARNING: Unkinded files are not supported
      return None
        
    fileObjectName = getStringBetween(file__matching_member__name, ']', None, True)
  
    if findMatchedSubstring(fileObjectKind, possibleLinkKindNames):
      return formMatchingSettingsForInputFSItem_formMember_link(\
        fileObjectName,\
        openTextFileForRead(file__matching_member__path),\
        fileObjectName)

    #WARNING: Unknown file object kind  
    return None
    
  else:
    #Looks like director... Warning.
    #Currently dirs is not used for members setup
    return None
    
def formMatchingSettingsForInputFSItem(fsItem__matching__path):

  if not os.path.isdir(fsItem__matching__path):
    #ERROR: Matching should be presented as dir!
    return None
  dir__matching__path = fsItem__matching__path

  members = []

  for fsItem__matching_member__path in listDir(dir__matching__path, ListDir_SortRule.DontSort):
    member = formMatchingSettingsForInputFSItem_formMember(fsItem__matching_member__path)
    if member != None:
      members.append(member)   
   
  name = getFSItemName(dir__matching__path)

  return SETMatchingSettings(name, members)