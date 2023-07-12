
def getStringBetween(main, start, end, trimmed = False):

  startIndexBegin = main.find(start)
  if startIndexBegin == -1:
    return None
  startIndex = startIndexBegin + len(start)
  
  if end == None:
    return main[startIndex:].strip()
  
  startIndexWithoutOffset = main[startIndex:].find(end)
  if startIndexWithoutOffset == -1:
    return None
  endIndex = startIndex + startIndexWithoutOffset
  
  return main[startIndex:endIndex].strip()
  
def insertStringBetween(main, start, end, stringToInsert):

  startIndexBegin = main.find(start)
  if startIndexBegin == -1:
    return None
  startIndex = startIndexBegin + len(start)
  
  if end == None:
    return main[startIndex:]
  
  startIndexWithoutOffset = main[startIndex:].find(end)
  if startIndexWithoutOffset == -1:
    return None
  endIndex = startIndex + startIndexWithoutOffset
  
  return main[:startIndex] + stringToInsert + main[endIndex:]

def indexOfOneOf(string, symbols):
  index = 0
  for symbol in string:
    if symbol in symbols:
      return index

    index += 1

  return -1

def findMatchedSubstring(string, possibleSubstrings, matchCase = False):

  if matchCase:

    for possibleSubstring in possibleSubstrings:
      index = string.find(possibleSubstring)
      if index == -1:
        continue
      
      return possibleSubstring
    
  else:
  
    casefoldString = string.casefold()  
    
    for possibleSubstring in possibleSubstrings:
      index = casefoldString.find(possibleSubstring.casefold())
      if index == -1:
        continue
        
      return possibleSubstring

  return None
  
#Batch escapes  
#TODO: Move to file like "winBatchUtils"
#
#Based on:
# 1. [https://ss64.com/nt/syntax-esc.html]
#
#Links that was used, but not helped:
# 1. [https://stackoverflow.com/a/33868784]
# 2. [https://www.robvanderwoude.com/escapechars.php]


def batchStringEscaping_forEchoCommand(string, escapeOnlyThisSymbols = None):

  resultString = ""

  percentEscapedSymbols = "%"
  oneUpArrowEscapedSymbols = "^"
  threeUpArrowsEscapedSymbols = "&<>|'`,;=()!\"\\[].*?"

  for char in string:
    if escapeOnlyThisSymbols != None and (not char in escapeOnlyThisSymbols):
      resultString = resultString + char
    elif char in percentEscapedSymbols:
      resultString = resultString + "%" + char
    elif char in oneUpArrowEscapedSymbols:
      resultString = resultString + "^" + char
    elif char in threeUpArrowsEscapedSymbols:
      resultString = resultString + "^^^" + char
    else:
      resultString = resultString + char

  return resultString

def batchStringEscaping_forString(string, escapeOnlyThisSymbols = None):

  resultString = ""

  percentEscapedSymbols = "%"

  for char in string:
    if escapeOnlyThisSymbols != None and (not char in escapeOnlyThisSymbols):
      resultString = resultString + char
    elif char in percentEscapedSymbols:
      resultString = resultString + "%" + char
    else:
      resultString = resultString + char
      
  return resultString
