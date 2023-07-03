# For file actions
import os 
import shutil
import math
import datetime 

# For executable call
import subprocess

import os #for os.getcwd()

import datetime 

# Custom modules
import sys
from pathlib import Path
pythonRoot = Path(__file__).parents[1]
sys.path.insert(0, os.path.join(pythonRoot, "utils"))
sys.path.insert(0, os.path.join(pythonRoot, "OSINT", "_"))

from osint_sourceSettings_in import formSourceSettingsForInputFSItem
from osint_sourceSettings_in import formMatchingSettingsForInputFSItem
from osint_sourceSettings_in import isNameMarkedForSkipping
from osint_sourceSettings_in import isPathMarkedForSkipping

from osint_sourceSettings_out import formSourceLines
from osint_sourceSettings_out import formSourceRangeFrames
from osint_sourceSettings_out import formMatching

from osint_pathUtils import getPathFromWhichProcessIsCalled
from osint_pathUtils import getFSItemName

from osint_fileUtils import mkDirSafe
from osint_fileUtils import rmDirSafe
from osint_fileUtils import openTextFileForWrite
from osint_fileUtils import listDir
from osint_fileUtils import ListDir_SortRule
from osint_fileUtils import findDirMember

from osint_scopedPrinter import getScopedPrinter

from osint_profiling import getSimpleProfiler

# ========================= Form data for investigations =================================

def getInvestigationsPathsInDir(dir__investigations__path):
  # Currently we make no checks here, just assumes
  
  #TODO: Make checks here

  result = []

  for fsItem__investigation__path in listDir(dir__investigations__path, sortRule = ListDir_SortRule.DontSort):
    if not os.path.isdir(fsItem__investigation__path):
      #Print Warning here: unexcepeted file in investigations directory
      continue
    dir__investigation__path = fsItem__investigation__path
    
    result.append(dir__investigation__path)
  
  return result

# =================================================================

def formSource_sourceText(settings, dir__output__path):

  if settings.skip_sourceTextForming:
    getScopedPrinter().print("@ Skipped source text forming")  
    return True

  getScopedPrinter().print("Forming source text")
  getScopedPrinter().scopeIn()
  
  # Prepare directory for source
  
  dir__output_source__name = settings.name
  dir__output_source__path = os.path.join(dir__output__path, dir__output_source__name)
  
  mkDirSafe(dir__output_source__path)

  # Print source text
  
  sourceLines = formSourceLines(settings)

  file__output_source_lines__name = "source.txt"
  file__output_source_lines__path = os.path.join(dir__output_source__path, file__output_source_lines__name)

  file__output_source_lines__fileObject = openTextFileForWrite(file__output_source_lines__path)
  if file__output_source_lines__fileObject == None:
    getScopedPrinter().printAndScopeOut("ERROR: Cannot open text file for writing source text")
    return False
  
  for sourceLine in sourceLines:
    file__output_source_lines__fileObject.write(sourceLine)
    file__output_source_lines__fileObject.write("\n")
  
  getScopedPrinter().scopeOut()  
  
  return True

def formSource_frames(settings, dir__output__path):

  if settings.skip_framesForming:
    getScopedPrinter().print("@ Skipped frames forming")  
    return True

  getScopedPrinter().print("Forming source frames".format(\
    contentPath = settings.contentPath))
  getScopedPrinter().scopeIn()  
  
  rangeStart = datetime.timedelta()
  
  for cutTime in settings.cutTimes:
    
    rangeEnd = cutTime
    
    formSourceRangeFrames(settings.contentPath, dir__output__path,\
      rangeStart, rangeEnd, settings.contentStep)
    
    rangeStart = rangeEnd

  rangeEnd = settings.getContentDuration()

  formSourceRangeFrames(settings.contentPath, dir__output__path,\
    rangeStart, rangeEnd, settings.contentStep)

  getScopedPrinter().scopeOut()

  return True

def formSourceOutput(fsItem__in___path, dir__output__path):
  
  #Constants
  framesDirName = "frames"
  
  #Process skipping
  if isPathMarkedForSkipping(fsItem__in___path):
    getScopedPrinter().print("@ Source [{name}] is marked for skipping".format(\
      name = getFSItemName(fsItem__in___path)))
    return
      
  #Header actions
  getScopedPrinter().print("Forming source [{name}] data".format(\
    name = getFSItemName(fsItem__in___path)))
  getScopedPrinter().scopeIn()  
    
  #Form settings 
  settings = formSourceSettingsForInputFSItem(fsItem__in___path)
  if settings == None:
    getScopedPrinter().printAndScopeOut("ERROR: Invalid settings provided")
    return False    

  #[1] Form source text
  success = formSource_sourceText(settings, dir__output__path)
  if not success:
    getScopedPrinter().print("ERROR: Source text forming failure")
  
  #[2] Form frames
  if settings.contentPath != None:
    
    dir__output_investigation_source_frames__path = os.path.join(dir__output__path, settings.name, framesDirName)
    
    rmDirSafe(dir__output_investigation_source_frames__path)
    mkDirSafe(dir__output_investigation_source_frames__path)
  
    success = formSource_frames(settings, dir__output_investigation_source_frames__path)
    if not success:
      getScopedPrinter().printAndScopeOut("ERROR: Source frames forming failure")
  
  else:
    getScopedPrinter().print("<No content provided>")  

  #Footer actions
  getScopedPrinter().scopeOut()

  return True

# -----------------------------------------------------------------

def formMatchingOutput(fsItem__in___path, dir__output__path):

  #Process skipping
  if isPathMarkedForSkipping(fsItem__in___path):
    getScopedPrinter().print("@ Matching [{name}] is marked for skipping".format(\
      name = getFSItemName(fsItem__in___path)))
    return

  #Header actions
  getScopedPrinter().print("Forming source [{name}] data".format(\
    name = getFSItemName(fsItem__in___path)))
  getScopedPrinter().scopeIn()  
    
  #Form settings
  settings = formMatchingSettingsForInputFSItem(fsItem__in___path)
  if settings == None:
    getScopedPrinter().printAndScopeOut("ERROR: Invalid settings provided")
    return False    

  formMatching(\
    settings.name,\
    settings.contentMomentA.path, settings.contentMomentA.time,\
    settings.contentMomentB.path, settings.contentMomentB.time,\
    dir__output__path)

  #Footer actions
  getScopedPrinter().scopeOut()

# =================================================================

def formInvestigationOutput_sources(dir__in__path, dir__out__path):
  for fsItem__in_source___path in listDir(dir__in__path):
    formSourceOutput(fsItem__in_source___path, dir__out__path)

def formInvestigationOutput_matchings(dir__in__path, dir__out__path):
  for fsItem__in_matching___path in listDir(dir__in__path):
    formMatchingOutput(fsItem__in_matching___path, dir__out__path)

def formInvestigationOutput(dir__in__path, dir__out__path):

  #Constants
  dir__investigation_sources__possibleNames = [\
    "источники", "sources"\
  ]

  dir__investigation_matchings__possibleNames = [\
    "сопоставления", "matchings"\
  ]

  #Process skipping
  investigationName = getFSItemName(dir__in__path)

  if isNameMarkedForSkipping(investigationName):
    getScopedPrinter().print("@ Investigation [{name}] is marked for skipping".format(\
      name = investigationName))
    return

  #Prepare dir
  mkDirSafe(dir__in__path)

  #Heading actions
  getSimpleProfiler().start("Investigation")

  getScopedPrinter().print("Processing investigation [{name}]".format(\
    name = investigationName))
  getScopedPrinter().scopeIn()

  #Process sources
  fsItem__investigation_sources__path = findDirMember(dir__in__path, dir__investigation_sources__possibleNames)
  
  if fsItem__investigation_sources__path != None:
    if os.path.isdir(fsItem__investigation_sources__path):
      if not isPathMarkedForSkipping(fsItem__investigation_sources__path):
        
        dir__investigation_sources__path = fsItem__investigation_sources__path
        
        dir__investigation_sources__name = getFSItemName(dir__investigation_sources__path)      
        dir__output_sources__path = os.path.join(dir__out__path, dir__investigation_sources__name)
        
        mkDirSafe(dir__output_sources__path)
        
        formInvestigationOutput_sources(dir__investigation_sources__path, dir__output_sources__path)

      else:
        getScopedPrinter().print("@ Skipped sources forming")

    else:
      getScopedPrinter().print("ERROR: Sources was provided not by directory")
  
  else:
    getScopedPrinter().print("ERROR: Cannot find sources directory")

  #Process matchings
  fsItem__investigation_matchings__path = findDirMember(dir__in__path, dir__investigation_matchings__possibleNames)
  
  if fsItem__investigation_matchings__path != None:
    if os.path.isdir(fsItem__investigation_matchings__path):
      if not isPathMarkedForSkipping(fsItem__investigation_matchings__path):

        dir__investigation_matchings__path = fsItem__investigation_matchings__path
        
        dir__investigation_matchings__name = getFSItemName(dir__investigation_matchings__path)      
        dir__output_matchings__path = os.path.join(dir__out__path, dir__investigation_matchings__name)
        
        mkDirSafe(dir__output_matchings__path)
        
        formInvestigationOutput_matchings(dir__investigation_matchings__path, dir__output_matchings__path)

      else:
        getScopedPrinter().print("@ Skipped matchings forming")

    else:
      getScopedPrinter().print("ERROR: Matchings was provided not by directory")
  
  else:
    getScopedPrinter().print("ERROR: Cannot find matchings directory")

  #Footer actions
  time = getSimpleProfiler().finish("Investigation")
  getScopedPrinter().print("*** Time taken: {time} seconds".format(\
    time = round(time.total_seconds(), 3)\
  ))

  getScopedPrinter().scopeOut()

## ******************************************** ENTRY POINT

dir__in__name = "in"
dir__out__name = "out"

#Form "in" and "out" paths
dir__in__path = os.path.join(getPathFromWhichProcessIsCalled(), dir__in__name)
dir__out__path = os.path.join(getPathFromWhichProcessIsCalled(), dir__out__name)

for dir__in_investigation__path in getInvestigationsPathsInDir(dir__in__path):
  formInvestigationOutput(dir__in_investigation__path, dir__out__path)
