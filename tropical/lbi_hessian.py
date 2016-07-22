"""@package Tropical
Exploration of group-based encryption in the tropical semiring.

Tropical Hessian Pencil group law.

"""
import time, argparse
import numpy as np
import lbi

def chk_carry( carry, s ):
    if 0!=carry:
        print "Carry %s" % (s)

def pt_K_alt( lbiX, lbiY, sgnX, sgnY, verbose=False ):
    """Hessian Pencil parameter from a cyce point.

    4 ADDSUBs + 5 CMPs
    """
    (lbisum, csum), sgnsum = lbi.lbi_add( lbiX, lbiY, sgnX, sgnY )
    (lbi2X, c2X), sgn2X = lbi.lbi_add( lbiX, lbiX, sgnX, sgnX )
    (lbi2Y, c2Y), sgn2Y = lbi.lbi_add( lbiY, lbiY, sgnY, sgnY )
    cmp = lbi.lbi_cmp( lbiX, lbiY, sgnX, sgnY )
    if 1==cmp:
        if 1==sgnX:
            (lbiR, cR), sgnR = lbi.lbi_sub( lbi2X, lbiY, sgn2X, sgnY )
            return lbiR, sgnR
        else:
            return lbisum, -sgnsum
    else:
        if 1==sgnY:
            (lbiR, cR), sgnR = lbi.lbi_sub( lbi2Y, lbiX, sgn2Y, sgnX )
            return lbiR, sgnR
        else:
            return lbisum, -sgnsum

def pt_K( lbiX, lbiY, sgnX, sgnY, verbose=False ):
    (lbi3X, c3X), sgn3X = lbi.lbi_add( lbiX, lbiX, sgnX, sgnX )
    (lbi3X, c3X), sgn3X = lbi.lbi_add( lbi3X, lbiX, sgn3X, sgnX )
    (lbi3Y, c3Y), sgn3Y = lbi.lbi_add( lbiY, lbiY, sgnY, sgnY )
    (lbi3Y, c3Y), sgn3Y = lbi.lbi_add( lbi3Y, lbiY, sgn3Y, sgnY )
    (lbisum, csum), sgnsum = lbi.lbi_add( lbiX, lbiY, sgnX, sgnY )
    if verbose:
        print "In K: 3X, 3Y", lbi.lbi_lbi2dec( lbi3X, sgn3X ), lbi.lbi_lbi2dec( lbi3Y, sgn3Y )
        print "In K:  X+Y  ", lbi.lbi_lbi2dec( lbisum, sgnsum)
    if 1 == lbi.lbi_cmp( lbiX, lbiY, sgnX, sgnY ):
        lbimax, sgnmax = lbi3X, sgn3X
    else:
        lbimax, sgnmax = lbi3Y, sgn3Y
    if 1==sgnmax:
        (lbiR, cR), sgnR = lbi.lbi_sub( lbimax, lbisum, sgnmax, sgnsum )
    else:
        (lbiR, cR), sgnR = (lbisum, csum), -sgnsum
    return lbiR, sgnR

def pt_double_alt( lbiX, lbiY, sgnX, sgnY ):
    """See also: K. Kajiwara et al., http://arxiv.org/abs/0803.4062 and
    http://arxiv.org/pdf/0903.0331.pdf

    5 ADDSUBs + 6 CMPs
    """
    (lbi2X, c2X), sgn2X = lbi.lbi_add( lbiX, lbiX, sgnX, sgnX )
    (lbi3X, c3X), sgn3X = lbi.lbi_add( lbi2X, lbiX, sgn2X, sgnX )
    (lbi2Y, c2Y), sgn2Y = lbi.lbi_add( lbiY, lbiY, sgnY, sgnY )
    (lbi3Y, c3Y), sgn3Y = lbi.lbi_add( lbi2Y, lbiY, sgn2Y, sgnY )
    cmp = lbi.lbi_cmp( lbiX, lbiY, sgnX, sgnY )
    if 1==cmp:
        if 1==sgnX:
            lbiXX, sgnXX = lbiY, sgnY
        else:
            (lbiXX, cXX), sgnXX = lbi.lbi_sub( lbiY, lbi3X, sgnY, sgn3X )
        if 1==sgnY:
            (lbiYY, cYY), sgnYY = lbi.lbi_sub( lbi3Y, lbi2X, sgn3Y, sgn2X )
        else:
            lbiYY, sgnYY = lbiX, sgnX
    else:
        if 1==sgnX:
            (lbiXX, cXX), sgnXX = lbi.lbi_sub( lbi3X, lbi2Y, sgn3X, sgn2Y )
        else:
            lbiXX, sgnXX = lbi2Y, -sgn2Y
        if 1==sgnY:
            lbiYY, sgnYY = lbi2X, -sgn2X
        else:
            (lbiXX, cXX), sgnXX = lbi.lbi_sub( lbiX, lbi3Y, sgnX, sgn3Y )
    return lbiXX, lbiYY, sgnXX, sgnYY


def pt_double( lbiX, lbiY, sgnX, sgnY ):
    """See also: K. Kajiwara et al., http://arxiv.org/abs/0803.4062 and
    http://arxiv.org/pdf/0903.0331.pdf

    8 ADDSUBs + 10 CMPs
    """
    (lbi3X, c3X), sgn3X = lbi.lbi_add( lbiX, lbiX, sgnX, sgnX )
    (lbi3X, c3X), sgn3X = lbi.lbi_add( lbi3X, lbiX, sgn3X, sgnX )
    (lbi3Y, c3Y), sgn3Y = lbi.lbi_add( lbiY, lbiY, sgnY, sgnY )
    (lbi3Y, c3Y), sgn3Y = lbi.lbi_add( lbi3Y, lbiY, sgn3Y, sgnY )
    # Get [2]P x-coordinate
    if 1==sgnX:
        (lbi2X, c2X), sgn2X = lbi.lbi_add( lbiY, lbi3X, sgnY, sgn3X )
    else:
        (lbi2X, c2X), sgn2X = (lbiY, 0), sgnY
    if 1 == lbi.lbi_cmp( lbiX, lbiY, sgnX, sgnY ):
        (lbi2X, c2X), sgn2X = lbi.lbi_sub( lbi2X, lbi3X, sgn2X, sgn3X )
    else:
        (lbi2X, c2X), sgn2X = lbi.lbi_sub( lbi2X, lbi3Y, sgn2X, sgn3Y )
    # Get [2]P y-coordinate
    if 1==sgnY:
        (lbi2Y, c2Y), sgn2Y = lbi.lbi_add( lbiX, lbi3Y, sgnX, sgn3Y )
    else:
        (lbi2Y, c2Y), sgn2Y = (lbiX, 0), sgnX
    if 1 == lbi.lbi_cmp( lbiX, lbiY, sgnX, sgnY ):
        (lbi2Y, c2Y), sgn2Y = lbi.lbi_sub( lbi2Y, lbi3X, sgn2Y, sgn3X )
    else:
        (lbi2Y, c2Y), sgn2Y = lbi.lbi_sub( lbi2Y, lbi3Y, sgn2Y, sgn3Y )
    return lbi2X, lbi2Y, sgn2X, sgn2Y

def pt_sp( vcoeff, vlbi, vsgn ):
    vlen = len( vcoeff )
    lbiR, sgnR = np.full( lbi.LBI_WORDS, 0, dtype=np.uint32 ), 1
    for i in range(vlen):
        if 2==vcoeff[i]:
            (lbiC, cC), sgnC = lbi.lbi_add( vlbi[i], vlbi[i], vsgn[i], vsgn[i] )
            (lbiR, cR), sgnR = lbi.lbi_add( lbiR, lbiC, sgnR, sgnC )
            chk_carry( cR, '%d in %s' % (i, vcoeff) )
        if 1==vcoeff[i]:
            (lbiR, cR), sgnR = lbi.lbi_add( lbiR, vlbi[i], sgnR, vsgn[i] )
            chk_carry( cR, '%d in %s' % (i, vcoeff) )
    return lbiR, sgnR

def pt_coord_pre( vectors, vlbi, vsgn, lbineg, sgnneg ):
    (v1, v2, v3, v4) = vectors
    lbi1, sgn1 = pt_sp( v1, vlbi, vsgn )
    lbi2, sgn2 = pt_sp( v2, vlbi, vsgn )
    if 1==lbi.lbi_cmp( lbi1, lbi2, sgn1, sgn2 ):
        lbipos, sgnpos = lbi1, sgn1
    else:
        lbipos, sgnpos = lbi2, sgn2
    (lbiR, cR), sgnR = lbi.lbi_sub( lbipos, lbineg, sgnpos, sgnneg )
    return lbiR, sgnR

def pt_coord( vectors, vlbi, vsgn ):
    (v1, v2, v3, v4) = vectors
    lbi1, sgn1 = pt_sp( v1, vlbi, vsgn )
    lbi2, sgn2 = pt_sp( v2, vlbi, vsgn )
    if 1==lbi.lbi_cmp( lbi1, lbi2, sgn1, sgn2 ):
        lbipos, sgnpos = lbi1, sgn1
    else:
        lbipos, sgnpos = lbi2, sgn2
    lbi3, sgn3 = pt_sp( v3, vlbi, vsgn )
    lbi4, sgn4 = pt_sp( v4, vlbi, vsgn )
    if 1==lbi.lbi_cmp( lbi3, lbi4, sgn3, sgn4 ):
        lbineg, sgnneg = lbi3, sgn3
    else:
        lbineg, sgnneg = lbi4, sgn4
    (lbiR, cR), sgnR = lbi.lbi_sub( lbipos, lbineg, sgnpos, sgnneg )
    return lbiR, lbineg, sgnR, sgnneg
    
def pt_add( lbiXP, lbiYP, sgnXP, sgnYP,
            lbiXQ, lbiYQ, sgnXQ, sgnYQ,
            lbiK, sgnK):
    """See also: A. Nobe, http://arxiv.org/pdf/1111.0131.pdf"""
    arr = [ [ ([0,1,0,0], [2,0,1,1], [1,0,2,0], [0,2,0,1]),
              ([1,1,0,2], [0,0,1,0], [1,0,2,0], [0,2,0,1])],
            [ ([1,1,2,0], [0,0,0,1], [0,1,0,2], [2,0,1,0]),
              ([1,0,0,0], [0,2,1,1], [0,1,0,2], [2,0,1,0])],
            [ ([1,0,0,2], [0,2,1,0], [1,1,0,0], [0,0,1,1]),
              ([0,1,2,0], [2,0,0,1], [1,1,0,0], [0,0,1,1])]
        ]
    vlbi, vsgn = [ lbiXP, lbiYP, lbiXQ, lbiYQ ], [ sgnXP, sgnYP, sgnXQ, sgnYQ ]
    res = []
    for coeffs in arr:
        # 26 adds, 29 cmps down from 36 adds, 38 cmps (38 adds, 40 cmps)
        lbiX, lbineg, sgnX, sgnneg = pt_coord( coeffs[0], vlbi, vsgn )
        lbiY, sgnY = pt_coord_pre( coeffs[1], vlbi, vsgn, lbineg, sgnneg )
        lbiD, sgnD = pt_K_alt( lbiX, lbiY, sgnX, sgnY )
        res += [ (lbiX, lbiY, sgnX, sgnY, lbiD, sgnD) ]
        if sgnK==sgnD and all(lbiK==lbiD):
            return lbiX, lbiY, sgnX, sgnY
    print "-- Error in add"
    print lbi.lbi_lbi2dec(lbiXP, sgnXP), lbi.lbi_lbi2dec(lbiYP, sgnYP)
    print lbi.lbi_lbi2dec(lbiXQ, sgnXQ), lbi.lbi_lbi2dec(lbiYQ, sgnYQ)
    for (x,y,sx,sy,k,sk) in res:
        print 'x',lbi.lbi_lbi2dec(x, sx)
        print 'y',lbi.lbi_lbi2dec(y, sy)
        k, sk = pt_K(x, y, sx, sy, verbose=True)
        print 'k',lbi.lbi_lbi2dec(k, sk)
    exit(1)

def pt_nmap( bits, gx, gy, sgx, sgy,
             lbiK, sgnK ):
    x, y, sx, sy = gx, gy, sgx, sgy
    for c in bits[1:]:
        x, y, sx, sy = pt_double( x, y, sx, sy )
        if 1 == c:
            x, y, sx, sy = pt_add( x, y, sx, sy, gx, gy, sgx, sgy, lbiK, sgnK )
    return x, y, sx, sy

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tropical Hessian Pencil Group Law.')
    parser.add_argument('--threads', dest='N', metavar='N', type=int, default=16,
                        help='number of threads')
    parser.add_argument('--exp', dest='exp', metavar='N', type=int, default=10,
                        help='exponent')
    args = parser.parse_args()

    lbiX = np.random.randint( 2**29, size=lbi.LBI_WORDS )
    sgnX = 1
    lbiY = np.random.randint( 2**29, size=lbi.LBI_WORDS )
    sgnY = 1
    print lbiX
    print lbiY
    print lbi.lbi_lbi2dec( lbiX, sgnX )
    print lbi.lbi_lbi2dec( lbiY, sgnY )
    lbi.lbi_count_reset()
    lbiK, sgnK = pt_K_alt( lbiX, lbiY, sgnX, sgnY )
    print "K=",lbiK,lbi.lbi_lbi2dec( lbiK, sgnK )
    print "-- Hessian parameter K (adds: %d, cmps: %d)" % lbi.lbi_counts()    
    lbi.lbi_count_reset()
    lbi2X, lbi2Y, sgn2X, sgn2Y = pt_double_alt( lbiX, lbiY, sgnX, sgnY )
    print "-- Duplication (adds: %d, cmps: %d)" % lbi.lbi_counts()
    print lbi2X
    print lbi2Y
    print lbi.lbi_lbi2dec( lbi2X, sgn2X )
    print lbi.lbi_lbi2dec( lbi2Y, sgn2Y )
    lbiD, sgnD = pt_K( lbi2X, lbi2Y, sgn2X, sgn2Y )
    print "K=",lbi.lbi_lbi2dec( lbiD, sgnD )

    lbi.lbi_count_reset()
    (x,y,sgnx,sgny) = pt_add( lbiX, lbiY, sgnX, sgnY,
                              lbi2X, lbi2Y, sgn2X, sgn2Y,
                              lbiK, sgnK )
    lbiD, sgnD = pt_K(x,y,sgnx,sgny)
    print "-- Addition (adds: %d, cmps: %d)" % lbi.lbi_counts()
    print "X=",lbi.lbi_lbi2dec( x, sgnx )
    print "Y=",lbi.lbi_lbi2dec( y, sgny )
    print "K=",lbi.lbi_lbi2dec( lbiD, sgnD )

    # bits = np.random.randint(2, size=args.exp)
    # bits[0]=1
    # ex = np.array( [ c for c in bits ], dtype=np.ubyte )
    # EXP = bits[0]
    # for b in bits[1:]:
    #     EXP = 2.*EXP+b

    # t0 = time.clock()
    # (x,y,sgnx,sgny) = pt_nmap( ex, lbiX, lbiY, sgnX, sgnY,
    #                            lbiK, sgnK )
    # cpusecs = time.clock()-t0
    # print "CPU:", cpusecs, "secs"

    # lbiD, sgnD = pt_K(x,y,sgnx,sgny)
    # print "-- [%d]P" % (EXP), len(ex)
    # print "X=",lbi.lbi_lbi2dec( x, sgnx )
    # print "Y=",lbi.lbi_lbi2dec( y, sgny )
    # print "K=",lbi.lbi_lbi2dec( lbiD, sgnD )
    
