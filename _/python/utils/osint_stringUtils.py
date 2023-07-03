
def getStringBetween(main, start, end):

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
  
  return main[startIndex:endIndex]
  
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

def findMatchedSubstring(string, possibleSubstrings, caseSensitive = False):

  if caseSensitive:

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