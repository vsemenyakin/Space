from osint_utils import indexOfOneOf
from enum import Enum

class ParseResult(Enum):
  Finished = 1
  Continue = 2
  Failed = 3

def parseArguments(arguments, parsers, ignoreWhitespaceArguments = True):

  currentContinueParser = None

  for argument in arguments:
    
    if ignoreWhitespaceArguments and argument.isspace():
      continue
    
    lastParseResult = ParseResult.Failed
    
    if currentContinueParser != None:
      lastParseResult = currentContinueParser.parse(argument)
      if lastParseResult == ParseResult.Finished:
        currentContinueParser = None
      elif lastParseResult == ParseResult.Continue:
        continue
      elif lastParseResult == ParseResult.Failed:
        # Started continue parser cannot fail
        return ParseResult.Failed
   
    for possibleParser in parsers:
      lastParseResult = possibleParser.parse(argument)
      if lastParseResult == ParseResult.Finished:
        break
      elif lastParseResult == ParseResult.Continue:
        currentContinueParser = possibleParser
        break
      elif lastParseResult == ParseResult.Failed:
        continue

    # No parser was finished for arguments. Error place
    if lastParseResult == ParseResult.Failed:
      return ParseResult.Failed

  if currentContinueParser:
    currentContinueParser.finish()

  return ParseResult.Finished

class ArgumentParser_Named():

  # expectedName : string
  # action :       func(value : string)
  def __init__(self, expectedNames, resultAction, possibleDelimiters = ['=', ':'], caseSensitive = False):
    self.expectedNames = expectedNames
    self.possibleDelimiters = possibleDelimiters
    self.resultAction = resultAction
    self.caseSensitive = caseSensitive

  def parse(self, argument):
    delimiter = '='
    
    delimiterIndex = indexOfOneOf(argument, self.possibleDelimiters)
    if delimiterIndex == -1:
      return ParseResult.Failed
   
    name = argument[0:delimiterIndex].strip()
    if not self.isExpectedName(name):
      return ParseResult.Failed
    
    value = argument[delimiterIndex + 1:].strip() 

    self.resultAction(value)
    
    return ParseResult.Finished

  def isExpectedName(self, possibleExpectedName):
    if self.caseSensitive:
      return possibleExpectedName in self.expectedNames
  
    for expectedName in self.expectedNames:
      if possibleExpectedName.casefold() == expectedName.casefold():
        return True
    
    return False
