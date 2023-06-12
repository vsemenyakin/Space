
def stringBetween(main, start, end):

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