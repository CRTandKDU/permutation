#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
""" Exploring the Tropical Hesse curve

    See also: 
    [[Kajiwara et al.][http://arxiv.org/pdf/0903.0331.pdf]].
    [[Atsushi Nobe][http://www.kurims.kyoto-u.ac.jp/~kyodo/kokyuroku/contents/pdf/1765-14.pdf]]
    [[Atsushi Nobe][http://arxiv.org/pdf/1111.0131.pdf]]

"""

import matplotlib.pyplot as plt
import numpy as np

class Thessian:
    """Tropical Hesse curve."""

    def __init__(self, (X, Y)):
        # Defining point on the cycle
        self.Xpub, self.Ypub = X, Y
        # Parameter
        self.K = max(3*X,3*Y,0)-X-Y

    def plot( self, plt ):
        vertices = [ (-self.K, 0, 'V1'),
                     (0, -self.K, 'V2'),
                     (self.K, self.K, ' 0') ]
        for (vx, vy, s) in vertices :
            plt.plot( vx, vy, 'bo' )
            plt.text( vx, vy+2, s, fontdict=font )
        for i in range(3):
            xc = [ vertices[i%3][0], vertices[(i+1)%3][0] ]
            yc = [ vertices[i%3][1], vertices[(i+1)%3][1] ]
            plt.plot( xc, yc, 'b-' )
        

    def halving_tree( self, (X,Y), n ):
        if 1==n :
            return self.halving( (X,Y) )
        else:
            res = []
            for (A,B) in self.halving( (X,Y) ):
                res += self.halving_tree( (A,B), n-1 )
            return res

    def doubling( self, (X, Y) ):
        return Y+3*max(0,X)-3*max(X,Y), X+3*max(0,Y)-3*max(X,Y)

    def halving( self, (X,Y) ):
        f = self.face( (X,Y) )
        if 1==f or 2==f :
            return [
                ( Y, (Y+self.K)/2. ),
                ( (Y-X-self.K)/2., (X-Y-self.K)/2. )
                ]
        if 3==f or 4==f :
            return [
                ( Y, (Y+self.K)/2. ),
                ( (X+self.K)/2., X )
                ]
        if 5==f or 6==f :
            return [
                ( (Y-X-self.K)/2., (X-Y-self.K)/2. ),
                ( (X+self.K)/2., X )
                ]

    def oncyclep( self, (X,Y) ):
        return X+Y+self.K == max(3*X,3*Y,0)

    def face( self, (X,Y) ):
        if Y>=X:
            if X>=0:
                return 1
            elif Y>=0:
                return 2
            else:
                return 3
        else:
            if X<=0:
                return 4
            elif Y<=0:
                return 5
            else:
                return 6

    def toString( self ):
        return "--- Tropical Hesse: K=%d, Ppub=(%d,%d) on face %d." % (self.K, self.Xpub, self.Ypub, self.face((self.Xpub,self.Ypub)) )

if __name__ == '__main__':
    Ppub = (17, -15)
    th = Thessian( Ppub )
    print th.toString()
    print th.doubling( Ppub ) , th.face(th.doubling( Ppub ))
    halves = th.halving_tree( Ppub, 7 )
    for half in halves:
        print half, th.face(half), th.doubling( half )
    
    font = {'family': 'serif',
            'color':  'blue',
            'weight': 'normal',
            'size': 10,
    }
    plt.title( 'Halving on the Tropical Hesse curve' )
    th.plot( plt )
    plt.plot( Ppub[0], Ppub[1], 'ro' )
    plt.text( Ppub[0], Ppub[1]+2, 'P', fontdict=font )
    for (X,Y) in halves:
        plt.plot( X, Y, 'r+' )
    plt.show()
