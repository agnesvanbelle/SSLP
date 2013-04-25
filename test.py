import sys

class Reader(object):
  """read file"""
  inputFileName = "";
  def __init__(self, inputFileName=None):
    if (inputFileName != None):
      self.inputFileName = inputFileName

class Main(object):
  reader = Reader("blafile.txt")
  message = "" 
  def __init__(self):
    self.message = "Hi"
  
  def run(self):
    print self.message
    print self.reader.inputFileName

if __name__ == '__main__': #if this file is called by python test.py
  main = Main()
  main.run()
