import sys
import os
import math
import cPickle as pickle


alignDir = 'aligned-data/'
tableDir = 'tables/'


alignsFileName = 'aligned.nl-en2'
nlFileName = 'europarl.nl-en.nl2'
enFileName = 'europarl.nl-en.en2'

basicDebug = True
moreDebug = False


table_nl_file = 'table_nl.dat'
table_en_file = 'table_en.dat'
table_nl_en_file = 'table_nl_en.dat'


MAXIMUM_READ_SENTENCES = 1000000  #10000 # for testing purposes

"""
  The Main class contains filenames (could be extended to use command-line arguments) and starts everything
  The Reader class is used to read - line by line - the relevant stuff from the three files
  The Extractor class extracts phrases (using Reader)
  The PhraseTables class hold the phrase tables

  In 'Extractor.parseSentencePair(..)':
  i1, i2 = dutch indices
  j1, j2 = english indices
  (i.e. treat dutch as source)

"""

class PhraseTables(object):
  """
    holds the phrase tables
    has methods to caulculate conditional probabilities etc.
  """

  # phrase tables are dictionaries
  table_nl = {} # contains log(pr(nl)) for all dutch phrases
  table_en = {} # contains log(pr(en)) for all english phrases
  table_nl_en = {} # contains log(pr(nl, en)) for all dutch&english phrase pairs
                    #from these three, pr(nl | en) and pr(en | nl) can be computed

  def __init__(self):
    pass

  # pr( en | nl)
  def getConditionalProbabilityEn(self, nl, en, log=False):
    nl_en = (nl , en)

    if (nl_en in self.table_nl_en):
      logP_en = self.table_nl_en[nl_en] - self.table_nl[nl]
      if log:
        return logP_en
      else:
        return math.exp(logP_en)
    return 0 # given en and/or nl phrase did not occur in tables

  # pr( nl | en )
  def getConditionalProbabilityNl(self, nl, en, log=False):
    nl_en = (nl , en)

    if (nl_en in self.table_nl_en):
      logP_nl = self.table_nl_en[nl_en] - self.table_en[en]
      if log:
        return logP_nl
      else:
        return math.exp(logP_nl)
    return 0 # given en and/or nl phrase did not occur in tables

  # pr(nl, en)
  def getJointProbability(self, nl, en, log=False):
    nl_en = (nl , en)

    if (nl_en in self.table_nl_en):
      logP_nl_en = self.table_nl_en[nl_en]
      if log:
        return logP_nl_en
      else:
        return math.exp(logP_nl_en)
    return 0 # given en & nl phrase pair did not occur in table

  # get phrase tables from files
  def readFromFiles(self, tablePath):
    f1 = open(tablePath +  table_nl_file, "rb")
    f2 = open(tablePath +  table_en_file, "rb")
    f3 = open(tablePath +  table_nl_en_file, "rb")

    self.table_nl = pickle.load( f1 )
    if basicDebug:
        sys.stdout.write(table_nl_file + ' read.\n')
    self.table_en = pickle.load( f2 )
    if basicDebug:
        sys.stdout.write(table_en_file + ' read.\n')
    self.table_nl_en = pickle.load( f3 )
    if basicDebug:
        sys.stdout.write(table_nl_en_file + ' read.\n')

    f1.close()
    f2.close()
    f3.close()

  # get phrase tables from given Extractor object
  def getFromExtractor(self, extractor):
    extractor.extract()
    self.table_nl = extractor.table_nl
    self.table_en = extractor.table_en
    self.table_nl_en = extractor.table_nl_en


class Extractor(object):
  """
    extract phrases
    write tables to files
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

  def __init__(self, reader, tablePath):
    self.reader = reader
    self.tablePath = tablePath

    if not os.path.exists(tablePath):
      os.makedirs(tablePath)


  # extract phrases for all sentence pairs  (provided by the "Reader")
  def extract(self):
      self.reader.line_list_aligns = "Meaningless init value because python had no do..while"
      while (self.reader.line_list_aligns != None and self.reader.counter < MAXIMUM_READ_SENTENCES): # the fixed limit is only for debug
        if basicDebug:
          if (self.reader.counter > 0 and self.reader.counter % 500 == 0):
            sys.stdout.write('Reached line ' + str(self.reader.counter) + ' \n')
        self.reader.load_next_line()
        if (self.reader.line_list_aligns != None):
          # parse phrases using  the dutch sentence, the english sentence and their alignments-list
          self.parseSentencePair(self.reader.line_list_aligns, self.reader.line_nl_words, self.reader.line_en_words)

      sys.stdout.write('\n')
      sys.stdout.write('Extracted ' + str(self.total_extracted) + ' phrase pairs \n' +
                        '\t unique phrases for nl: ' + str(self.unique_nl) + '\n'+
                        '\t unique phrases for en: ' + str(self.unique_en) + '\n'+
                        '\t unique pairs: ' + str(self.unique_nl_en) + '\n')



      sys.stdout.write('Writing to files...\n')

      self.normalizeTables() #make probabilities of the counts
      self.pickleTables()

      if basicDebug:
        self.writeTables()

      sys.stdout.write('Done writing to files.\n')



  def normalizeTables(self):

    for pair, value in self.table_nl_en.iteritems():
      value_new = math.log(value) - math.log(self.total_extracted)
      self.table_nl_en[pair] = value_new

    for nl, value in self.table_nl.iteritems():
      value_new = math.log(value) - math.log(self.total_extracted)
      self.table_nl[nl] = value_new

    for en, value in self.table_en.iteritems():
      value_new = math.log(value) - math.log(self.total_extracted)
      self.table_en[en] = value_new


  def makeConditionalTables(self):
    pass


  def pickleTables(self):
    f1 = open( self.tablePath + table_nl_file, "wb" );
    f2 = open( self.tablePath +  table_en_file, "wb" );
    f3 = open( self.tablePath +  table_nl_en_file, "wb" );

    pickle.dump(self.table_nl, f1)
    pickle.dump(self.table_en, f2)
    pickle.dump(self.table_nl_en, f3)

    f1.close()
    f2.close()
    f3.close()


  def writeTables(self):

    f1 = open( self.tablePath +  table_nl_file[:-4] + '_raw.txt', "wb" );
    f2 = open( self.tablePath +  table_en_file[:-4] + '_raw.txt', "wb" );
    f3 = open( self.tablePath +  table_nl_en_file[:-4] + '_raw.txt', "wb" );


    for nl, value in self.table_nl.iteritems():
      f1.write(str(value) + ' : ' + str(nl) + '\n')

    for en, value in self.table_en.iteritems():
      f2.write(str(value) + ' : ' + str(en) + '\n')

    for pair, value in self.table_nl_en.iteritems():
      f3.write(str(value) + ' : ' + str(pair) + '\n')

    f1.close()
    f2.close()
    f3.close()


  #extract phrases from one sentence pair
  def parseSentencePair(self, alignments, list_nl, list_en):

    if moreDebug:
      sys.stdout.write('\n pair '+ str(self.reader.counter-1) + ':\n')
      print alignments
      print list_nl
      print list_en

    

    
    totalExtractedThisPhrase = 0
    
    len_list_nl = len(list_nl)
    len_list_en = len(list_en)
    len_alignments = len(alignments)
    
    nl_to_en = [[100, -1] for i in range(len_list_nl)] #[minimum, maximum]
    en_to_nl = [[100, -1] for i in range(len_list_en)]
    
    #print nl_to_en
    
    for a_pair in alignments:
      #print a_pair
      
      nl_index = a_pair[0]
      en_index = a_pair[1]
      
      #sys.stdout.write('nl_index: ' + str(nl_index) + '\n')
      
      
      nl_to_en[nl_index][0] = min(en_index, nl_to_en[nl_index][0])
      nl_to_en[nl_index][1] = max(en_index, nl_to_en[nl_index][1])
      
      en_to_nl[en_index][0] = min(nl_index, en_to_nl[en_index][0])
      en_to_nl[en_index][1] = max(nl_index, en_to_nl[en_index][1])
      
      
      
      
    if moreDebug:
      print nl_to_en
      print en_to_nl
    
    
    
    
    for nl_index1 in range(0, len_list_nl-1): # do not check the period at the end
      if moreDebug:
        sys.stdout.write('nl_index1: ' + str(nl_index1) + '\n')
      
      
      enRange = nl_to_en[nl_index1]
      
      if (enRange != [100, -1]): #if aligned
        
        nlFromEnMin = min(en_to_nl[enRange[0]][0], en_to_nl[enRange[1]][0])
        nlFromEnMax = max(en_to_nl[enRange[0]][1], en_to_nl[enRange[1]][1])
        
        nl_index2 = nl_index1
        while(nl_index2 < min(nl_index1 + self.maxPhraseLen, len_list_nl)):
          if moreDebug:
            sys.stdout.write('\tnl_index2: ' + str(nl_index2) + ', ')
            sys.stdout.write('\tchecking: ' + self.getSubstring(list_nl, range(nl_index1, nl_index2+1)) + '\n')
          
          enRangeThisIndex = nl_to_en[nl_index2]
          
          if (enRangeThisIndex != [100, -1]):
            enRange = [min(enRange[0], enRangeThisIndex[0]), max(enRange[1], enRangeThisIndex[1])]
            
            if (enRange[1] - enRange[0] < self.maxPhraseLen):
              nlFromEnMin = min(nlFromEnMin, en_to_nl[enRange[0]][0], en_to_nl[enRange[1]][0])
              nlFromEnMax = max(nlFromEnMax, en_to_nl[enRange[0]][1], en_to_nl[enRange[1]][1])
              
              
              if nlFromEnMin < nl_index1:
                if moreDebug:
                  sys.stdout.write('\tnlFromEnMin < nl_index1: ' + str(nlFromEnMin) + ' < ' + str(nl_index1) + '\n')
                break
                
              elif nlFromEnMax > nl_index2:
                if moreDebug:
                  sys.stdout.write('\tnlFromEnMax > nl_index2: ' + str(nlFromEnMax) + ' > ' + str(nl_index2) + '\n')       
                nl_index2 = nlFromEnMax                     
                continue
              
              
              
              # got one
              elif [nl_index1, nl_index2] == [nlFromEnMin, nlFromEnMax] :
                if moreDebug:
                  sys.stdout.write ('\t' + str([nl_index1, nl_index2]) + ' == ' + str([nlFromEnMin, nlFromEnMax]) + '\n')
                  sys.stdout.write ('\t'+ self.getSubstring(list_nl, range(nl_index1, nl_index2+1)) + ' == ')
                  sys.stdout.write ( self.getSubstring(list_en, range(enRange[0], enRange[1]+1)) + '\n')
                              
                
                self.addPair(list_nl, list_en, nl_index1, nl_index2, enRange[0], enRange[1])
                totalExtractedThisPhrase += 1
                
                
                
                
                ####################
                #check for unaligned 
                ######################
                nl_unaligned_list = []    
                en_unaligned_list = []
                
                ## unaligned on dutch  side                                
                #above unlimited         
                nl_index2_copy = nl_index2 + 1
                while nl_index2_copy < min(nl_index1 + self.maxPhraseLen, len_list_nl) and nl_to_en[nl_index2_copy] == [100, -1] :
                  nl_unaligned_list.append([nl_index1, nl_index2_copy])
                  nl_index2_copy += 1
                
                # below unlimited
                nl_index1_copy = nl_index1 - 1
                while nl_index1_copy >= 0  and nl_to_en[nl_index1_copy] == [100,-1] :
                  nl_unaligned_list.append([nl_index1_copy, nl_index2])
                  
                  # above unlimited for this below-level
                  nl_index2_copy = nl_index2 + 1
                  while nl_index2_copy < min(nl_index1_copy + self.maxPhraseLen, len_list_nl)  and nl_to_en[nl_index2_copy] == [100, -1] :
                    nl_unaligned_list.append([nl_index1_copy, nl_index2_copy])
                    nl_index2_copy += 1                    
                  
                  nl_index1_copy -= 1

                ## unaligned on english  side
                en_index1 = enRange[0]
                en_index2 = enRange[1] 
                             
                #above unlimited         
                en_index2_copy = en_index2 + 1
                while en_index2_copy < min(en_index1 + self.maxPhraseLen, len_list_en) and en_to_nl[en_index2_copy] == [100, -1] :
                  en_unaligned_list.append([en_index1, en_index2_copy])
                  en_index2_copy += 1
                
                # below unlimited
                en_index1_copy = en_index1 - 1
                while en_index1_copy >= 0  and en_to_nl[en_index1_copy] == [100,-1] :
                  en_unaligned_list.append([en_index1_copy, en_index2])
                  
                  # above unlimited for this below-level
                  en_index2_copy = en_index2 + 1
                  while en_index2_copy < min(en_index1_copy + self.maxPhraseLen, len_list_en)  and en_to_nl[en_index2_copy] == [100, -1] :
                    en_unaligned_list.append([en_index1_copy, en_index2_copy])
                    en_index2_copy += 1                    
                  
                  en_index1_copy -= 1
                  
                if moreDebug:
                  sys.stdout.write('\tunaligned nl list: ' + str(nl_unaligned_list) + '\n')
                  sys.stdout.write('\tunaligned en list: ' + str(en_unaligned_list) + '\n')
                
                # add unaligned nl's for current english phrase
                for unaligned_nl in nl_unaligned_list :
                  self.addPair(list_nl, list_en, unaligned_nl[0], unaligned_nl[1], enRange[0], enRange[1])
                  totalExtractedThisPhrase += 1
                # add unaligned en's for current dutch phrase
                for unaligned_en in en_unaligned_list :
                  self.addPair(list_nl, list_en, nl_index1, nl_index2, unaligned_en[0], unaligned_en[1])
                  totalExtractedThisPhrase += 1
                  # add unaliged nl / unaligned en combi's
                  for unaligned_nl in nl_unaligned_list :
                    self.addPair(list_nl, list_en, unaligned_nl[0], unaligned_nl[1], unaligned_en[0], unaligned_en[1])
                    totalExtractedThisPhrase += 1
              
              
              else : #it wasnt a  valid phrase pair
                if moreDebug: 
                  sys.stdout.write ('\t' + str([nl_index1, nl_index2]) + ' != ' + str([nlFromEnMin, nlFromEnMax]) + '\n')
                  sys.stdout.write ('\t'+ self.getSubstring(list_nl, range(nl_index1, nl_index2+1)) + ' != ' )
                  sys.stdout.write ( self.getSubstring(list_en, range(enRange[0], enRange[1]+1)) + '\n')
                
            else:
              if moreDebug:
                sys.stdout.write ('\t too long: ' + self.getSubstring(list_en, range(enRange[0], enRange[1]+1)) + '\n')
              break
              
          else:
            if moreDebug:
              sys.stdout.write('\t ' + str(nl_index2) + ' is unaligned\n')
            
          if moreDebug:
            sys.stdout.write('we have extracted ' + str(totalExtractedThisPhrase) + ' phrase pairs \n')
            
          nl_index2 +=1
        
        
        
    self.addPeriod()
      
    #~if moreDebug:
      #~sys.stdout.write('\nWith this sentence pair , \n')
      #~sys.stdout.write('we have extracted ' + str(totalExtractedThisPhrase) + ' phrase pairs \n')


                
  # why not
  def addPeriod(self):
    self.total_extracted = self.total_extracted + 1

    # update tables
    nlEntry = '.'
    enEntry = '.'
    nl_enEntry = ('.' , '.') #tuple

    self.updateTables(nlEntry, enEntry, nl_enEntry)
    
  def addPair(self, list_nl, list_en, start_nl, end_nl, start_en, end_en):
    self.total_extracted = self.total_extracted + 1

    # update tables
    nlEntry = self.getSubstring(list_nl, range(start_nl,end_nl+1))
    enEntry = self.getSubstring(list_en, range(start_en,end_en+1))
    nl_enEntry = (nlEntry , enEntry) #tuple

    self.updateTables(nlEntry, enEntry, nl_enEntry)

  # update the hash tables (phrase (pair) --> count)
  def updateTables(self, nlString, enString, nl_enString):

    if nlString in self.table_nl:
      self.table_nl[nlString] = self.table_nl[nlString] + 1
    else:
      self.table_nl[nlString] = 1
      self.unique_nl = self.unique_nl + 1

    if enString in self.table_en:
      self.table_en[enString] = self.table_en[enString] + 1
    else:
      self.table_en[enString] = 1
      self.unique_en = self.unique_en + 1

    if nl_enString in self.table_nl_en:
      self.table_nl_en[nl_enString] = self.table_nl_en[nl_enString] + 1
    else:
      self.table_nl_en[nl_enString] = 1
      self.unique_nl_en = self.unique_nl_en + 1


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
  """

  path = os.getcwd()



  alignPath = path + '/' + alignDir
  tablePath = path + '/' + tableDir

  reader = Reader(alignPath, alignsFileName, nlFileName, enFileName)
  extractor = Extractor(reader, tablePath)
  phraseTables = PhraseTables()

  def __init__(self):
    pass

  def run(self):
    self.phraseTables.getFromExtractor(self.extractor)

    #self.initPhraseTables()
    #~sys.stdout.write( 'log(Pr(\"and\" | \"en\")) = ' + str(self.phraseTables.getConditionalProbabilityEn('en', 'and', True)) + '\n')
    #~sys.stdout.write( 'Pr(\"and\" | \"en\") = ' + str(self.phraseTables.getConditionalProbabilityEn('en', 'and', False)) + '\n')
#~
    #~sys.stdout.write( 'log(Pr(\"en\" | \"and\")) = ' + str(self.phraseTables.getConditionalProbabilityNl('en', 'and', True)) + '\n')
    #~sys.stdout.write( 'Pr(\"en\" | \"and\") = ' + str(self.phraseTables.getConditionalProbabilityNl('en', 'and', False)) + '\n')
#~
#~
    #~sys.stdout.write( 'Pr(\"en\" , \"and\") = ' + str(self.phraseTables.getJointProbability('en', 'and', False)) + '\n')

  def initPhraseTables(self):

    # if tables are already written to files
    if (os.path.isfile(self.tablePath  + table_nl_en_file) and
          os.path.isfile(self.tablePath  + table_nl_file) and
          os.path.isfile(self.tablePath  + table_en_file)):

      sys.stdout.write('===================================================\n' +
                     'reading phrases from files: \n' +
                     'NL & EN joint phrase table: \"' + table_nl_en_file + '\"\n' +
                     'NL phrase table: \"' + table_nl_file + '\"\n' +
                     'EN phrase table: \"' + table_en_file + '\"\n' +
                     'from directory \"' + self.tablePath + '\"'+ '\n' +
                     '===================================================\n\n')

      self.phraseTables.readFromFiles(self.tablePath)


    else:
        sys.stdout.write('\n===================================================\n' +
                         'parsing alignments in \"' + alignsFileName + '\"\n' +
                         'for \"' + nlFileName + '\" and \"' + enFileName + '\"\n'+
                         'from directory \"' + self.alignPath + '\"'+ '\n' +
                         '===================================================\n')

        self.phraseTables.getFromExtractor(self.extractor)

        sys.stdout.write('\n===================================================\n' +
                         'have parsed alignments in \"' + alignsFileName + '\"\n' +
                         'for \"' + nlFileName + '\" and \"' + enFileName + '\"\n'+
                         'from directory \"' + self.alignPath + '\"'+ '\n'+
                         'and saved to: \n' +
                         'NL & EN joint phrase table: \"' + table_nl_en_file + '\"\n' +
                         'NL phrase table: \"' + table_nl_file + '\"\n' +
                         'EN phrase table: \"' + table_en_file + '\"\n' +
                         'in directory \"' + self.tablePath + '\"'+ '\n' +
                         '===================================================\n')

### used to call Main.run()
if __name__ == '__main__': #if this file is called by python test.py
  main = Main()
  main.run()
