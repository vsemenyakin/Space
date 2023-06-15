
def indexOfOneOf(string, symbols):
  index = 0
  for symbol in string:
    if symbol in symbols:
      return index

    index += 1

  return -1
