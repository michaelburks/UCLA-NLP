"""
file: ckyYCFG.py    
M. Burks, 2014-07-22
   cky parsing for the grammar from Yoshinaka '11.
   fixed pretty printing for categories, grammar, and chart
"""

def subset(c1,c2):
    for x1 in c1:
        if not(x1 in c2):
            return False
    return True

def initializeChart(w,PL,chart): # insert lexical items
    for (i,wi) in enumerate(w):  # enumerate numbers elements of w from 0
        wiCat = []
        for (lhs,rhs) in PL:
            if rhs == wi:
                chart[i][i+1].append(lhs)

def closeChart(P,chart,n):
    for width in range(2,n+1):
        for start in range(n-width+1):     # so then range stops with n-width
            end = start + width
            for mid in range(start+1,end): # so then range stops with end-1
                for (lhs,y,z) in P: # lhs, y, z are all (S,SF)
                    if contextsContained(y,chart[start][mid]) and contextsContained(z,chart[mid][end]):
                        chart[start][end].append(lhs)
                        
def contextsContained((S,SF),L): # all contexts of first are contexts of item in L
    for (S1,S1F) in L:
        if subset(SF,S1F):
            return True
    return False
    
def containsNullContext(L): # L is chart[0][n], a list of (S,SF) pairs
    for (S,SF) in L:
        if (([],[]) in SF):
            return True
    return False
    
def accepts((PL,P),w):
    n = len(w)
    chart = [ [ [] for i in range(n+1) ] for j in range(n+1) ]
    initializeChart(w,PL,chart)
    closeChart(P,chart,n)
    if containsNullContext(chart[0][n]):
        return True
    else:
        return False

"""
## example grammar for {a^nb^n| n>0}
PL0 = [ 
    ( [ ([],['b']), ([],['a','b','b']) ] , 'a' ),
    ( [ (['a'],[]), (['a','a','b'],[]) ] , 'b' )
    ]
P0 = [
    ( [ ([],[]) ]    , [ ([],['b']) ]         , [ (['a','a','b'],[]) ] ),
    ( [ ([],[]) ]    , [ ([],['a','b','b']) ] , [ (['a'],[]) ] ),
    ( [ ([],['b']) ] , [ ([],['a','b','b']) ] , [ ([],[]) ] ),
    ( [ (['a'],[]) ] , [ ([],[]) ]            , [ (['a','a','b'],[]) ] )
    ]

#w0 = ['a','b']
#w0 = ['a','a','b','b']
w0 = ['a','b','b']
#w0 = ['a','a','a','b','b','b']
"""

"""
## example grammar for {a,b}+
PL0 = [ 
    ( [ ([],[]) ] , 'a' ),
    ( [ ([],[]) ] , 'b' ),
    ]
P0 = [
    ( [ ([],[]) ]    , [ ([],[]) ] , [ ([],[]) ] ),
    ]
"""

"""
## example grammar for {aba}
# K= nesubstrings(aba) = {a,ab,aba,b,ba}
# F= contexts(aba) = {(,ba), (,a), (,), (a,a), (a,)}
PL0 = [ 
    ( [ ([],['b','a']),(['a','b'],[]) ] , 'a' ),
    ( [ (['a'],['a']) ]                 , 'b' ),
    ]
P0 = [
    ( [ ([],[]) ]      , [ ([],['b','a']), (['a','b'],[]) ] , [ (['a'],[]) ]                    ),   # FL(aba) -> FL(a) FL(ba)
    ( [ ([],[]) ]      , [ ([],['a']) ]                     , [ ([],['b','a']),(['a','b'],[]) ] ),   # FL(aba) -> FL(ab) FL(a)
    ( [ ([],['a']) ]   , [ ([],['b','a']),(['a','b'],[])  ] , [ (['a'],['a']) ]                 ),   # FL(ab) -> FL(a) FL(b)
    ( [ (['a'],[]) ]   , [ (['a'],['a']) ]                  , [ ([],['b','a']),(['a','b'],[]) ] ),   # FL(ba) -> FL(b) FL(a)
    ]
"""

## BEGIN pretty printer for context
def prettyContext((lc,rc)):
    sep = " "   # put space if some lex items have > 1 character
    plc = sep.join(map(str,lc))
    prc = sep.join(map(str,rc))
    result = "(" + plc + "," + prc + ")"
    return result
## END pretty printer for context

## BEGIN pretty printer for chart
def prettyChart(c):
    for (r,row) in enumerate(c):
        for (c,col) in enumerate(row):
            if len(col)>0:
                print (r,c),"=",",".join(map(prettyCategory,col))
## END pretty printer for chart

## BEGIN pretty printer for category
def prettyCategory((S,SF)):
    prettys = []
    for s in S:
        prettys.append(' '.join(s))
    prettyS = ', '.join(prettys)
    prettysf = []
    for sf in SF:
        prettysf.append(prettyContext(sf))
    prettySF = ', '.join(prettysf)
    result = "(["+prettyS+"],["+prettySF+"])"
    return result
## END pretty printer for category

#cat = ([['0']], [([], ['1']), ([], ['0', '1', '1']), (['0'], ['1', '1']), ([], ['0', '0', '1', '1', '1']), (['0'], ['0', '1', '1', '1']), (['0', '0'], ['1', '1', '1'])])
#print prettyCategory(cat)

## BEGIN pretty printer for grammar
def prettyGrammar((PL,P)):
    for (lhs,rhs) in PL: # lhs is (S,SF), rhs is 'a'
        print '\t',prettyCategory(lhs),' -> ',rhs
    for (lhs,y,z) in P:
        print '\t',prettyCategory(lhs),' -> ',prettyCategory(y),'   ',prettyCategory(z)
## END pretty printer for grammar

def ckyChart((PL,P),w): # like accepts, but shows chart
    n = len(w)
    chart = [ [ [] for i in range(n+1) ] for j in range(n+1) ]
    initializeChart(w,PL,chart)
    closeChart(P,chart,n)
    prettyChart(chart)
    print
    if containsNullContext(chart[0][n]):
        return True
    else:
        return False

#prettyGrammar((PL0,P0))
#print ckyChart((PL0,P0),w0)