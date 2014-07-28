"""
file: yoshinaka11.py
E. Stabler  Clark,Eyraud&Habrard'08, updated 2014-07-08 with time, comments, etc 
D. Peatman  Clark,Eyraud&Habrard'10  updated 2014-07-17
E. Stabler  added timing, modified the new tests, etc
            updated 2014-07-19 with some corrections, clarified variable names
M. Burks    Yoshinaka '11. 2014-07-22. Algorithm 1
"""
#import ckyCBFG # for parsing with hypothesis grammar
#import cky     # for parsing with target grammar
import time    # for timing the learner
import sys     # for stdout
import ckyYCFG # for parsing with Yoshinaka's grammars
from sets import Set
import ckye

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

def subsets(K,k): # returns all subsets of K with size k
    sets = []
    if (k == 0): # return set with empty set, this case is meaningless and should not be reached
        sets = [[]]
    elif (len(K) < k): # should never reach this case
        sets = []
    elif (len(K) == k): #subset size is equal to set size
        sets = [K]
    elif (k == 1): # subsets have size 1
        for a in K:
            sets.append([a])
    else:
        for i in range(len(K)-k+1):
            a = K[i]
            Kbar = K[i+1:]
            for s in subsets(Kbar,k-1): # I couldn't quickly think of a way to avoid recursion entirely but tried to minimize it.
                s.append(a)
                sets.append((s)) 
    return sets

def tupledSubsets(subsets): # converts subsets in list form to tuple form
    TS = []
    for ss in subsets:
        SS = []
        for string in ss:
            SS.append(tuple(string))
        TS.append(tuple(SS))
    return TS
"""
K0 = [['0'],['1'],['2'],['3'],['4'],['5']]
sets = subsets(K0,3)
print "sets"
print sets
print len(sets)
print "tupled sets"
print tupledSubsets(sets)
"""
def context_odot_S(context,S,target,start): # returns True if (context odot S) is a subset of target.
    for s in S:
        string = list(s)
        if not(whatOracleSays(target,start,context[0]+string+context[1])):
            return False
    return True
    
def C_odot_string(C,s,target,start): # returns True if (C odot string) is a subset of target.
    string = list(s)
    for context in C:
        if not(whatOracleSays(target,start,context[0]+string+context[1])):
            return False
    return True

def C_odot_S1_S2(C,S1,S2,target,start): # returns True if (SF odot S1S2) is a subset of target.
    for w1 in S1:
        for w2 in S2:
            if not(C_odot_string(C,w1+w2,target,start)):
                return False
    return True
    
def SF(S,F,target,start): # Yoshinaka '11, 435
    SF = []
    for context in F:
        if context_odot_S(context,S,target,start):
           SF.append(context)
    return SF 

def V_k(K,F,k,target,start): # Yoshinaka '11, 435
    V = []
    if (k==0):
        return V
    for i in range(k): # i+1 is size of subset
        ts = tupledSubsets(subsets(K,i+1))
        for s in ts:
            sf = SF(s,F,target,start)
            if not(sf == []): # if there are no contexts for a potential category, we have no reason to include it.
                V.append((s,sf))
    return V        
        
def alphabet(K):
    sigma = []
    for w in K:
        if (len(w) == 1):
            sigma.append(w)
    return sigma

# print alphabet([['0'], ['0', '1'], ['1'], ['2']])

def g_k(K,F,k,target,start): # Yoshinaka '11, 435
    P0 = Set([])
    P1 = Set([])
    P2 = Set([])
    PL = Set([])
    V = V_k(K,F,k,target,start) # V is a list of tuples (S,SF). (S is strings, SF is contexts)
    Sigma = alphabet(K)
    for (S,SF) in V: # determine rules for each (S,SF)
        for a in Sigma: # add to PL
            if C_odot_string(SF,a,target,start):
                newRule = (S,a[0])
                if not(newRule in PL):
                    PL.add(newRule)
        if C_odot_string(SF,[],target,start): # add to P0
            newRule = S
            if not(newRule in P0):
                P0.add(newRule)
        for (S1,S1F) in V: # add to P2.
            for (S2,S2F) in V:
               if C_odot_S1_S2(SF,S1,S2,target,start):
                   newRule = (S,S1,S2)
                   if not(newRule in P2):
                       P2.add(newRule)
        if (([],[]) in SF): # add start rules to P1
            newRule = (0,S) 
            if not(newRule in P1):
                P1.add(newRule)
    return (P0,P1,P2,PL)

# First conditional check
def notDinLG(D,G):
    for s in D:
        if not(ckye.accepts(G,0,s)):
            return True
    return False

def kFKP (sample,target,start): # Yoshinaka '11, 437
    t0 = time.time() #for trace
    D = []
    K = []
    F = [([],[])]
    ConD = []
    SubD = []
    k = 3 # this can be changed. I don't really know or understand the effects of changing this.
    Ghat = g_k(K,F,k,target,start) # EPS - Ghat is the current hypothesis. Note: It is a CBFG, not a regular CFG.
    for w in sample:
#        print #for trace
#        traceFlag = 0 #for trace
        print 'processing input:', w # for trace
        sys.stdout.write(str(time.time() - t0)+' seconds\n') #for trace
        sys.stdout.flush() #for trace
        D.append(w)
        addContexts(ConD,w)
        addNEsubstrings(SubD,w)
        F = ConD
        if notDinLG(D,Ghat):
#            if traceFlag: print #for trace
#            print 'undergeneralization:',w # " ".join(w) #for trace
#            traceFlag = 0 #for trace
            K = SubD
#        else: #for trace
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
        value = ckye.accepts(target,start,t)  # consult oracle for new result
        memoryOfOraclesClaims[t] = value
        return value

""" examples: uncomment one grammar # EPS
"""
# from cfg0e import *  # target L = { aba }
from cfg1e import *  # target L = {0^n1^n| n>0}
# from cfg2e import *  # target L inspired by Koopman,Sportiche,Stabler ISAT chapter 3

"""
target0 = (['S'], [], [('S','A','SB'), ('SB','S','B')], [('A','a'), ('B','b')] )
sample0 = [['a','b']]
start0 = 'S'

target1 = ([], [], [('S','A','B'),('S','A','SB'), ('SB','S','B')], [('A','0'), ('B','1')] )
sample1 = [['0','1'],['0','0','1','1'],['0','0','0','1','1','1']]
start1 = 'S'
"""

print 'checking sample with target grammar...'
for w in sample0:
    if whatOracleSays(target0,start0,w):
        print "Accepted by target grammar :", " ".join(w)
    else:
        print "Rejected by target grammar :", " ".join(w)
        sys.exit(-1) # do not continue if sample is not a subset of target!

Ghat = kFKP(sample0,target0,start0)

print
for w in sample0:
    if ckye.accepts(Ghat,0,w):
        print "Accepted by learner's grammar :", " ".join(w)
    else:
        print "Rejected by learner's grammar :", " ".join(w)

print 
print "Ghat:"
ckye.prettyGrammar(Ghat)
print

print len(Ghat[0])+len(Ghat[1])+len(Ghat[2])+len(Ghat[3]),'rules in grammar'
print
print len(memoryOfOraclesClaims),'queries to oracle'

"""
testw = ['0','0','0','0','0','1','1','1','1','1']
if ckye.accepts(Ghat,0,testw):
    print "Accepted by learner's grammar :", " ".join(testw)
else:
    print "Rejected by learner's grammar :", " ".join(testw)
"""