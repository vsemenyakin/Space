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

from osint_videoUtils import excludeFrames

from osint_scopedPrinter import getScopedPrinter

from osint_profiling import getSimpleProfiler

from osint_pathUtils import getFSItemName
from osint_pathUtils import getPathWithoutLastMember

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

def formMatching_getMatchingDirPath(dir__out__path, matchingName):
  return os.path.join(dir__out__path, matchingName)

def formMatching_getLogFilePath(dir__out__path, matchingName):
  dir__out_matching__path = formMatching_getMatchingDirPath(dir__out__path, matchingName)
  return os.path.join(dir__out_matching__path, "log.txt")

def formMatching_getOutFilePath(dir__out__path, in_time, file__in_content__path, matchingName):

  timeSting = timeDeltaToString(in_time, formSourceRangeFrames_getTimeFormat_forFrame())
  outName = getFSItemName(getPathWithoutLastMember(file__in_content__path), False)
  file__out_matching_frame__name = "[" + timeSting + "]" + " " + outName + "." + "png"

  dir__out_matching__path = formMatching_getMatchingDirPath(dir__out__path, matchingName)
  return os.path.join(dir__out_matching__path, file__out_matching_frame__name)

def formMatching(matchingName,\
  file__in_contentA__path, in_timeA,\
  file__in_contentB__path, in_timeB,\
  dir__out__path):

  getScopedPrinter().print("Forming image frames for matching [{matchingName}]".format(\
    matchingName = matchingName)\
  )
  getScopedPrinter().scopeIn()

  dir__out_matching__path = formMatching_getMatchingDirPath(dir__out__path, matchingName)

  rmDirSafe(dir__out_matching__path)
  mkDirSafe(dir__out_matching__path)

  #TODO: Prepare log file!
  file__out_log__fileObject = open(\
    formMatching_getLogFilePath(dir__out__path, matchingName), 'a')  

  # Heading actions

  getSimpleProfiler().start("MatchingFramesForming")
  
  # Form frame for the A
  outPath = formMatching_getOutFilePath(dir__out__path, in_timeA, file__in_contentA__path, matchingName)

  getScopedPrinter().print("Forming frame image for [{name}]".format(
    name = getFSItemName(outPath, False))\
  )  
  
  excludeFrames(file__in_contentA__path, outPath, in_timeA, file__out_log__fileObject)  

  file__out_log__fileObject.flush()  
  file__out_log__fileObject.write("============================================================\n")

  # Form frame for the B
  outPath = formMatching_getOutFilePath(dir__out__path, in_timeB, file__in_contentB__path, matchingName)

  getScopedPrinter().print("Forming frame image for [{name}]".format(
    name = getFSItemName(outPath, False))\
  )

  excludeFrames(file__in_contentB__path, outPath, in_timeB, file__out_log__fileObject)

  # Footing actions

  time = getSimpleProfiler().finish("MatchingFramesForming")
  getScopedPrinter().print("*** Time taken: {time} seconds".format(\
    time = round(time.total_seconds(), 3)\
  ))

  getScopedPrinter().scopeOut()

