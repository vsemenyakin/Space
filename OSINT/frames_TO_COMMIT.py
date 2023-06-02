# For file actions
import os 
import shutil
import math

# For executable call
import subprocess

# stringWithPossibleArguments : string
def excludeRawArguments(stringWithPossibleArguments):
  argumentsStart = stringWithPossibleArguments.find('@')
  
  if argumentsStart == -1:
    return None
  
  argumentsEnd = stringWithPossibleArguments.find('@', argumentsStart + 1)
  if argumentsEnd == -1:
    return None

  argumentsString = stringWithPossibleArguments[argumentsStart+1:argumentsEnd]
  
  unstrippedRawArguments = argumentsString.split('_')
  return [unstrippedRawArgument.strip() for unstrippedRawArgument in unstrippedRawArguments]

def stringWithoutArguments(stringWithPossibleArguments):
  
  #Just find first "@" symbols
  argumentsStart = stringWithPossibleArguments.find('@')
  if argumentsStart == -1:
    return stringWithPossibleArguments
  
  argumentsEnd = stringWithPossibleArguments.find('@', argumentsStart + 1)
  if argumentsStart == -1:
    return stringWithPossibleArguments
  
  return stringWithPossibleArguments[argumentsEnd+1:len(stringWithPossibleArguments)].lstrip()

# ==============================
class Int:
  def __init__(self, value):
    self.value = value

  value = 0

# ------------------------------
# Constructs "OptionalInt" from
# string
#
# [string : string]
#   string to parse value from
#
# [{ret} : IntRange]
#   range if it was succefully
#   created or "None" otherwise
# ------------------------------
def parseInt(string):
  result = None
  
  try:
    result = Int(int(string))
  except ValueError:
    result = None
  
  return result

# ==============================
class IntRange:
  begin = None
  end = None

# ------------------------------
# Constructs range from string
#
# [string : string]
#   string to parse value from
#
# [{ret} : IntRange]
#   range if it was succefully
#   created or "None" otherwise
# ------------------------------
def parseRange(string):

  possibleRangeLimitStrings = string.split('-')
  possibleLimitsCount = len(possibleRangeLimitStrings)
  
  if possibleLimitsCount >= 1 and possibleLimitsCount <= 2:

    possibleBegin = parseInt(possibleRangeLimitStrings[0].strip())
    if possibleBegin == None:
      return None
    result = IntRange()
    result.begin = possibleBegin
    
    if possibleLimitsCount == 1:
      return result
    
    possibleEnd = parseInt(possibleRangeLimitStrings[1].strip())
    if possibleEnd == None:
      return None    

    result.end = possibleEnd
    return result

  return None

# raw_arguments : string[]
def parseRanges(rawArguments):

  if rawArguments == None:
    return None

  possibleResult = [parseRange(rawArgument) for rawArgument in rawArguments]
  if None in possibleResult:
    return None
  
  return possibleResult

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def getFileNameWithoutExtension(file_in_path):
  return os.path.basename(file_in_path).split('.')[0]

def mkDirSafe(dir__path):
  try:
    os.mkdir(dir__path)
    return True
  except:
    return False

def rmDirSafe(dir__path):
  try:
    shutil.rmtree(dir__path)
    return True
  except:
    return False

# ================================ Actions with video

class ExcludeFrames_Settings:
  doCleanArgumentsFromInFile = True
  doIncludeFileNameIntoFrames = False

def excludeFrames(file__in__path, dir__out__path, framesRange, step, settings = ExcludeFrames_Settings()):

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
  timeRange_defaultBegin = 0
  framesRange_actualBegin = framesRange.begin.value if hasBegin else 0

  framesRange_actualEnd = 0
  hasEnd = (framesRange != None) and (framesRange.end != None) 
  if hasEnd:
    framesRange_actualEnd = framesRange.end.value
  else:
    possibleVideoDuration = getVideoDuration(file__in__path)
    if possibleVideoDuration == None:
      return
    framesRange_actualEnd = possibleVideoDuration.value
  
  print("=== Start forming frames range [" ,\
    framesRange_actualBegin , " - " , framesRange_actualEnd ,\
    "] with step [" , step ,\
    "] for video [" , outNaming , "]")
  
  for frameTime in range(framesRange_actualBegin, framesRange_actualEnd, step):
    frameTime__asString = str(frameTime)

    # Form name of the frame output file
    file__out_result_frame__name = frameTime__asString
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
    execArguments.extend(["-ss", frameTime__asString])

    #[3] Mode of excluding: exclude one frame
    execArguments.extend(["-frames:v", "1"])
    
    #[4] Name of the output file
    execArguments.extend([ file__out_result_frame__path ])

    # Call exec
    
    print("Forming frame for frame at [" , frameTime__asString , "seconds ]")
    
    subprocess.check_call(execArguments,\
      stdout = file__out_result_log__fileObject,\
      stderr = file__out_result_log__fileObject)
    
    file__out_result_log__fileObject.flush()
    file__out_result_log__fileObject.write("============================================================\n")

# ----------------------------------
    
def getVideoDuration(file__in__path):
  
  execArguments = ["ffprobe"]
  execArguments.extend(["-i", file__in__path])
  execArguments.extend(["-show_entries"])
  execArguments.extend(["format=duration"])
  execArguments.extend([ "-of", "default=noprint_wrappers=1:nokey=1" ])

  try:  
    ffprobe__process = subprocess.run(execArguments, capture_output=True)
  except:
    return None
  
  if ffprobe__process.returncode != 0:
    return None
  
  result_string = ffprobe__process.stdout.decode().strip()
  result_float = 0.0
  try:
    result_float = float(result_string)
  except:
    return None
  
  return Int(math.floor(result_float))
      
# ================================= Settings

files__inIgnore__name = [".gitignore"]
dir__in__name = "in"
dir__out__name = "out"
step = 5

# ================================= Utility call

dir__current__path = os.getcwd()
dir__in__path = os.path.join(dir__current__path, dir__in__name)
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