"""@package Tropical
Exploration of group-based encryption in the tropical semiring.

Little Big Integers: scaled-down bignum arithmetic.

"""

import numpy as np

global base, curr
global bsgn, csgn

global LBI_WORDS, LBI_COUNT_ADDSUB, LBI_COUNT_CMP

LBI_WORDS = 4
LBI_COUNT_ADDSUB, LBI_COUNT_CMP = 0, 0

def lbi_count_reset():
    global LBI_COUNT_ADDSUB, LBI_COUNT_CMP    
    LBI_COUNT_ADDSUB, LBI_COUNT_CMP = 0, 0

def lbi_counts():
    global LBI_COUNT_ADDSUB, LBI_COUNT_CMP    
    return LBI_COUNT_ADDSUB, LBI_COUNT_CMP    
    
def lbi_lbi2dec( lbiN, sgnN ):
    b = np.array( [ 2**(32*i) for i in range(LBI_WORDS) ] )
    return sum(b*lbiN)*sgnN

def lbi_cmp0( lbiA, lbiB ):
    global LBI_COUNT_ADDSUB, LBI_COUNT_CMP    
    LBI_COUNT_CMP += 1
    for p in range(LBI_WORDS):
        i = LBI_WORDS-p-1
        if lbiA[i]>lbiB[i]:
            return 1
        if lbiA[i]<lbiB[i]:
            return -1
    return 0

def lbi_cmp( lbiA, lbiB, sgnA, sgnB ):
    if sgnA != sgnB:
        if 1 == sgnA:
            return 1
        else:
            return -1
    else:
        cmp_ = lbi_cmp0( lbiA, lbiB )
        if 1 == sgnA:
            return cmp_
        else:
            return -cmp_
        

def lbi_add0( lbiA, lbiB ):
    lbiC  = np.full( LBI_WORDS, 0, dtype=np.uint32 )
    carry = 0
    for i in range(LBI_WORDS):
        lword   = np.uint64(lbiA[i]) + np.uint64(lbiB[i]) + carry
        lbiC[i] = np.uint32( lword )
        # carry   = np.right_shift( lword, 32, dtype=np.uint64 )
        carry   = int(lword)>>32
        # print lword, lbiA[i], lbiB[i], lbiC[i], carry
    return lbiC, carry

def lbi_sub0( lbiA, lbiB ):
    lbiC  = np.full( LBI_WORDS, 0, dtype=np.uint32 )
    carry = 0
    for i in range(LBI_WORDS):
        if lbiA[i]>lbiB[i]:
            lbiC[i] = np.uint32(lbiA[i]-lbiB[i]+carry)
            carry = 0
        else:
            lbiC[i] = np.uint32( 2**32+lbiA[i]-lbiB[i]+carry )
            carry = -1
        # print "- ",lbiA[i], lbiB[i], lbiC[i], carry
    return lbiC, carry

def lbi_sub( lbiA, lbiB, sgnA, sgnB ):
    global LBI_WORDS, LBI_COUNT_ADDSUB, LBI_COUNT_CMP
    LBI_COUNT_ADDSUB += 1
    cmp_ = lbi_cmp0( lbiA, lbiB )
    if sgnA != sgnB:
        return lbi_add0( lbiA, lbiB ), sgnA
    else:
        if cmp_>=0:
            return lbi_sub0( lbiA, lbiB ), sgnA
        else:
            return lbi_sub0( lbiB, lbiA ), -sgnA
    return 0, 0

def lbi_add( lbiA, lbiB, sgnA, sgnB ):
    global LBI_WORDS, LBI_COUNT_ADDSUB, LBI_COUNT_CMP
    LBI_COUNT_ADDSUB += 1
    cmp_ = lbi_cmp0( lbiA, lbiB )
    if sgnA == sgnB:
        return lbi_add0( lbiA, lbiB ), sgnA
    else:
        if cmp_==-1:
            return lbi_sub0( lbiB, lbiA ), sgnB
        else:
            return lbi_sub0( lbiA, lbiB ), sgnA
    return 0, 0


if __name__ == '__main__':
    # base = np.random.randint( 2**30, size=LBI_WORDS )
    # base = np.full( LBI_WORDS, 2**31, dtype=np.uint32 )
    base = np.random.randint( 2**28, size=LBI_WORDS )
    bsgn = 1
    # curr = np.full( LBI_WORDS, 2**31, dtype=np.uint32 )
    curr = np.random.randint( 2**28, size=LBI_WORDS )
    csgn = -1
    print base
    print curr
    print lbi_lbi2dec( base, bsgn )
    print lbi_lbi2dec( curr, csgn )
    print "A > B:u", lbi_cmp0(base,curr)
    print "A > B: ", lbi_cmp(base,curr, bsgn, csgn)
    lbi_count_reset()
    (lbir, carry), asgn  = lbi_add( base, curr, bsgn, csgn )
    (lbis, scarry), ssgn = lbi_sub( base, curr, bsgn, csgn )
    print lbi_counts()
    lbi_count_reset()
    print lbir, carry
    if carry==1:
        a = 2**(LBI_WORDS*32)+lbi_lbi2dec(lbir, asgn)
        b =  lbi_lbi2dec( base, bsgn )+lbi_lbi2dec( curr, csgn )
        print a, asgn
        print b
        print a-b
    else:
        print lbi_lbi2dec(lbir, asgn)
        print lbi_lbi2dec( base, bsgn )+lbi_lbi2dec( curr, csgn )
    print "---"
    print lbis, scarry
    a = lbi_lbi2dec( base, bsgn )
    b = lbi_lbi2dec( curr, csgn )
    print a-b
    if scarry==1:
        print 2**(LBI_WORDS*32)+lbi_lbi2dec(lbis, ssgn)
    else:
        print lbi_lbi2dec(lbis, ssgn), ssgn
