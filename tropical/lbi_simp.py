"""@package Tropical
Exploration of group-based encryption in the tropical semiring.

Tropical Hessian Pencil group law. Simplified formulas.

"""
import time, argparse
import matplotlib.pyplot as plt
import numpy as np
import lbi

def point_face( xr, sxr, yr, syr ):
    if (1,-1)==(sxr,syr) : return 5
    if (-1,1)==(sxr,syr) : return 2
    cmpyx = lbi.lbi_cmp( xr, yr, sxr, syr )
    if (1,1)==(sxr,syr) :
        if 1==cmpyx : return 6
        else : return 1
    elif (-1,-1)==(sxr,syr) :
        if 1==cmpyx : return 4
        else : return 3
    else:
        return 0

def line_center( xp, sxp, yp, syp,
                 xq, sxq, yq, syq ):
    xcmp = lbi.lbi_cmp( xp, xq, sxp, sxq )
    ycmp = lbi.lbi_cmp( yp, yq, syp, syq )
    # P, Q are on edges 2 and 3
    if -1==xcmp*ycmp :
        if xcmp==1:
            (xb, sxb, yb, syb) = (xq, sxq, yq, syq)
            (xc, sxc, yc, syc) = (xp, sxp, yp, syp)
            conf = 'CB'
        else:
            (xb, sxb, yb, syb) = (xp, sxp, yp, syp)
            (xc, sxc, yc, syc) = (xq, sxq, yq, syq)
            conf = 'BC'
        return (xc, sxc, yb, syb, conf)
    # One of P or Q in on edge 2 or 3
    else :
        if 1==xcmp:
            (subyxinf, cyxinf), sgnyxinf = lbi.lbi_sub( yq, xq, syq, sxq )
            (subyx, cyx), sgnyx          = lbi.lbi_sub( yp, xp, syp, sxp )
            cmpyx = lbi.lbi_cmp( subyx, subyxinf, sgnyx, sgnyxinf )
            if 1==cmpyx:
                (add, cadd), sadd = lbi.lbi_add( xq, subyx, sxq, sgnyx )
                return( xq, sxq, add, sadd, 'AC' )
            else:
                (sub, csub), ssub = lbi.lbi_sub( yq, subyx, syq, sgnyx )
                return( sub, ssub, yq, syq, 'AB' )
        else:
            (subyxinf, cyxinf), sgnyxinf = lbi.lbi_sub( yp, xp, syp, sxp )
            (subyx, cyx), sgnyx          = lbi.lbi_sub( yq, xq, syq, sxq )
            cmpyx = lbi.lbi_cmp( subyx, subyxinf, sgnyx, sgnyxinf )
            if 1==cmpyx:
                (add, cadd), sadd = lbi.lbi_add( xp, subyx, sxp, sgnyx )
                return( xp, sxp, add, sadd, 'CA' )
            else:
                (sub, csub), ssub = lbi.lbi_sub( yp, subyx, syp, sgnyx )
                return( sub, ssub, yp, syp, 'BA' )
    return( 0, 0, 0, 0, '')

if __name__ == '__main__':
    def randsgn():
        s = 1
        if np.random.randint(100)>50:
            s = -1
        return s
    
    vp = 2**28
    lbiXP = np.random.randint( vp, size=lbi.LBI_WORDS )
    sgnXP = randsgn()
    lbiYP = np.random.randint( vp, size=lbi.LBI_WORDS )
    sgnYP = randsgn()
    lbiXQ = np.random.randint( vp, size=lbi.LBI_WORDS )
    sgnXQ = randsgn()
    lbiYQ = np.random.randint( vp, size=lbi.LBI_WORDS )
    sgnYQ = randsgn()
    print "(%10d,%10d)" % (lbiXP,lbiYP)
    print "(%10d,%10d)" % (lbiXQ,lbiYQ)
    lbi.lbi_count_reset()
    (xr, sxr, yr, syr, conf) = line_center( lbiXP, sgnXP, lbiYP, sgnYP,
                                      lbiXQ, sgnXQ, lbiYQ, sgnYQ )
    print "-- Line Center (adds: %d, cmps: %d)" % lbi.lbi_counts()
    print lbi.lbi_lbi2dec( xr, sxr )
    print lbi.lbi_lbi2dec( yr, syr )
    print conf
    print "Face:", point_face( xr, sxr, yr, syr )
    
    bfont = {'family': 'serif',
            'color':  'blue',
            'weight': 'normal',
            'size': 10,
        }
    f, ax = plt.subplots()
    ax.axis( [-vp*4, vp*4, -vp*4, vp*4], visible=True )
    ax.plot( [-vp*4, vp*4], [0, 0], linestyle='--', color='cornflowerblue' )
    ax.plot( [0, 0], [-vp*4, vp*4], linestyle='--', color='cornflowerblue' )
    ax.plot( [-vp*4, vp*4], [-vp*4, vp*4], linestyle='--', color='cornflowerblue' )
    ax.plot( lbi.lbi_lbi2dec( lbiXP, sgnXP ),
             lbi.lbi_lbi2dec( lbiYP, sgnYP ), 'bo' )
    ax.text( lbi.lbi_lbi2dec( lbiXP, sgnXP ),
             lbi.lbi_lbi2dec( lbiYP, sgnYP ),
             'P', fontdict=bfont )
    
    ax.plot( lbi.lbi_lbi2dec( lbiXQ, sgnXQ ),
             lbi.lbi_lbi2dec( lbiYQ, sgnYQ ), 'bo' )
    ax.text( lbi.lbi_lbi2dec( lbiXQ, sgnXQ ),
             lbi.lbi_lbi2dec( lbiYQ, sgnYQ ),
             'Q', fontdict=bfont )

    ax.plot( lbi.lbi_lbi2dec( xr, sxr ),
             lbi.lbi_lbi2dec( yr, syr ), 'ro' )
    

    plt.show()

