import itertools

#phrase is tuple
def coverage_concat(phrase, table_nl_en,n):
	nl = phrase[0].split()
	en = phrase[1].split()
	
	length_en  = len(en)

	#can be built by concatenating (in any order) n > 0 phrase pairs from the training set phrase table
	#check length --- n
	#...............................
	
	
def coverage (test_phrases, table_nl_en, n):
  total = 0
  found = 0
  for phrase in test_phrases:
    total += 1
    if n == 1:
      if test_phrases[phrase] != None :
        found += 1
    else :
      check_concat(phrase, table_nl_en, n)
    
  return float(found)/total 



