
import os #for os.getcwd()

# Custom modules
import sys
sys.path.insert(0, '../_/python_utils')
sys.path.insert(0, '_')

from osint_sourceSettings_in import formSourceSettingsForInputFSItem

#for tests
import datetime 
from osint_sourceSettings_in import SETSourceSettings
from osint_sourceSettings_out import formSourceLines

from osint_sourceSettings_out import formSourceRangeFrames

from osint_pathUtils import getPathFromWhichProcessIsCalled
from osint_pathUtils import getFSItemName

from osint_fileUtils import mkDirSafe
from osint_fileUtils import openTextFileForWrite

from osint_fileSystemChangesTracking import loadOrMakeFSMeta
from osint_fileSystemChangesTracking import saveFSMeta

# ========================= Form data for investigations =================================

def getInvestigationsPathsInDir(dir__investigations__path):
  # Currently we make no checks here, just assumes
  
  #TODO: Make checks here

  result = []

  for fsItem__investigation__name in os.listdir(dir__investigations__path):
    fsItem__investigation__path = os.path.join(\
      dir__investigations__path, fsItem__investigation__name)

    if not os.path.isdir(fsItem__investigation__path):
      #Print Warning here: unexcepeted file in investigations directory
      continue
    dir__investigation__path = fsItem__investigation__path
    
    result.append(dir__investigation__path)
  
  return result

def formSource_sourceText(settings, dir__output__path):
  
  # Prepare directory for source
  
  dir__output_source__name = settings.name
  dir__output_source__path = os.path.join(dir__output__path, dir__output_source__name)
  
  mkDirSafe(dir__output_source__path)

  # Print source text
  
  sourceLines = formSourceLines(settings)

  file__output_source_lines__name = "source.txt"
  file__output_source_lines__path = os.path.join(dir__output_source__path, file__output_source_lines__name)

  file__output_source_lines__fileObject = openTextFileForWrite(file__output_source_lines__path)
  for sourceLine in sourceLines:
    file__output_source_lines__fileObject.write(sourceLine)
    file__output_source_lines__fileObject.write("\n")

def formSource_frames(settings, dir__output__path):
  
  rangeStart = datetime.timedelta()
  
  for cutTime in settings.cutTimes:
    
    rangeEnd = cutTime
    
    formSourceRangeFrames(settings.contentPath, dir__output_source__path,\
      rangeStart, rangeEnd, settings.contentStep)
    
    rangeStart = rangeEnd

  rangeEnd = settings.getContentDuration()

  formSourceRangeFrames(settings.contentPath, dir__output_source__path,\
    rangeStart, rangeEnd, settings.contentStep)

def formInvestigationOutput(dir__investigation__path, dir__output__path):

  investigationName = getFSItemName(dir__investigation__path)

  dir__output_investigation__path = os.path.join(dir__output__path, investigationName)
  mkDirSafe(dir__output_investigation__path)

  for fsItem__investigation_source___name in os.listdir(dir__investigation__path):
    fsItem__investigation_source___path = os.path.join(\
      dir__investigation__path, fsItem__investigation_source___name)
                
    formSourceOutput(fsItem__investigation_source___path, dir__output_investigation__path)

## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class OSINT_UpdateSettings_Investigation_Source:

  def __init__(self,\
    settingsIn, dir__output__path,\
    shouldUpdate_sourceText, shouldUpdate_frames,\
    updateCauseString):
      
    self.settingsIn = settingsIn
    self.dir__output__path = dir__output__path
    
    self.shouldUpdate_sourceText = shouldUpdate_sourceText
    self.shouldUpdate_frames = shouldUpdate_frames    
  
    self.updateCauseString = updateCauseString
  
  # Return if updated took place as planed
  def performUpdate(self):
    
    if not self.shouldUpdate_sourceText and not self.shouldUpdate_frames:
      #WARNING: Useless settings
      return True
    
    if self.shouldUpdate_sourceText:
      localSuccess = formSource_sourceText(settingsIn, self.dir__output__path)
      if not localSuccess:
        return False
    
    if self.shouldUpdate_frames:
      localSuccess = formSource_frames(settingsIn, self.dir__output__path)    
      if not localSuccess:
        return False    

    return True


class OSINT_UpdateSettings_Investigation:

  def __init__(self, name, sourceUpdateSettings, updateCauseString):
    self.name = name
    self.sourceUpdateSettings = sourceUpdateSettings
    
    self.updateCauseString = updateCauseString

# ********************************************

def getInvestigationMetaOutByIn(dir__in_investigation__meta, dir__out__meta):
  
  investigationName = dir__in_investigation__meta.getName()

  for fsItem__out_investigation__meta in dir__out__meta.items:
    
    if isinstance(fsItem__out_investigation__meta, FSMeta_file):
      #WARNING: Unexpected file in investigations OUT folder
      # Just actualize info about it
      continue
    dir__out_investigation__meta = fsItem__out_investigation__meta
  
    if dir__out_investigation__meta.getName() == investigationName
      return (dir__out_investigation__meta, dir__out_investigation__meta.getPath())

  out_path = os.path.join(dir__out__meta.getPath(), investigationName)
  return (None, out_path)

# ********************************************

def formSourcesUpdateSettings_prepareFullInvestigationUpdate(\
  dir__investigationIn__meta, dir__investigationOut__path):

  # In was added - so no existing output is expected. Remove existing
  # directory before update
  rmDirSafe(dir__investigationOut__path)
  
  result = []
  
  for fsItem__investigationIn_source__meta in dir__investigationIn__meta.items:
  
    settingsIn = formSourceSettingsForInputFSItem(fsItem__investigationIn_source__meta.getPath())
    
    if settingsIn == None:
      #WARNING: Cannot create settings for source input
      continue
    
    sourceUpdateSetting = OSINT_UpdateSettings_Investigation_Source(\
      settingsIn, dir__investigationOut__path,\
      shouldUpdate_sourceText = True, shouldUpdate_frames = True,\
      updateCauseString = "Investigation added")
    
    result.append(sourceUpdateSetting)
  
  return result

# "dir__investigationOut" is passed for cause when no meta is exist
def formSourcesUpdateSettings(dir__investigationIn__meta, dir__investigationOut__meta, dir__investigationOut__path):

#class EFSMetaItemStatus(Enum):
#  Actual = 1
#  Added = 2
#  Changed = 3
#  Removed = 4

  status = dir__investigationIn__meta.getStatus()

  if status == EFSMetaItemStatus.Actual:

    # Out is unchanged too. No changes are needed    
    if dir__investigationOut__meta != None and outStatus == EFSMetaItemStatus.Actual:
      return []
  
    fullUpdateCause = None    
    if dir__investigationOut__meta != None:
    
      outStatus = dir__investigationOut__meta.getStatus()
        
      if outStatus == EFSMetaItemStatus.Added or :
        fullUpdateCause = "Untracked adding of investigation directory"
      
      elif outStatus == EFSMetaItemStatus.Removed:
        fullUpdateCause = "Untracked removing of investigation directory"
    
    else:
      fullUpdateCause = "Investigation directory was unexisted"
        
    if fullUpdateCause != None:
    
      #TODO: For full update 
    
      return
    
    # If we got here - we know that "dir__investigationOut__meta"\
    # has Changed status
    
        
        
    if dir__investigationOut__meta == None or\
      dir__investigationOut__meta.getStatus() == EFSMetaItemStatus.Removed:
    
    
    return [] 

  if status == EFSMetaItemStatus.Removed:
    if dir__investigationOut__meta != None and\
      dir__investigationOut__meta.getStatus() != EFSMetaItemStatus.Removed:
      
      # In was removed while out is exists. Remove output
      rmDirSafe(dir__investigationOut__meta.getPath())
      
      
    #TODO: Make removing as kind of update type!
    return []

  elif status == EFSMetaItemStatus.Added:
  
    if dir__investigationOut__meta != None and\
      dir__investigationOut__meta.getStatus() != EFSMetaItemStatus.Removed:
  
      # In was added - so no existing output is expected. Remove existing
      # directory before update
      rmDirSafe(dir__investigationOut__meta.getPath())
  
    result = []
  
    for fsItem__investigationIn_source__meta in dir__investigationIn__meta.items:
    
      settingsIn = formSourceSettingsForInputFSItem(fsItem__investigationIn_source__meta.getPath())
      
      if settingsIn == None:
        #WARNING: Cannot create settings for source input
        continue
      
      sourceUpdateSetting = OSINT_UpdateSettings_Investigation_Source(\
        settingsIn, dir__investigationOut__path,\
        shouldUpdate_sourceText = True, shouldUpdate_frames = True,\
        updateCauseString = "Investigation added")
      
      result.append(sourceUpdateSetting)
  
    return result
      
  elif status == EFSMetaItemStatus.Changed:
    #TODO: Find what items changed and how

  else
    #WARNING: Unsupported change status
    return []






def formInvestigationsUpdateSettings(dir__in__meta, dir__out__meta):
  
  dir__in__meta = dir__in__meta.rootDirs[0]
  
  result = []
  
  for fsItem__in_investigation__meta in dir__in__meta.items:
    
    if isinstance(fsItem__in_investigation__meta, FSMeta_file):
      #WARNING: Unexpected file in investigations IN folder
      # Just actualize info about it
      continue

    dir__in_investigation__meta = fsItem__in_investigation__meta
    (dir__out_investigation__meta, dir__out_investigation__path) =\
      getInvestigationMetaOutByIn(dir__in_investigation__meta, dir__out__meta)

    #TODO: Pass output settings
    sourceUpdateSettings = formSourcesUpdateSettings(\
      dir__in_investigation__meta,\
      dir__out_investigation__meta,\
      dir__out_investigation__path)
    
    if updateSettings == None:
      return None

    if len(updateSettings) > 0:
    
      newInvestigationUpdateSettings = OSINT_UpdateSettings_Investigation(\
        dir__in_investigation__meta.getName(), sourceUpdateSettings)
    
      result.append(newInvestigationUpdateSettings)

  return result



## ********************************************
#
##TODO:
## 1. Print console out: print info about starting processing:
##     - Investigation
##     - Source
##     - Range
## 2. Print console out: time of processing the source
## 3. Try to perform frames processing in separate processes
#
## ******************************************** ENTER POINT
#
dir__in__name = "in"
dir__out__name = "out"
dir__meta__name = "meta"

#Form "in" and "out" paths
dir__in__path = os.path.join(getPathFromWhichProcessIsCalled(), dir__in__name)
dir__out__path = os.path.join(getPathFromWhichProcessIsCalled(), dir__out__name)

#Form "in" and "out" meta paths
dir__meta__path = os.path.join(getPathFromWhichProcessIsCalled(), dir__meta__name)
dir__meta_in__path = os.path.join(dir__meta__path, dir__in__name)
dir__meta_out__path = os.path.join(dir__meta__path, dir__out__name)

#Load meta
mkDirSafe(dir__meta__path)
metaIn = loadOrMakeFSMeta(dir__meta_in__path, [dir__in__path])
metaOut = loadOrMakeFSMeta(dir__meta_out__path, [dir__out__path])

#Form update settings
#TODO:
#
#1. Find what should be updated
# Source settings added / updated => make source AND frames
# Content added / updated => make frames
# Second priority:
# Todo: Make system for getting input by output!
# Source output changed => update source output only
# Any frame changed =>update frames
#
#2. Form source forming settings based on this info





#Perform
#TODO: Call forming output

#Save meta
saveFSMeta(dir__meta_in__path, metaIn)
saveFSMeta(dir__meta_out__path, metaOut)

#for dir__in_investigation__path in getInvestigationsPathsInDir(dir__in__path):
#  formInvestigationOutput(dir__in_investigation__path, dir__out__path)
