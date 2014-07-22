"""
file: yoshinaka11.py
E. Stabler  Clark,Eyraud&Habrard'08, updated 2014-07-08 with time, comments, etc 
D. Peatman  Clark,Eyraud&Habrard'10  updated 2014-07-17
E. Stabler  added timing, modified the new tests, etc
            updated 2014-07-19 with some corrections, clarified variable names
M. Burks    Yoshinaka '11. 2014-07-22. Algorithm 1
"""
#import ckyCBFG # for parsing with hypothesis grammar
import cky     # for parsing with target grammar
import time    # for timing the learner
import sys     # for stdout
import ckyYCFG # for parsing with Yoshinaka's grammars

def addNEsubstrings(sofar,w):  # non-empty substrings of w added to list sofar
    max=len(w)
    for i in range(max):
        for j in range(max+1):
            if i<j:
                s=w[i:j]
                if not(s in sofar): # avoid redundancy
                    sofar.append(s) # EPS: no sort needed
"""
x = []
addNEsubstrings(x,['the','cat','smiles'])
print x
"""
def addContexts(sofar,w):  # contexts of substrings of w added to list sofar
    max=len(w)
    for i in range(max):
        for j in range(max+1):
            if i<j:
                lc=w[0:i]
                rc=w[j:max]
                c=(lc,rc)
                if not(c in sofar): # avoid redundancy
                    sofar.append(c) # EPS: no sort needed
"""
x = []
addContexts(x,['a','b','c'])
"""
""" this has been in-lined
def odot(c,s): return c[0]+s+c[1]

# this is not used
def odotCartesianProduct(C,S):
    product=[]
    for c in C:
        for s in S:
            product.append(c[0]+s+c[1])
    return product
"""
"""
def FL(F,w,target,start): # from CEH'08, Def.5 on p.5
    ok = []
    for c in F:
        if whatOracleSays(target,start,c[0]+w+c[1]): # EPS added start for modified cky.py
            ok.append(c)
    return ok

def g(K,F,target,start): # from CEH'08, Def.7 on p.6
    PL=[]
    P=[]
    for w in K:
        lhs = FL(F,w,target,start) # oracle called for this
        if len(w)==1:
            rhs = w[0]
            rule = (lhs,rhs)
            if not(rule in PL): # avoid redundancy
                PL.append(rule)
        else:
            lenw=len(w)
            for i in range(lenw):
                if 0<i and i<lenw:
                    fl1=FL(F,w[0:i],target,start) # oracle called for this
                    fl2=FL(F,w[i:lenw],target,start) # oracle called for this
                    rule = (lhs,fl1,fl2)
                    if not(rule in P): # avoid redundancy
                        P.append(rule)
    return(PL,P)
"""

def subsets(K,k): # returns all subsets of K with size k
    sets = []
    if (k == 0): # should never reach this case
        return []
    if (len(K) < k): # should never reach this case
        return []
    if (len(K) == k): #subset size is equal to set size
        return [K]
    if (k == 1): # subsets have size 1
        for s in K:
            sets.append([s])
        return sets
    for i in range(len(K)): 
        a = K[i]
        Kbar = K[i+1:]
        for s in subsets(Kbar,k-1): # I couldn't quickly think of a way to avoid recursion entirely but tried to minimize it.
            s.append(a)
            sets.append(s)            
    return sets

"""      
K0 = [['0'],['1'],['2'],['3'],['4'],['5']]
sets = subsets(K0,6)
print sets
print len(sets)
"""

def contextWithStrings(context,S,target,start): # returns True if the context can be combined with each string to get something in the language
    for string in S:
        if not(whatOracleSays(target,start,context[0]+string+context[1])):
            return False
    return True
    
def stringWithContexts(string,F,target,start): # returns True if the string can be combined with each context to get something in the language
    for context in F:
        if not(whatOracleSays(target,start,context[0]+string+context[1])):
            return False
    return True

def SF(S,F,target,start):
    SF = []
    for context in F:
        if contextWithStrings(context,S,target,start):
           SF.append(context)
    return SF 

def V_k(K,F,k,target,start):
    V = []
    if (k==0):
        return V
    for i in range(k): # i is one less than size of subset
        for S in subsets(K,i+1):
            V.append((S,SF(S,F,target,start)))
    return V        
        
def alphabet(K):
    sigma = []
    for w in K:
        if (len(w) == 1):
            sigma.append(w)
    return sigma

# print alphabet([['0'], ['0', '1'], ['1'], ['2']])

def contextWithStringSets(SF,S1,S2,target,start):
    for w1 in S1:
        for w2 in S2:
            if not(stringWithContexts(w1+w2,SF,target,start)):
                return False
    return True

def g_k(K,F,k,target,start):
    P = []
    PL = []
    V = V_k(K,F,k,target,start) # V is a list of tuples (S,SF). (S is strings, SF is contexts)
    sigma = alphabet(K)
    sigma.append([''])
    for (S,SF) in V:
        for a in sigma:
            if stringWithContexts(a,SF,target,start):
                rule = ((S,SF),a[0])
                if not(rule in PL): # avoid redundancy
                    PL.append(rule)
        for (S1,S1F) in V:
            for (S2,S2F) in V:
               if contextWithStringSets(SF,S1,S2,target,start):
                   rule = ((S,SF),(S1,S1F),(S2,S2F))
                   if not(rule in P):
                       P.append(rule)
    return(PL,P)


# First conditional check
def notDinLG(D,G):
    for s in D:
        if not(ckyYCFG.accepts(G,s)):
            return True
    return False
"""
# Second conditional check
def reallyLongCond(SubD,K,C,F,target,start): # EPS: needs target grammar and start symbol
    for v in SubD:
        FLv = FL(F,v,target,start)
        for u in K:
            FLu = FL(F,u,target,start)
            if ckyCBFG.subset(FLu,FLv): # EPS: enter following loop only if this succeeds!
                for f in C:
                    if whatOracleSays(target,start,f[0]+u+f[1]) and whatOracleSays(target,start,f[0]+v+f[1]):
                        return True
    return False

def iil(Sample,target,start):  # target grammar is for oracle computation only
    t0 = time.time() #for trace
    K = []
    D = []
    F = [([],[])]
    ConD = []
    SubD = []
    Ghat = g(K,F,target,start) # EPS - Ghat is the current hypothesis. Note: It is a CBFG, not a regular CFG.
    for w in Sample:
#        print #for trace
#        traceFlag = 0 #for trace
        print 'processing input:', w # for trace
        sys.stdout.write(str(time.time() - t0)+' seconds\n') #for trace
        sys.stdout.flush() #for trace
        D.append(w)
        addContexts(ConD,w) #EPS
        addNEsubstrings(SubD,w) #EPS
        # at this point, IIL constructs a large set of test sentences, but here we just use D
        if notDinLG(D,Ghat): # EPS: w is in D, does not need to be passed
#            if traceFlag: print #for trace
#            print 'undergeneralization:',w # " ".join(w) #for trace
#            traceFlag = 0 #for trace
            K = SubD
            F = ConD
        elif reallyLongCond(SubD,K,ConD,F,target,start):
#            print 'adding contexts from new test:',w # " ".join(w) #for trace
#            traceFlag = 0 #for trace
            F = ConD
#        else: #for trace
#            traceFlag = traceFlag + 1 #for trace
#            sys.stdout.write("\r"+str(traceFlag)) #for trace
#            sys.stdout.flush() #for trace
        Ghat = g(K,F,target,start)
    print
    print time.time() - t0, "seconds" #for trace
    return Ghat
"""
def y1 (sample,target,start): # Yoshinaka Algorithm 1. Primal Approach
    t0 = time.time() #for trace
    D = []
    K = []
    F = [([],[])]
    ConD = []
    SubD = []
    k = 1 # this can be changed. I don't really know or understand the effects of changing this.
    Ghat = g_k(K,F,k,target,start) # EPS - Ghat is the current hypothesis. Note: It is a CBFG, not a regular CFG.
    for w in sample:
#        print #for trace
#        traceFlag = 0 #for trace
        print 'processing input:', w # for trace
#        sys.stdout.write(str(time.time() - t0)+' seconds\n') #for trace
#        sys.stdout.flush() #for trace
        D.append(w)
        addContexts(ConD,w)
        addNEsubstrings(SubD,w)
        F = ConD
        if notDinLG(D,Ghat):
#            if traceFlag: print #for trace
#            print 'undergeneralization:',w # " ".join(w) #for trace
#            traceFlag = 0 #for trace
            K = SubD
#       else: #for trace
#            traceFlag = traceFlag + 1 #for trace
#            sys.stdout.write("\r"+str(traceFlag)) #for trace
#            sys.stdout.flush() #for trace
        Ghat = g_k(K,F,k,target,start)
    print
    print time.time() - t0, "seconds" #for trace
    return Ghat            

memoryOfOraclesClaims = {}

def whatOracleSays(target,start,s):
    """ returns remembered or new values from oracle """
    t = tuple(s)  # tuples are hashable
    if t in memoryOfOraclesClaims.keys():  # ck "memory" first
        return memoryOfOraclesClaims[t]
    else: 
        value = cky.accepts(target,start,t)  # consult oracle for new result
        memoryOfOraclesClaims[t] = value
        return value

""" examples: uncomment one grammar # EPS
"""
# from cfg0 import *  # target L = { aba }
# from cfg1 import *  # target L = {0^n1^n| n>0}
from cfg2 import *  # target L inspired by Koopman,Sportiche,Stabler ISAT chapter 3


print 'checking sample with target grammar...'
for w in sample0:
    if whatOracleSays(target0,start0,w):
        print "Accepted by target grammar :", " ".join(w)
    else:
        print "Rejected by target grammar :", " ".join(w)
        sys.exit(-1) # do not continue if sample is not a subset of target!

Ghat = y1(sample0,target0,start0)
print
for w in sample0:
    if ckyYCFG.accepts(Ghat,w):
        print "Accepted by learner's grammar :", " ".join(w)
    else:
        print "Rejected by learner's grammar :", " ".join(w)

print 
print "Ghat:"
ckyYCFG.prettyGrammar(Ghat)
print

print len(Ghat[0])+len(Ghat[1]),'rules in grammar'
print
print len(memoryOfOraclesClaims),'queries to oracle'

"""
testw = ['0','0','0','0','0','1','1','1','1','1']
if ckyYCFG.accepts(Ghat,testw):
    print "Accepted by learner's grammar :", " ".join(testw)
else:
    print "Rejected by learner's grammar :", " ".join(testw)
"""