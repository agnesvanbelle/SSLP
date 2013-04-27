import sys


  

class Extractor(object): 
  """ 
    extract phrases
  """ 
  maxPhraseLen = 4 
  reader = None
  
  table_SP = {}
  table_TP = {}
  table_SP_TP = {}
  
  def __init__(self, reader):
    self.reader = reader
  
  def extract(self):   
      self.reader.line_list_aligns = "Meaningless init value because python had no do..while"
      while (self.reader.line_list_aligns != None and self.reader.counter < 3):
        self.reader.load_next_line()
        if (self.reader.line_list_aligns != None):
          self.parsePhrase(self.reader.line_list_aligns, self.reader.line_nl_words, self.reader.line_en_words)

  def parsePhrase(self, alignments, list_nl, list_en):
    sys.stdout.write('\n pair '+ str(self.reader.counter-1) + ':\n')
    print alignments
    print list_nl
    print list_en
    string_nl = " ".join(list_nl)
    string_en = " ".join(list_en)
    #print string_nl
    #print string_en
    
    for i1 in range(0, len(list_nl)):
      for i2 in range(i1, min(i1+self.maxPhraseLen, len(list_nl))):
        list_enWordsAligned = []
        for i in range(i1, i2+1):
          list_enWordsAligned.extend(self.get_possible_alignments(alignments, i, 'nl'))
          print list_enWordsAligned
        #string_enWordsAligned = " ".join(list_enWordsAligned)
        #print string_enWordsAligned
        sys.stdout.write(self.getSubstring(list_nl, range(i1,i2+1)) + 
                          ' ==> ' +  
                          self.getSubstring(list_en, list_enWordsAligned) + '\n')
      #break
  
  def getSubstring(self,line_list, aligned_list):
    wordList = map((lambda x : line_list[x]), aligned_list)
    return " ".join(wordList)
    
  #returns the list of tuples sorted by the second element
  def sort_by_y(self, list_aligns):
    return sorted(list_aligns, key=lambda x : x[1])

  #returns all the possible alignments of an element
  #to return all the possible alignments of element y, use sort_by_y() first
  #^it traverses whole list so sorting not needed
  def get_possible_alignments(self, list_aligns, nr, language):
    if (language == 'en'): #source language
      return [item[0] for item in list_aligns if item[1]==nr]
    else:
      return [item[1] for item in list_aligns if item[0]==nr]
  

class Reader(object):
  """ 
    read lines from files
  """ 
  inputFileName = "";
  
  aligns = ''
  nl = ''
  en = ''
  
  
  
  f_aligns = None
  f_nl = None
  f_en = None
  
  counter = 0
 
  line_list_aligns = None
  line_nl_words = None
  line_en_words = None
  
  def __init__(self, path, alignsFileName, nlFileName, enFileName):
    self.aligns = path+alignsFileName
    self.nl = path+nlFileName
    self.en = path+enFileName
    
    
  
  def load_data(self):
    #open the input files
    self.f_aligns = open(self.aligns)
    self.f_nl = open(self.nl)
    self.f_en = open(self.en)

    self.counter = 0
  
  #get the next line of each file
  def load_next_line(self):
    
    if (self.f_aligns == None):
      self.load_data()      
    
    
    line_aligns = self.f_aligns.readline()
    line_nl = self.f_nl.readline()
    line_en = self.f_en.readline()

    if not line_aligns: #EOF
      sys.stdout.write('\nEnd of files reached\n')
      self.f_aligns.close()
      self.f_nl.close()
      self.f_en.close()
      self.line_list_aligns = None
      
    else:      
      self.line_list_aligns = self.get_align_list(line_aligns)
      self.line_nl_words = self.get_words (line_nl)
      self.line_en_words = self.get_words (line_en)

      self.counter = self.counter+1
    
  def get_align_list(self, line):
    splitted = line.split()
    pairs = []
    for pair in splitted:
      dot_pos = pair.find('-')
      x = int(pair[0:dot_pos])
      y = int(pair[dot_pos+1])
      pairs.append((x,y))
    return pairs

  def get_words (self, line):
    return line.split()
    


class Main(object):
  """
    main class
    start everything 
    initialize file names
  """
  
  #path = '/Users/nikos/Downloads/aligned-data/'
  path = '/run/media/root/ss-ntfs/3.Documents/huiswerk_20122013/SSLP/project1/aligned-data/'
  
  alignsFileName = 'aligned.nl-en_short'
  nlFileName = 'europarl.nl-en.nl_short'
  enFileName = 'europarl.nl-en.en_short'
  
  reader = Reader(path, alignsFileName, nlFileName, enFileName)
  extractor = Extractor(reader)
  
  
  def __init__(self):
    pass
  
  def run(self):
    sys.stdout.write('parsing alignments in \"' + self.alignsFileName + 
                     '\", for \"' + self.nlFileName + '\" and \"' + self.enFileName + 
                     '\" from directory \"' + self.path + '\"'+ '\n')

    self.extractor.extract()

### used to call Main.run()
if __name__ == '__main__': #if this file is called by python test.py
  main = Main()
  main.run()
