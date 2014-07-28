""" file: ckye.py -- CKY extended to 2-normal form (cf Lange&Leiss 2009)
    E. Stabler  updated 2014-07-16
  Grammars given in the form (P0, P1, P2, PL) where 
        P0 ia a list of A where A -> empty
        P1 is a list of (A,B) where A -> B
        P2 is a list of (A,B,C) where A -> B C
        PL is a list of (A,w) where A -> w
  Terminals are the second elements of pairs in PL.
  (We assume non-initial elements of tuples in P1, P2 also appear initially.)
  Nonterminals are the first elements of tuples in these 4 sets.
  (Start category is specified separately.)
"""
from sets import Set

def buildNullable(g):
    """ returns nullable, a dictionary that maps nonterminal A to True iff A is nullable """
    nullable = {}
    occurs1 = {}
    occurs2 = {}
    todo = []
    # initialize nullable, occurs1, occurs2 and todo
    for r in g[1]: # unary rules
        nullable[r[0]]=False
        occurs1[r[0]] = []
        occurs2[r[0]] = []
    for r in g[2]: # binary rules
        nullable[r[0]]=False
        occurs1[r[0]] = []
        occurs2[r[0]] = []
    for r in g[3]: # lexical rules
        nullable[r[0]]=False
        occurs1[r[0]] = []
        occurs2[r[0]] = []
    # following loop guarantees all nonterminals will appear in nullable.keys(),
    #   and also initializes the agenda, todo
    for r in g[0]: # empty productions
        nullable[r]=True
        occurs1[r] = []
        occurs2[r] = []
        todo.append(r)
    # now calculate occurs1, occurs2
    for r in g[1]:
        if not(r[0] in occurs1[r[1]]): occurs1[r[1]].append(r[0])
    for r in g[2]:
        if not((r[0],r[2]) in occurs2[r[1]]): occurs2[r[1]].append((r[0],r[2]))
        if not((r[0],r[1]) in occurs2[r[2]]): occurs2[r[2]].append((r[0],r[1]))
    # loop to complete nullable
    while todo:
        B = todo.pop()
        for A in occurs1[B]:
            if not(nullable[A]):
                nullable[A] = True
                todo.append(A)
        for A,C in occurs2[B]:
            if nullable[C] and not(nullable[A]):
                nullable[A] = True
                todo.append(A)
    return nullable

# example: build_nullable(cfg1e)
# example: build_nullable(cfg3e)

def buildChainsTo(g,nullable): 
    """ returns chainsTo which maps each symbol x to {C| C =>* x} """
    # NB: reflexive and transitive closed for categories C; transitive for terminals x
    chainsTo = {}
    for A in nullable.keys(): chainsTo[A]=[A] # initialize with non-terminals
    for r in g[3]: # lexical rules
        if r[1] in chainsTo.keys():
            if not(r[0] in chainsTo[r[1]]): chainsTo[r[1]].append(r[0])
        else: 
            chainsTo[r[1]] = [r[0]]
    for r in g[1]: # unary rules
        if not(r[0] in chainsTo[r[1]]): chainsTo[r[1]].append(r[0])
    for r in g[2]: # binary rules
        if nullable[r[1]] and not(r[0] in chainsTo[r[2]]): chainsTo[r[2]].append(r[0])
        if nullable[r[2]] and not(r[0] in chainsTo[r[1]]): chainsTo[r[1]].append(r[0])
    # now compute transitive closure
    for k in chainsTo.keys():
        for i in chainsTo.keys():
            for j in chainsTo.keys():
                if k in chainsTo[i] and j in chainsTo[k] and not(j in chainsTo[i]):
                    chainsTo[i].append(j)
    return chainsTo

# example: build_chainsTo(cfg3e,build_nullable(cfg3e))

def buildMatrix(g,w,cD):
    """ returns square CKY matrix """
    n = len(w)
    t = [ [ Set([]) for i in range(n) ] for i in range(n) ]  # Set operation
    for i in range(n): t[i][i].update(cD[w[i]]) # Set operation
    for j in range(1,n):
        for i in reversed(range(j)):
            for h in range(i,j):
                for r in g[2]:
                    if r[1] in t[i][h] and r[2] in t[h+1][j]:
                        t[i][j].update(cD[r[0]]) # Set operation
    return t

# example: buildMatrix(cfg1e,['a','b'],buildChainsTo(cfg1e,buildNullable(cfg1e)))
# example: buildMatrix(cfg1e,['a','a','b','b'],buildChainsTo(cfg1e,buildNullable(cfg1e)))
# example: buildMatrix(cfg1e,['a','a','b'],buildChainsTo(cfg1e,buildNullable(cfg1e)))
# example: buildMatrix(cfg3e,['Sue','proved'],buildChainsTo(cfg3e,buildNullable(cfg3e)))

def accepts0(g,start,nD,cD,w):
    """ returns True iff w in L(g), for 2-normal form grammar g with specified start category """
    if len(w)==0:                        # check for empty string
        return nD[start]
    cDkeys = cD.keys()
    for wi in w:
        if not(wi in cDkeys):        # reject if any nonterminal is not in grammar
            return False
    else:
        t = buildMatrix(g,w,cD)
#        printSquareMatrix(t)
        if start in t[0][len(w)-1]: return True
        else: return False

def accepts(g,start,w):
    """ returns True iff w in L(g), for 2-normal form grammar g with specified start category """
    nD = buildNullable(g)
    cD = buildChainsTo(g,nD)
    return accepts0(g,start,nD,cD,w)

# example: accepts(cfg1e,'S',['a','b'])
# example: accepts(cfg1e,'S',['a','a','b','b'])
# FALSE example: accepts(cfg1e,'S',['a','a','b'])
# example: accepts(cfg3e,'S',['Sue','proved'])

#from cfg2int import *
#def intAccepts(g,w,start):
#    (ig,g2i,i2g) = buildG2I(g) # from cfg2int
#    return accepts(ig,[g2i[s] for s in w],g2i[start])

# for compatibility with cky.py, we could add
# def ckyAccepts((PL,P),w): return accepts(([],[],P,PL),w,'S')

## For display of upper triangle of square matrix
def printSquareMatrix(a):
    for i in range(len(a)):
        for j in range(len(a)):
            if i <= j: print str((i,j))+':'+str(a[i][j])

## For display of 2-normal form grammar, grouping rules by category
def prettyGrammar((P0,P1,P2,L)):
    rules = []
    for A in P0: rules.append(str(A)+' -> []')
    for A,B in P1: rules.append(str(A)+' -> '+str(B))
    for A,B,C in P2: rules.append(str(A)+' -> '+str(B)+'    '+str(C))
    for A,w in L: rules.append(str(A)+' -> '+str(w))
    rules.sort()
    for r in rules: print r
"""
 EXAMPLES
# 0^n1^n for n>=0  This recognizer works when both cats and terminals are ints.
cfg0e = ([3], [], [(3, 0, 5), (5, 3, 2)], [(0, 1), (2, 4)])

# accepts(cfg0e,[0,0,0,1,1,1],0)

# a^nb^n for n>=0  This recognizer works when both cats and terminals are strings.
cfg1e = (['S'], [], [('S','A','SB'), ('SB','S','B')], [('A','a'), ('B','b')] )

# accepts(cfg1e,['a','b'],'S')

# a^nb^n for n>0, Chomsky Normal Form
cfg2e = ([], [], [('S','A','B'),('S','A','SB'), ('SB','S','B')], [('A','a'), ('B','b')] )

# accepts(cfg2e,['a','a','a','b','b','b'],'S')

# language with empty DP, V, for testing nullable, chainsTo
cfg3e = (['DP','V'],
        [('VP','V'), ('AP','A'), ('VP','VP')],
        [('S','DP','VP'), ('VP','V','DP'), ('VP','VP','AP')],
        [('DP','Sue'),('DP','it'),('V','proved'),('A','true')] )
"""