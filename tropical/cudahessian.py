"""@package Tropical
Exploration of group-based encryption in the tropical semiring.
"""

import sys
import time
import numpy as np
import argparse

import pycuda.autoinit
import pycuda.driver as drv
import pycuda.tools
from pycuda.compiler import SourceModule

mod = SourceModule("""
typedef int fieldelt;

__device__ void devicedouble( fieldelt *x, fieldelt *y )
{
  const int i = threadIdx.x;
  int dx, dy;
  dx = y[i] + 3*max(x[i],0) - 3*max(x[i],y[i]);
  dy = x[i] + 3*max(y[i],0) - 3*max(x[i],y[i]);
  x[i] = dx;
  y[i] = dy;
}

__device__ void deviceadd( fieldelt *xp, fieldelt *yp, fieldelt *xq, fieldelt *yq,
                           fieldelt K )
{
  const int i = threadIdx.x;
  int xpq[3], ypq[3], j, m;
  xpq[0] = max( yp[i], 2*xp[i]+xq[i]+yq[i] ) - max( xp[i]+2*xq[i], 2*yp[i] + yq[i] );
  ypq[0] = max( xp[i]+yp[i]+2*yq[i], xq[i] ) - max( xp[i]+2*xq[i], 2*yp[i] + yq[i] );
  xpq[1] = max( xp[i]+yp[i]+2*xq[i], yq[i] ) - max( yp[i]+2*yq[i], 2*xp[i] + xq[i] );
  ypq[1] = max( xp[i], 2*yp[i]+xq[i]+yq[i] ) - max( yp[i]+2*yq[i], 2*xp[i] + xq[i] );
  xpq[2] = max( xp[i]+2*yq[i], 2*yp[i]+xq[i]) - max( xp[i]+yp[i], xq[i] + yq[i] );
  ypq[2] = max( xp[i]+yp[i]+2*yq[i], xq[i] ) - max( xp[i]+yp[i], xq[i] + yq[i] );
  for( j=0; j<3; j++ ){
    m = max( 3*xpq[j], 3*ypq[j] );
    m = max( m, 0 );
    if( xpq[j]+ypq[j]+K == m ){
	xp[i]=xpq[j];
	yp[i]=ypq[j];
	return;
      }
  }
}

__global__ void kernelExp( fieldelt *ax, fieldelt *ay,
			   fieldelt *gx, fieldelt *gy,
			   unsigned char * exp, fieldelt n,
			   fieldelt K ){
  const int i = threadIdx.x;
  int j;
  ax[i] = gx[i];
  ay[i] = gy[i];
  for( j=0; j<n; j++ ){
    devicedouble( ax, ay );
    if( 1 == exp[j] ){
      deviceadd( ax, ay, gx, gy, K );
    }
  }
}

""")

gpuExp = mod.get_function( "kernelExp" )

class THessian:
    """Tropical elliptic curve in Hessian form."""
    K = 0
    
    def __init__(self, cst):
        self.K = np.int32(cst)

    def tequation( self, x, y ):
        # Equation in tropical Hessian form
        return [ 3*x, 3*y , x+y+self.K, 0 ]

    def tduplicate( self, x, y ):
        """Kajiwara's formula for duplication."""
        return (np.int32(y+3*max(x,0)-3*max(x,y)),
                np.int32(x+3*max(y,0)-3*max(x,y)) )
    
    def tcyclep( self, x, y ):
        # Cycle: max( 3x, 3y, 0 ) == x+y+K
        X, Y = np.int32(x), np.int32(y)
        return 0 == max( 3*X, 3*Y, 0 ) - (X + Y + self.K) 

    def tedge( self, x, y ):
        """Find edge of cycle point (x,y)."""
        edge = 0
        m = np.int32( max( x, y, 0 ) )
        if 0 == x - m :
            edge = 1
        if 0 == y - m :
            edge = 2
        if 0 == m :
            edge = 3
        return edge

    def taddition( self, xp, yp, xq, yq ):
        """Nobe's addition formula."""
        X, Y, X1, Y1 = xp, yp, xq, yq
        Ptransforms = [
            ( np.int32(max(Y,(2*X+X1+Y1) )-max((X+2*X1) ,(2*Y+Y1) )) ,
              np.int32(max((X+Y+2*Y1) ,X1)-max((X+2*X1) ,(2*Y+Y1) )) ,
              'P1' ),
            ( np.int32(max((X+Y+2*X1) ,Y1)-max((Y+2*Y1) ,(2*X+X1) )) ,
              np.int32(max(X,(2*Y+X1+Y1) )-max((Y+2*Y1) ,(2*X+X1) )) ,
              'P2'  ),
            ( np.int32(max((X+2*Y1) ,(2*Y+X1) )-max((X+Y) ,(X1+Y1) )) ,
              np.int32(max((Y+2*X1) ,(2*X+Y1) )-max((X+Y) ,(X1+Y1) )) ,
              'P3' )
        ]
        for (px, py, s) in Ptransforms:
            if self.tcyclep( px, py ):
                return (px, py)
        return (0,0)

    def tnmap( self, bits, gx, gy ):
        x, y = gx, gy
        for c in bits[1:]:
            x, y = self.tduplicate( x, y )
            if '1' == c:
                x,y = self.taddition( x, y, gx, gy )
        return x, y

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tropical Hessian Pencil Group Law.')
    parser.add_argument('--threads', dest='N', metavar='N', type=int, default=16,
                        help='number of threads')
    parser.add_argument('--exp', dest='exp', metavar='N', type=int, default=10,
                        help='exponent')
    args = parser.parse_args()

    x, y = np.int32(7883), np.int32(6163) # Base point
    K = 3*max( x, y, 0 ) - x - y # From cycle equation
    print "Base point: (%d,%d), coefficient: %d" % (x,y,K)
    th = THessian( K )

    THREADS = args.N
    EXP = args.exp
    gx = np.full( THREADS, x, dtype=np.int32 ) 
    gy = np.full( THREADS, y, dtype=np.int32 )
    ax = np.full( THREADS, 0, dtype=np.int32 ) 
    ay = np.full( THREADS, 0, dtype=np.int32 )
    ex = np.array( [ c for c in bin(EXP)[3:] ], dtype=np.ubyte )
    nn = np.int32( ex.size )
    KK = np.int32( K )
    print bin(10), ex, nn

    t0 = time.clock()
    gpuExp( drv.Out(ax), drv.Out(ay),
            drv.In(gx), drv.In(gy),
            drv.In(ex), nn,
            KK,
            block=(THREADS,1,1), grid=(1,1) )
    cpusecs = time.clock()-t0
    print "GPU:", cpusecs, "secs"
    print ax
    print ay
    
    t0 = time.clock()
    for i in range(THREADS):
        (xx,yy) = th.tnmap(bin(EXP)[2:], x, y)
    cpusecs = time.clock()-t0
    print "CPU:", cpusecs, "secs"
    print xx
    print yy
        

