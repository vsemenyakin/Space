import subprocess
import datetime
import math
import pathlib

def getFFMPEGDirPath():

  return pathlib.Path(__file__).parent.parent.parent / "ffmpg" / "bin"

def getVideoDuration(file__in__path):
  
  execArguments = [str(getFFMPEGDirPath() / "ffprobe")]
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
  
  return datetime.timedelta(seconds = math.floor(result_float))


def excludeFrames(file__in__path, file__out__path, frameTime, log__fileObject = None):

  frameTime_float = frameTime.total_seconds()

  # Prepare arguments
  #[0] Path to ffmpeg exec
  execArguments = [str(getFFMPEGDirPath() / "ffmpeg")]
  
  print(execArguments[0])
  
  #[1] Name of the input file
  execArguments.extend(["-i", file__in__path])

  #[2] Time of the frame to exclude
  execArguments.extend(["-ss", str(frameTime_float)])
  
  #[3] Mode of excluding: exclude one frame
  execArguments.extend(["-frames:v", "1"])
  
  #[4] Name of the output file
  execArguments.extend([ file__out__path ])
    
  if log__fileObject != None:
    process = subprocess.check_call(execArguments,\
      stdout = log__fileObject,\
      stderr = log__fileObject)  
  
  else:
    process = subprocess.check_call(execArguments)

  return process
