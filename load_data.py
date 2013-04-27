######
######


#returns a list with the pairs of alignments
def get_align_list(line):
	splitted = line.split()
	pairs = []
	for pair in splitted:
		dot_pos = pair.find('-')
		x = int(pair[0:dot_pos])
		y = int(pair[dot_pos+1])
		pairs.append((x,y))
	return pairs


#returns the list with the words of this line's sentence
def get_words (line):
	return line.split()

#returns the list of tuples sorted by the second element
def sort_by_nl(list_aligns):
	return sorted(list_aligns, key=lambda x : x[1])

#returns all the possible alignments of an element
#to return all the possible alignments of element y, use sort_by_y() first
#^it traverses whole list so sorting not needed
def get_possible_alignments(list_aligns, nr, language):
  if (language == 'nl'):
    return [item[0] for item in list_aligns if item[1]==nr]
  else:
    return [item[1] for item in list_aligns if item[0]==nr]

def phrase_extraction(list_aligns, nl_words, en_words):
  print list_aligns
  print sort_by_nl(list_aligns)
  print nl_words
  print en_words
  print get_possible_alignments(list_aligns, 3, 'en')
  print get_possible_alignments(list_aligns, 3, 'nl')

	#compute statistics and update the data structures


#this method loads the files line by line in parallel
#and loads the statistics in the data structures
def load_data(aligns, nl, en):
	#open the input files
  f_aligns = open(aligns)
  f_nl = open(nl)
  f_en = open(en)

  counter = 0

  while(True):
    #get the next line of each file
    line_aligns = f_aligns.next()
    line_nl = f_nl.next()
    line_en = f_en.next()

    if not line_aligns: #EOF
      f_aligns.close()
      f_nl.close()
      f_en.close()
      break

    list_aligns = get_align_list(line_aligns)
    nl_words = get_words (line_nl)
    en_words = get_words (line_en)

    phrase_extraction(list_aligns, nl_words, en_words)
    
    counter = counter +1
    if (counter == 4):
      break #testing

def load_data(aligns, nl, en):
	#open the input files
  f_aligns = open(aligns)
  f_nl = open(nl)
  f_en = open(en)

  counter = 0

  while(True):
    #get the next line of each file
    line_aligns = f_aligns.next()
    line_nl = f_nl.next()
    line_en = f_en.next()

    if not line_aligns: #EOF
      f_aligns.close()
      f_nl.close()
      f_en.close()
      break

    list_aligns = get_align_list(line_aligns)
    nl_words = get_words (line_nl)
    en_words = get_words (line_en)

    phrase_extraction(list_aligns, nl_words, en_words)
    
    counter = counter +1
    if (counter == 4):
      break #testing
path = 'aligned-data/'

aligns = 'aligned.nl-en2'
nl = 'europarl.nl-en.nl2'
en = 'europarl.nl-en.en2'

load_data(path+aligns, path+nl, path+en)
