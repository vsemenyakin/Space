
import datetime

class SimpleProfiler:

  def __init__(self):
    self.startTimes = { }

  def start(self, timerMarker = "<default>"):
    if timerMarker in self.startTimes:
      #ERROR: Trying to start time that was currently started
      return
  
    self.startTimes[timerMarker] = datetime.datetime.now()
  
  def finish(self, timerMarker = "<default>"):
    if not timerMarker in self.startTimes:
      #ERROR: Trying to stop timer that was not started
      return None

    delta = datetime.datetime.now() - self.startTimes[timerMarker]
    del self.startTimes[timerMarker]
  
    return delta
  

  commonInstance = None
 
# =======================================================
 
def getSimpleProfiler():

  if SimpleProfiler.commonInstance == None:
    SimpleProfiler.commonInstance = SimpleProfiler()
    
  return SimpleProfiler.commonInstance
