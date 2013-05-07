import itertools

#checks if a partition is valid (every phrase is in the hashtable)
def valid (p, table):
  print p
  
  for x in p:
    
    if " ".join(x) not in table:
      print " ".join(x)
      return False
  return True

def get_valid_partitions(partitions, table):
  return [x for x in partitions if valid(x, table)]


def part2(x, len_x):
  y = []
  #n = len(x)
  for i in range(1, len_x):
    y.append((x[0:i], x[i:len_x]))
  return y

def part3(x, len_x):
  y = []
  #n = len(x)
  for i in range(1, len_x):
    for j in range(i+1, len_x):
      y.append((x[0:i], x[i:j], x[j:len_x]))
  return y

def partitions(x,n, table):
  len_x = len(x)
  if n == 2:
    partitions = part2(x, len_x)
  elif n == 3:
    partitions = part3(x, len_x)
  return get_valid_partitions(partitions, table)



def valid_pair(a, len_a, p, table_x_y):
  #n = len(a)
  for i in range(0,len_a):
    if (" " .join(a[i])," ".join(p[i])) not in table_x_y:
      return False
  return True

#checks coverage of the phrase pair for n = 2 to 3
#table_x : hashtable of 'x' language
#table_y : hashtable of 'y' language
#table_x_y : hashtable for ('x','y') phrase pairs
def check_coverage(phrase_pair, table_x, table_y, table_x_y):
  for i in range(2,4):
    x, y = phrase_pair
    #print x.split()
    
    x_partitions = partitions(x, i, table_x)
    y_partitions = partitions(y, i, table_y)
    #print y_partitions
    for a in x_partitions :
      len_a = len(a)
      print a
      for b in y_partitions:
        #print b
        perms = itertools.permutations(b)
        for p in perms:
          print p
          if valid_pair(a, len_a, p, table_x_y):
            print 'valid:'
            print a
            print b
            return True
  return False

#***************EXAMPLE****************************
x = ['a', 'b', 'c', 'd']#'abcd'
y = ['x','y', 'z']#'xyz'
table_x=['a b', 'c d', 'a', 'b c d', 'b']  #a, b, cd
table_y=['x', 'y z', 'y', 'z'] #x,y,z
table_x_y = [('a','y'), ('b', 'x'), ('c d', 'z')]
print check_coverage((x,y), table_x, table_y, table_x_y)
