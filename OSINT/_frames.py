# For file actions
import os 
import shutil
import math
import datetime 
from enum import Enum

# For executable call
import subprocess

# ================================ Actions with video

class ExcludeFrames_Settings:
  def __init__(self):
    self.doCleanArgumentsFromInFile = True
    self.doIncludeFileNameIntoFrames = False

# >>> Markdown to text online editor
# https://dillinger.io/
# https://www.w3docs.com/nx/marked

def excludeFrames(file__in__path, dir__out__path, framesRange, step, settings = ExcludeFrames_Settings()):

  #TODO:
  # 1. Create folders per range named as range
  # 2. Create file with 

  # Constants
  file__log__nameAndExt = "log.txt"

  # Prepare out naming
  file__in__absPath = os.path.abspath(file__in__path)
  file__in__name = getFileNameWithoutExtension(file__in__path)

  outNaming = stringWithoutArguments(file__in__name) if settings.doCleanArgumentsFromInFile else file__in__name

  # Prepare "outForResult" directory
  
  dir__out_result__absPath = os.path.join(dir__out__path, outNaming)
  mkDirSafe(dir__out_result__absPath)
  
  # Prepare log file in the "outForResult" directory
  file__out_result_log__absPath = os.path.join(dir__out_result__absPath, file__log__nameAndExt)
  file__out_result_log__fileObject = open(file__out_result_log__absPath, 'a') 

  # Get actual range info
  hasBegin = (framesRange != None) and (framesRange.begin != None)
  timeRange_defaultBegin = datetime.timedelta()
  framesRange_actualBegin = framesRange.begin if hasBegin else timeRange_defaultBegin

  hasEnd = (framesRange != None) and (framesRange.end != None) 
  framesRange_actualEnd = datetime.timedelta()
  if hasEnd:
    framesRange_actualEnd = framesRange.end
  else:
    possibleVideoDuration = getVideoDuration(file__in__path)
    if possibleVideoDuration == None:
      return
    framesRange_actualEnd = possibleVideoDuration

  # Convert to seconds format
  framesRange_actualBegin__int = math.floor(framesRange_actualBegin.total_seconds())
  framesRange_actualEnd__int = math.floor(framesRange_actualEnd.total_seconds())
  
  # Form frames
  print("=== Start forming frames range [" ,\
    str(framesRange_actualBegin__int) , " - " , str(framesRange_actualEnd__int) ,\
    "] with step [" , step ,\
    "] for video [" , outNaming , "]")
  
  for frameTimeSeconds in range(framesRange_actualBegin__int, framesRange_actualEnd__int, step):
    frameTimeForProcess__string = str(frameTimeSeconds)

    # Form name of the frame output file
    file__out_result_frame__name = str(frameTimeSeconds)
    if settings.doIncludeFileNameIntoFrames:
      file__out_result_frame__name += "_" + outNaming
      
    file__out_result_frame__nameAndExt = file__out_result_frame__name + "." + "png"
    file__out_result_frame__path = os.path.join(dir__out_result__absPath, file__out_result_frame__nameAndExt)
    
    # Prepare arguments
    #[0] Path to ffmpeg exec
    execArguments = ["ffmpeg"]
    
    #[1] Name of the input file
    execArguments.extend(["-i", file__in__absPath])
    
    #[2] Time of the frame to exclude
    execArguments.extend(["-ss", frameTimeForProcess__string])

    #[3] Mode of excluding: exclude one frame
    execArguments.extend(["-frames:v", "1"])
    
    #[4] Name of the output file
    execArguments.extend([ file__out_result_frame__path ])

    # Call exec
    
    print("Forming frame for frame at [",\
      timeDeltaToString(datetime.timedelta(seconds = frameTimeSeconds)),\
      "]")
    
    subprocess.check_call(execArguments,\
      stdout = file__out_result_log__fileObject,\
      stderr = file__out_result_log__fileObject)
    
    file__out_result_log__fileObject.flush()
    file__out_result_log__fileObject.write("============================================================\n")

# ----------------------------------

      
# ================================= Settings

files__inIgnore__name = [".gitignore"]
dir__out__name = "out"
step = 5

# ================================= Utility call

dir__current__path = os.getcwd()

dir__out__path = os.path.join(dir__current__path, dir__out__name)

# Clear "out" directory
rmDirSafe(dir__out__path)
mkDirSafe(dir__out__path)

for fsItem__in_member__name in os.listdir(dir__in__path):
  if fsItem__in_member__name in files__inIgnore__name:
    continue

  fsItem__in_member__path = os.path.join(dir__in__path, fsItem__in_member__name)
    
  if os.path.isdir(fsItem__in_member__path):
    continue
  file__in_member__path = fsItem__in_member__path

  file__in_member__name = getFileNameWithoutExtension(file__in_member__path)
  rawArguments = excludeRawArguments(file__in_member__name)
  rangesToExclude = parseRanges(rawArguments)

  if rangesToExclude != None:
    for rangeToExclude in rangesToExclude:
      excludeFrames(file__in_member__path, dir__out__path, rangeToExclude, step)
  else:
    excludeFrames(file__in_member__path, dir__out__path, None, step)
