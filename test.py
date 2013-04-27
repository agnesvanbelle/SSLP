import sys


debug = True

""" 
  The Main class contains filenames (could be extended to use command-line arguments) and starts everything
  The Reader class is used to read - line by line - the relevant stuff from the three files 
  The Extractor class extracts phrases (using Reader)
  
  In 'Extractor.parseSentencePair(..)':
  i1, i2 = dutch indices
  j1, j2 = english indices
  (i.e. treat dutch as source)
  
"""

class Extractor(object): 
  """ 
    extract phrases
  """ 
  maxPhraseLen = 4 
  reader = None
  
  table_nl = {}
  table_en = {}
  table_nl_en = {}
  
  total_extracted = 0
  
  unique_nl = 0
  unique_en = 0
  unique_nl_en = 0
  
  def __init__(self, reader):
    self.reader = reader
  
  # extract phrases for all sentence pairs  (provided by the "Reader")
  def extract(self):   
      self.reader.line_list_aligns = "Meaningless init value because python had no do..while"
      while (self.reader.line_list_aligns != None and self.reader.counter < 1): # the fixed limit is only for debug 
        self.reader.load_next_line()
        if (self.reader.line_list_aligns != None):
          # parse phrases using  the dutch sentence, the english sentence and their alignments-list
          self.parseSentencePair(self.reader.line_list_aligns, self.reader.line_nl_words, self.reader.line_en_words)
      
      sys.stdout.write('\n')
      sys.stdout.write('Extracted ' + str(self.total_extracted) + ' phrase pairs \n' +
                        '\t unique ones for nl: ' + str(self.unique_nl) + '\n'+ 
                        '\t unique ones for en: ' + str(self.unique_en) + '\n'+
                        '\t unique pairs: ' + str(self.unique_nl_en) + '\n')
  
                      
  #extract phrases from one sentence pair
  def parseSentencePair(self, alignments, list_nl, list_en):
    sys.stdout.write('\n pair '+ str(self.reader.counter-1) + ':\n')
    print alignments
    print list_nl
    print list_en
    #string_nl = " ".join(list_nl)
    #string_en = " ".join(list_en)
    #print string_nl
    #print string_en
    
    totalExtractedThisPhrase = 0 
    
    for i1 in range(0, len(list_nl)):
      for i2 in range(i1, min(i1+self.maxPhraseLen, len(list_nl))):        
        
        # the considered dutch words
        list_nlWords = range(i1, i2+1)
        
        # get the english words aligned to the considered dutch words
        list_enWordsAligned = []        
        for i in list_nlWords:
          list_enWordsAligned.extend(self.get_possible_alignments(alignments, i, 'nl'))  
        
        list_enWordsAligned.sort()
        
        #check if the set of english words are consecutive with the exception
        #of possible unaligned words (i.e. the indices of the found aligned english words
        #can skip a number so long as that number is also not in the full alignments list)
        consecutive = self.checkConsecutive(list_enWordsAligned, alignments)
        
        #debug info
        if(debug):
          sys.stdout.write('\n')
          sys.stdout.write(str(list_nlWords) + '==> ' + str(list_enWordsAligned) + '\n')
          sys.stdout.write(self.getSubstring(list_nl, list_nlWords) + 
                            ' ==> ' +  
                            self.getSubstring(list_en, list_enWordsAligned) + '\n')
          if (consecutive):
            sys.stdout.write('is consecutive\n')
          else:
            sys.stdout.write('is NOT consecutive\n')        
        
        
        if(consecutive):
          # check the other way: if the aligned english words (j's) also map 
          # only to the considered, consecutive, dutch words (i's) (list_nlWords)
          j1 = list_enWordsAligned[0]
          j2 = list_enWordsAligned[-1]
          
          list_nlWordsAligned = []
          
          for j in range(j1, j2+1):
            list_nlWordsAligned.extend(self.get_possible_alignments(alignments, j, 'en'))
          
          list_nlWordsAligned.sort()       
          
          # if so, the alignment is consistent
          consistent = self.containsIndices(list_nlWords, list_nlWordsAligned)
          
          #debug info
          if(debug):
            sys.stdout.write('Re-mapped dutch words: ' + str(list_nlWordsAligned) + '\n')          
            if(consistent):
              sys.stdout.write('Consistent.\n')
            else:
              sys.stdout.write('NOT consistent.\n')
              
          if consistent:
            #update stats
            self.total_extracted = self.total_extracted + 1
            totalExtractedThisPhrase = totalExtractedThisPhrase + 1
            
            nlString = self.getSubstring(list_nl, list_nlWords)
            if nlString in self.table_nl:
              self.table_nl[nlString] = self.table_nl[nlString] + 1              
            else:
              self.table_nl[nlString] = 1
              self.unique_nl = self.unique_nl + 1
            
            
            enString = self.getSubstring(list_en, list_enWordsAligned)
            if enString in self.table_en:
              self.table_en[enString] = self.table_en[enString] + 1              
            else:
              self.table_en[enString] = 1
              self.unique_en = self.unique_en + 1
            
          
            nl_enString = (nlString , enString) #tuple
            if nl_enString in self.table_nl_en:
              self.table_nl_en[nenString] = self.table_nl_en[enString] + 1              
            else:
              self.table_nl_en[enString] = 1
              self.unique_nl_en = self.unique_nl_en + 1
            
            # ===> TODO:
            # check for unaligned words in english phrase
            
            
            #~j2b = j2 + 1
            #~while(j2b < min(i1+self.maxPhraseLen, len(list_en))):
              #~if (self.isEnUnaligned(j2b, alignments)):                
                #~# add phrase
            #~
            #~j2b = j2  
            #~j1 = j1 - 1            
            #~while(j1 > 0 and j2b-j1 < self.maxPhraseLen):
              #~if (self.isEnUnaligned(j1, alignments)):
                 #~# add phrase
              #~
              #~j2b = j2 + 1
            
    
    if debug:
      sys.stdout.write('\nWith this sentence pair , \n')
      sys.stdout.write('we have extracted ' + str(totalExtractedThisPhrase) + ' phrase pairs \n')
          
  
  # check if the english word is unaligned
  def isEnUnaligned(self, enIndex, alignments):
    
    lenAlignments = len(alignments)
    
    i = 0
    while (i < lenAlignments and alignments[i][1] <= enIndex):
      if (alignments[i][1] == enIndex):
        return False
      i = i + 1
    
    return True
    
  # get the words in the word-list "line_list" that the indices
  # in "aligned_list" point to
  # return them as a string
  def getSubstring(self,line_list, aligned_list):
    wordList = map((lambda x : line_list[x]), aligned_list)
    return " ".join(wordList)
  
  # note alignments are ordered on english order (y)
  # and the list of english words (indices) should be sorted before too
  # otherwise this doesn't work!
  def checkConsecutive(self, list_enWords, alignments):
    
    lenAlignments = len(alignments)
    lenEnWords = len(list_enWords)
    
    if (lenEnWords== 0): # no aligned words
      return False   
    
    for i in range(0, lenAlignments):
      alignment_pair = alignments[i]
      
      if (alignment_pair[1] > list_enWords[0]):
        break
      if (alignment_pair[1] == list_enWords[0]):
        alignments2 = alignments
        j = 0
        while(j < lenEnWords):
          if (alignments2[i+j][1] != list_enWords[0+j]):
            break
          j = j + 1
        if (j == lenEnWords):
          return True
    return False

  #not used
  #def containsSublist(self, lst, sublst):
    #n = len(sublst)
    #return any((sublst == lst[i:i+n]) for i in xrange(len(lst)-n+1))
  
  #checks if all (posisble duplicates) elements of nlWordsAligned
  #are a member of nlWords
  #assumes both lists of indices are sorted
  def containsIndices(self, nlWords, nlWordsAligned):
    lenNlWordsAligned = len(nlWordsAligned)
    lenNlWords = len(nlWords)
    
    i = 0
    j = 0
    
    while (i < lenNlWordsAligned and j < lenNlWords):
      if (nlWordsAligned[i] < nlWords[j]): # e.g. (24, 25, 25) can never be subset of (25, 26, 27)
        #sys.stdout.write(str(nlWordsAligned[i]) + ' < ' + str(nlWords[j]))
        return False
        
      if (nlWordsAligned[i] == nlWords[j]):
        i = i + 1
      else:
        j = j + 1
    
    return True
  
  #not used
  #returns the list of tuples sorted by the second element
  #def sort_by_y(self, list_aligns):
  #  return sorted(list_aligns, key=lambda x : x[1])

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
      pairList = pair.split('-')
      x = int(pairList[0])
      y = int(pairList[1])
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
  #path = '/run/media/root/ss-ntfs/3.Documents/huiswerk_20122013/SSLP/project1/aligned-data/'
  path = 'aligned-data/'
  
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
