import datetime
import os
import math

import sys
sys.path.insert(0, '../../_/python_utils')

from osint_URLParsing import tryMakeTimestampedURL
from osint_timeUtils import timeDeltaToString
from osint_fileUtils import mkDirSafe
from osint_videoUtils import excludeFrames

# ================================ Frames =========================================

def formSourceRangeFrames(in_content__path, dir__out_source__path, rangeStart, rangeEnd, step):

  dir__out_source_frames__path = formSourceRangeFrames_getRangeFramesDirPath(\
    dir__out_source__path, rangeStart, rangeEnd)

  mkDirSafe(dir__out_source_frames__path)

  framesRange_actualBegin__int = math.floor(rangeStart.total_seconds())
  framesRange_actualEnd__int = math.floor(rangeEnd.total_seconds())
  
  #TODO: Prepare log file!
  file__out_source_frames_log__fileObject = open(\
    formSourceRangeFrames_getLogFilePath(dir__out_source_frames__path), 'a')  
  
  for frameTimeSeconds in range(framesRange_actualBegin__int, framesRange_actualEnd__int, step):

    frameTime = datetime.timedelta(seconds = frameTimeSeconds)

    dir__out_source_frames_frame__name = timeDeltaToString(frameTime,\
      formSourceRangeFrames_getTimeFormat_forFrame())
    dir__out_source_frames_frame__nameAndExt = dir__out_source_frames_frame__name + "." + "png"
    dir__out_source_frames_frame__path = os.path.join(\
      dir__out_source_frames__path,\
      dir__out_source_frames_frame__nameAndExt)

    print("Forming image for frame at [{timeString}]".format(\
      timeString = timeDeltaToString(frameTime, formSourceRangeFrames_getTimeFormat_forFrame()))\
    )

    excludeFrames(in_content__path, dir__out_source_frames_frame__path, frameTime,\
      file__out_source_frames_log__fileObject)
    file__out_source_frames_log__fileObject.flush()
    
    file__out_source_frames_log__fileObject.write("============================================================\n")

# - - - - - - - - - - - - - - - - - - Private details - - - - - - - - - - - - - - - - - - 

def formSourceRangeFrames_getTimeFormat_forFramesDir():
  return "%M_%S"

def formSourceRangeFrames_getTimeFormat_forFrame():
  return "%M_%S"

# - - - - - - - - - - - - - - - - - - Private details - - - - - - - - - - - - - - - - - - 

def formSourceRangeFrames_getRangeFramesDirPath(dir__out_source__path, rangeStart, rangeEnd):

  #Note: ':' cannot be used as time delimiter because it is not allowed in Windows paths
  timeFormat = formSourceRangeFrames_getTimeFormat_forFramesDir()

  rangeStart__string = timeDeltaToString(rangeStart, timeFormat)
  rangeEnd__string = timeDeltaToString(rangeEnd, timeFormat)
  
  dir__range__name = "[{startText} - {endText}]".format(\
    startText = rangeStart__string,
    endText = rangeEnd__string)

  return os.path.join(dir__out_source__path, dir__range__name)

def formSourceRangeFrames_getLogFilePath(dir__out_source_frames__path):
  return os.path.join(dir__out_source_frames__path, "log.txt")

# ============================== Source text ======================================

def formSourceLines(settings):

  resultLines = []

  #Add header
  resultLines.append(settings.name)

  #Add details
  #!!! CURRENTLY NO IMPLEMENTATION !!!
  #TODO: Implement

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
    searchWorkaroundLink = settings.sourceURL
  ))
  
  return resultLines

# - - - - - - - - - - - - - - - - - - Private details - - - - - - - - - - - - - - - - - - 

def formSourceText_range(startTime, endTime, contentURL, backupURL):

  timeFormat = "%M:%S"
  
  sourceText = "[{startTime} - {endTime}]({link})".format(\
    startTime = timeDeltaToString(startTime, timeFormat),\
    endTime = timeDeltaToString(endTime, timeFormat),\
    link = tryMakeTimestampedURL(contentURL, startTime))
  
  backupText = "[Backup]({link})".format(\
    link = tryMakeTimestampedURL(backupURL, startTime))
  
  return "\[{source} | {backup}\] - Episode | Timeline".format(\
    source = sourceText,\
    backup = backupText)
