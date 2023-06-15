
class ScopedPrinter:

  offsetStringMember = "  "

  def __init__(self):
    self.offsetString = ""

  def print(self, string):
    print(self.offsetString + string)

  def printAndScopeOut(self, string):
    print(self.offsetString + string)
    self.scopeOut()

  def scopeIn(self):
    self.offsetString += ScopedPrinter.offsetStringMember
  
  def scopeOut(self):
    self.offsetString = self.offsetString[:-len(ScopedPrinter.offsetStringMember)]

  commonInstance = None


def getScopedPrinter():

  if ScopedPrinter.commonInstance == None:
    ScopedPrinter.commonInstance = ScopedPrinter()
    
  return ScopedPrinter.commonInstance
