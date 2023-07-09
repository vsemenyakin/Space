import datetime
import os
import math

import sys
sys.path.insert(0, '../../_/python_utils')

from osint_URLUtils import tryMakeTimestampedURL
from osint_URLUtils import makeURLUnclickableForMarkdown

from osint_timeUtils import timeDeltaToString

from osint_fileUtils import mkDirSafe
from osint_fileUtils import rmDirSafe
from osint_fileUtils import openTextFileForWrite

from osint_videoUtils import excludeFrames

from osint_scopedPrinter import getScopedPrinter

from osint_profiling import getSimpleProfiler

from osint_pathUtils import getFSItemName
from osint_pathUtils import getPathWithoutLastMember

from osint_sourceSettings_in import SETMatchingSettings_ContentMoment
from osint_sourceSettings_in import SETMatchingSettings_Link

# ================================ Frames =========================================

def formSourceRangeFrames(in_content__path, dir__out__path, rangeStart, rangeEnd, step):

  getScopedPrinter().print("Forming image frames in range [{stringFrom} - {stringTo}]".format(\
    stringFrom = timeDeltaToString(rangeStart, formSourceRangeFrames_getTimeFormat_forFrame()),
    stringTo = timeDeltaToString(rangeEnd, formSourceRangeFrames_getTimeFormat_forFrame())\
  ))
  getScopedPrinter().scopeIn()

  dir__out_source_frames__path = formSourceRangeFrames_getRangeFramesDirPath(\
    dir__out__path, rangeStart, rangeEnd)

  mkDirSafe(dir__out_source_frames__path)

  framesRange_actualBegin__int = math.floor(rangeStart.total_seconds())
  framesRange_actualEnd__int = math.floor(rangeEnd.total_seconds())
  
  #TODO: Prepare log file!
  file__out_source_frames_log__fileObject = open(\
    formSourceRangeFrames_getLogFilePath(dir__out_source_frames__path), 'a')  

  getSimpleProfiler().start("FrameForming")
  
  for frameTimeSeconds in range(framesRange_actualBegin__int, framesRange_actualEnd__int, step):

    frameTime = datetime.timedelta(seconds = frameTimeSeconds)

    dir__out_source_frames_frame__name = timeDeltaToString(frameTime,\
      formSourceRangeFrames_getTimeFormat_forFrame())
    dir__out_source_frames_frame__nameAndExt = dir__out_source_frames_frame__name + "." + "png"
    dir__out_source_frames_frame__path = os.path.join(\
      dir__out_source_frames__path,\
      dir__out_source_frames_frame__nameAndExt)

    getScopedPrinter().print("Frame [{timeString}] image forming".format(\
      timeString = timeDeltaToString(frameTime, formSourceRangeFrames_getTimeFormat_forFrame()))\
    )

    excludeFrames(in_content__path, dir__out_source_frames_frame__path, frameTime,\
      file__out_source_frames_log__fileObject)
    file__out_source_frames_log__fileObject.flush()
    
    file__out_source_frames_log__fileObject.write("============================================================\n")

  time = getSimpleProfiler().finish("FrameForming")
  getScopedPrinter().print("*** Time taken: {time} seconds".format(\
    time = round(time.total_seconds(), 3)\
  ))

  getScopedPrinter().scopeOut()

# - - - - - - - - - - - - - - - - - - Private details - - - - - - - - - - - - - - - - - - 

def formSourceRangeFrames_getTimeFormat_forFramesDir():
  return "%M_%S"

def formSourceRangeFrames_getTimeFormat_forFrame():
  return "%M_%S"

def formSourceRangeFrames_getTimeFormat_forSourceText():
  return "%M:%S"

def formSourceRangeFrames_getTimeFormat_forMatchingFrame():
  return "%M_%S.%f"

# - - - - - - - - - - - - - - - - - - Private details - - - - - - - - - - - - - - - - - - 

def formSourceRangeFrames_getRangeFramesDirPath(dir__out__path, rangeStart, rangeEnd):

  #Note: ':' cannot be used as time delimiter because it is not allowed in Windows paths
  timeFormat = formSourceRangeFrames_getTimeFormat_forFramesDir()

  rangeStart__string = timeDeltaToString(rangeStart, timeFormat)
  rangeEnd__string = timeDeltaToString(rangeEnd, timeFormat)
  
  dir__range__name = "[{startText} - {endText}]".format(\
    startText = rangeStart__string,
    endText = rangeEnd__string)

  return os.path.join(dir__out__path, dir__range__name)

def formSourceRangeFrames_getLogFilePath(dir__out_source_frames__path):
  return os.path.join(dir__out_source_frames__path, "log.txt")

# ============================== Source text ======================================

def formSourceLines(settings):

  resultLines = []

  #Add header
  resultLines.append(settings.name)

  #Add details
  if settings.details != None:
    resultLines.append(settings.details)

  #Add 
  rangeStart = datetime.timedelta()
  
  for cutTime in settings.cutTimes:
    
    rangeEnd = cutTime
    
    rangeLine = formSourceText_range(rangeStart, rangeEnd, settings.sourceURL, settings.backupURL)
    resultLines.append(rangeLine)
    
    rangeStart = rangeEnd

  rangeEnd = settings.getContentDuration()

  rangeLine = formSourceText_range(rangeStart, rangeEnd, settings.sourceURL, settings.backupURL)
  resultLines.append(rangeLine)

  resultLines.append("\[{searchWorkaroundLink}\]".format(\
    searchWorkaroundLink = makeURLUnclickableForMarkdown(settings.sourceURL)
  ))
  
  return resultLines

# - - - - - - - - - - - - - - - - - - Private details - - - - - - - - - - - - - - - - - - 

def formSourceText_range(startTime, endTime, contentURL, backupURL):

  stringForUnknownEndTime = "End"

  timeFormat = formSourceRangeFrames_getTimeFormat_forSourceText()
  
  endTimeString = timeDeltaToString(endTime, timeFormat)\
    if endTime != None else\
    stringForUnknownEndTime
  
  sourceText = "[{startTime} - {endTime}]({link})".format(\
    startTime = timeDeltaToString(startTime, timeFormat),\
    endTime = endTimeString,\
    link = tryMakeTimestampedURL(contentURL, startTime))
  
  backupText = "[Backup]({link})".format(\
    link = tryMakeTimestampedURL(backupURL, startTime))
  
  return "\[{source} | {backup}\] - Episode | Timeline".format(\
    source = sourceText,\
    backup = backupText)

# ================================ Matchings =========================================

def formMatching_getMatchingMemberDirPath_ContentMoment(dir__matching_out__path, contentMoment):

  timeSting = timeDeltaToString(contentMoment.time, formSourceRangeFrames_getTimeFormat_forMatchingFrame())
  outName = getFSItemName(getPathWithoutLastMember(contentMoment.path), False)
  dir__matching_member_out__name = "[" + timeSting + "]" + " " + outName

  return os.path.join(dir__matching_out__path, dir__matching_member_out__name)

def formMatchingMemberOutput_ContentMoment(contentMoment, dir__matching_out__path):

  dir__matching_member_out__path = formMatching_getMatchingMemberDirPath_ContentMoment(dir__matching_out__path, contentMoment)

  rmDirSafe(dir__matching_member_out__path)
  mkDirSafe(dir__matching_member_out__path)

  #- Heading actions
  # Preparing log file
  file__matching_member_log_out__fileObject = open(os.path.join(dir__matching_member_out__path, "log.txt"), 'a')  

  getScopedPrinter().print("Forming frame image for [{name}] frame moment matching member".format(
    name = getFSItemName(contentMoment.captionName))\
  )  
  getScopedPrinter().scopeIn()

  getSimpleProfiler().start("MatchingFramesForming")
  
  # Form frame
  file__matching_member_frame_out__path = os.path.join(dir__matching_member_out__path, "frame.png")
  
  excludeFrames(contentMoment.path, file__matching_member_frame_out__path, contentMoment.time,\
    file__matching_member_log_out__fileObject)  

  # Footing actions

  time = getSimpleProfiler().finish("MatchingFramesForming")
  getScopedPrinter().print("*** Time taken: {time} seconds".format(\
    time = round(time.total_seconds(), 3)\
  ))

  getScopedPrinter().scopeOut()

def formMatching_getMatchingMemberDirPath_Link(dir__matching_out__path, link):
  return os.path.join(dir__matching_out__path, link.name)

def createBatch_openURL(file__batch__path, URL):
  #TODO: Support cross-platform script

  openURLBatchCommand = "explorer"  
     
  file__output_source_lines__fileObject = openTextFileForWrite(file__batch__path)
  if file__output_source_lines__fileObject == None:
    return False
  
  file__output_source_lines__fileObject.write(openURLBatchCommand + " " + "\"" + URL + "\"")
  return True

def createBatch_copyURLMarkdown(file__batch__path, URLName, URL):
  #TODO: Support cross-platform script

  openURLBatchCommand = "echo"  
  openURLBatchFinisher = "|clip"
  
  textToCopy = "[" + URLName + "](" + URL + ")"
  
  file__output_source_lines__fileObject = openTextFileForWrite(file__batch__path)
  if file__output_source_lines__fileObject == None:
    return False
  
  file__output_source_lines__fileObject.write(openURLBatchCommand + " " + textToCopy + openURLBatchFinisher)
  return True

def formMatchingMemberOutput_Link(link, dir__matching_out__path):

  dir__matching_member_out__path = formMatching_getMatchingMemberDirPath_Link(dir__matching_out__path, link)

  rmDirSafe(dir__matching_member_out__path)
  mkDirSafe(dir__matching_member_out__path)

  #- Heading actions
  # Preparing log file
  getScopedPrinter().print("Forming batch files for [{name}] link matching member".format(
    name = getFSItemName(link.captionName))\
  )  
  getScopedPrinter().scopeIn()
  
  #NB: Forming bat files should not take a lot of time - so no profiling is needed
  
  #Perform actions
  #-Create open batch
  file__matching_member_openBatch_out__path = os.path.join(dir__matching_member_out__path, "open.bat")
  isBatchCreated = createBatch_openURL(file__matching_member_openBatch_out__path, link.URL)
  if not isBatchCreated:
    getScopedPrinter().printAndScopeOut("ERROR: Cannot open text file for forming \"open.bat\"")

  #-Create copy batch
  file__matching_member_copyBatch_out__path = os.path.join(dir__matching_member_out__path, "copy.bat")
  isBatchCreated = createBatch_copyURLMarkdown(file__matching_member_copyBatch_out__path, link.name, link.URL)
  if not isBatchCreated:
    getScopedPrinter().printAndScopeOut("ERROR: Cannot open text file for forming \"copy.bat\"")
   
  # Footing actions
  getScopedPrinter().scopeOut()

def formMatchingMemberOutput(member, dir__out_matching__path):
  
  if isinstance(member, SETMatchingSettings_ContentMoment):
    formMatchingMemberOutput_ContentMoment(member, dir__out_matching__path)
  elif isinstance(member, SETMatchingSettings_Link):
    formMatchingMemberOutput_Link(member, dir__out_matching__path)
  else:
    #UNKNOWN type
    pass
