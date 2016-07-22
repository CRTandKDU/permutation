#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
""" Explorations in tropical elliptic curves. 

    See also: 
    [[Kajiwara et al.][http://arxiv.org/pdf/0903.0331.pdf]].
    [[Atsushi Nobe][http://www.kurims.kyoto-u.ac.jp/~kyodo/kokyuroku/contents/pdf/1765-14.pdf]]
    [[Atsushi Nobe][http://arxiv.org/pdf/1111.0131.pdf]]

"""

import matplotlib.pyplot as plt
import numpy as np

def anc_unsignedbytes( data ):
    """Convert a bytearray into an integer, considering the first bit as
    sign. The data must be big-endian."""
    negative = False # data[0] & 0x80 > 0

    if negative:
        inverted = bytearray(~d % 256 for d in data)
        return -signedbytes(inverted) - 1

    encoded = str(data).encode('hex')
    return int(encoded, 16)

def anc_randomint( size=32 ):
    b = bytearray()
    b.extend( np.random.bytes( size ) )
    return anc_unsignedbytes( b )

class THessian:
    """Tropical elliptic curve in Hessian form."""
    K = 0
    
    def __init__(self, cst):
        self.K = np.float32(cst)

    def tequation( self, x, y ):
        # Equation in tropical Hessian form
        return [ 3*x, 3*y , x+y+self.K, 0 ]

    def tduplicate( self, x, y ):
        """Kajiwara's formula for duplication."""
        return (np.float32(y+3*max(x,0)-3*max(x,y)),
                np.float32(x+3*max(y,0)-3*max(x,y)) )
    
    def tcyclep( self, x, y ):
        # Cycle: max( 3x, 3y, 0 ) == x+y+K
        X, Y = np.float32(x), np.float32(y)
        return abs( max( 3*X, 3*Y, 0 ) - (X + Y + self.K) ) < np.finfo(np.float32(0.0)).resolution

    def tedge( self, x, y ):

"""Find edge of cycle point (x,y)."""
        edge = 0
        m = np.float32( max( x, y, 0 ) )
        if abs(x - m) < np.finfo(np.float32(0.0)).resolution :
            edge = 1
        if abs(y - m) < np.finfo(np.float32(0.0)).resolution:
            edge = 2
        if m < np.finfo(np.float32(0.0)).resolution:
            edge = 3
        return edge

    def taddition( self, xp, yp, xq, yq ):
        """Nobe's addition formula."""
        edge_p, edge_q = self.tedge( xp, yp ), self.tedge( xq, yq )
        X, Y, X1, Y1 = xp, yp, xq, yq
        Ptransforms = [
            ( np.float32(max(Y,(2*X+X1+Y1) )-max((X+2*X1) ,(2*Y+Y1) )) ,
              np.float32(max((X+Y+2*Y1) ,X1)-max((X+2*X1) ,(2*Y+Y1) )) ,
              'P1' ),
            ( np.float32(max((X+Y+2*X1) ,Y1)-max((Y+2*Y1) ,(2*X+X1) )) ,
              np.float32(max(X,(2*Y+X1+Y1) )-max((Y+2*Y1) ,(2*X+X1) )) ,
              'P2'  ),
            ( np.float32(max((X+2*Y1) ,(2*Y+X1) )-max((X+Y) ,(X1+Y1) )) ,
              np.float32(max((Y+2*X1) ,(2*X+Y1) )-max((X+Y) ,(X1+Y1) )) ,
              'P3' )
        ]
        for (px, py, s) in Ptransforms:
            if self.tcyclep( px, py ):
                return (px, py)
        return (0,0)
   

    def plot_iterates( self, plt, x, y, n=100 ):
        plt.plot( x, y, 'ro' )
        plt.text( x, y+2, 'P', fontdict=font )
        (x2, y2) = self.tduplicate( x, y )
        for i in range(n):
            plt.plot( x2, y2, 'r+' )
            (x2, y2) = self.taddition( x, y, x2, y2 )
            # plt.text( x, y+2, '%d'%(i+2), fontdict=font )

    def plot( self, plt, vp=10 ):
        plt.axis( [-vp, vp, -vp, vp], visible=True )
        xcoords = [ -self.K, self.K ]
        ycoords = [ 0, self.K ]
        plt.plot( xcoords, ycoords, 'b-' )
        xcoords = [ 0, self.K ]
        ycoords = [ -self.K, self.K ]
        plt.plot( xcoords, ycoords, 'b-' )
        xcoords = [ -self.K, 0 ]
        ycoords = [ 0, -self.K ]
        plt.plot( xcoords, ycoords, 'b-' )
        xcoords = [ -self.K, -vp ]
        ycoords = [ 0, 0 ]
        plt.plot( xcoords, ycoords, 'b-' )
        xcoords = [ 0, 0 ]
        ycoords = [ -self.K, -vp ]
        plt.plot( xcoords, ycoords, 'b-' )
        xcoords = [ self.K, vp ]
        ycoords = [ self.K, vp ]
        plt.plot( xcoords, ycoords, 'b-' )
        plt.plot( self.K, self.K, 'bo' )
        plt.text( self.K, self.K+2, 'O', fontdict=font )
        
if __name__ == '__main__':
    font = {'family': 'serif',
            'color':  'blue',
            'weight': 'normal',
            'size': 10,
        }
    x, y = np.float32(100./19.), np.float32(100./31.)
    # x, y = np.float32(3.54), np.float32(7.22)
    K = 3*max( x, y, 0 ) - x - y # From cycle equation
    th = THessian( K )

    (x2, y2) = th.tduplicate( x, y )
    print 'P on cycle: ', th.tcyclep( x, y ), th.tedge( x, y )
    print 'Q on cycle: ', th.tcyclep( x2, y2 ), th.tedge( x2, y2 )
    
    f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    ax1.set_title('Group law on the tropical Hessian')
    ax1.set_xlabel('100 iterations')
    th.plot( ax1, vp=25 )
    th.plot_iterates( ax1, x, y, n = 100 )
    ax2.set_xlabel('Iterations')
    for i in range( 20 ):
        ax2.plot( i, y2, 'r+' )
        (x2, y2) = th.taddition( x2, y2, x, y )
        print i, y2
    # ax1.plot( x2, y2, 'ro' );
    # (vx, vy) = th.taddition(x,y,x2,y2)
    # ax1.plot( vx, vy, 'bo' )
    # ax1.text( vx, vy+2, '3P', fontdict=font )
    # print vx, vy, th.tcyclep(vx,vy), th.tedge( vx, vy )

    plt.show()

    # p, q = anc_randomint(size=2), anc_randomint(size=2)
    # print p, q
    # Ax, Ay, i = x, y, p
    # while i>0:
    #     (Ax, Ay) = th.tduplicate( Ax, Ay )
    #     i -= 1
    # print 'Alice public:', Ax, Ay
    # Bx, By, i = x, y, q
    # while i>0:
    #     (Bx, By) = th.tduplicate( Bx, By )
    #     i -= 1
    # print 'Bob public:  ', Bx, By
    # i = q
    # while i>0:
    #     (Ax, Ay) = th.tduplicate( Ax, Ay )
    #     i -= 1
    # print 'Alice shared: ', Ax, Ay
    # i = p
    # while i>0:
    #     (Bx, By) = th.tduplicate( Bx, By )
    #     i -= 1
    # print 'Bob shared:   ', Bx, By
