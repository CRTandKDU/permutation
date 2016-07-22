#!/usr/bin/env python
""" Exploring cryptographic applications of CAs
"""

import time, argparse
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image  as mpimg

class CAEngine:
    def __init__(self, radius, rule):
        n  = radius+radius+1
        nn = 1<<n
        rule_array = np.zeros( nn, dtype=np.ubyte )
        # Convert rule index to binary array
        s = format( rule, '0%db' % (nn) )
        for i in range( nn ):
            rule_array[i] = 1 if s[nn-1-i]=='1' else 0
        # print "Rule %d:" % (rule), rule_array
        self.radius, self.rule = radius, rule_array

    def toIndex( self, diameter ):
        """Given a diameter-sized slice, returns its integer value.
        """
        idx = 0
        for val in diameter:
            idx += idx + val
        return idx
    
    def rowPreimage( self, r, i ):
        """Finds diameter centered on index `i' of row `r'
        """
        n, diameter = len(r), np.empty( [0], dtype=np.ubyte )
        for j in range(i-self.radius,i+self.radius+1):
            diameter = np.append( diameter, r[j%n] )
        # print diameter, self.toIndex( diameter )
        return self.toIndex( diameter )

    def rowNext( self, r ):
        """Returns one (cylindric) iteration of rule on row `r'
        """
        n, rnext = len(r), np.zeros_like( r )
        for i in range(n):
            rnext[i] = self.rule[ self.rowPreimage( r, i ) ]
        return rnext

    def ruleLTogglep( self, p ):
        """Test for a left-toggle rule `p' passed as an np binarray
        """
        n = len(p)
        for i in range(n>>1):
            if p[i] == p[i+(n>>1)]:
                return False
        return True

    def ruleRTogglep( self, p ):
        """Test for a right-toggle rule `p' passed as an np binarray
        """
        n = len(p)
        for i in range(n>>1):
            if p[i<<1] == p[(i<<1)+1]:
                return False
        return True
    
    def bitmap( self, r, ntimes ):
        img = [ self.rowToBitmap( r ) ]
        for i in range(ntimes):
            rnext = self.rowNext( r )
            # print r, '--', rnext
            img += [ self.rowToBitmap( rnext ) ]
            r = np.copy( rnext )
            rnext = np.zeros_like(r)
        return img
            
    def rowToBitmap( self, row ):
        return [ [1.,1.,1.] if 0==x else [0.,0.,1.] for x in row ]

    def stringNext( self, s ):
        """Returns one iteration of rule on string `s'
        """
        n = len(s)-self.radius-self.radius
        snext = np.zeros( n, dtype=np.ubyte )
        for i in range(n):
            subs = s[i:i+self.radius+self.radius+1]
            # print subs, self.rule[ self.toIndex( subs ) ]
            snext[i] = self.rule[ self.toIndex( subs ) ]
        return snext

    def stringRightPrev( self, s, seed ):
        # Previous string though right-toggle rule
        prev = [ x for x in seed ]
        n = self.radius+self.radius+1
        for i in s:
            tst0, tst1 = (prev + [0])[-n:], (prev + [1])[-n:]
            # print i, tst0, self.rule[ self.toIndex( tst0 ) ], tst1, self.rule[ self.toIndex( tst1 ) ]
            if   i == self.rule[ self.toIndex( tst1 ) ]:
                prev = prev + [1]
            elif i == self.rule[ self.toIndex( tst0 ) ]:
                prev = prev + [0]
            else:
                print "Error"
        return np.array( prev, dtype=np.ubyte )

    def stringLeftPrev( self, s, seed ):
        # Previous string though left-toggle rule
        prev = [ x for x in seed ]
        n = self.radius+self.radius+1
        for i in s[::-1]:
            tst0, tst1 = ([0]+prev)[:n], ([1]+prev)[:n]
            # print i, tst0, self.rule[ self.toIndex( tst0 ) ], tst1, self.rule[ self.toIndex( tst1 ) ]
            if   i == self.rule[ self.toIndex( tst1 ) ]:
                prev = [1]+prev
            elif i == self.rule[ self.toIndex( tst0 ) ]:
                prev = [0]+prev
            else:
                print "Error"
        return np.array( prev, dtype=np.ubyte )

    def stringDec( self, s, nrounds=32 ):
        dec = np.copy(s)
        for i in range(nrounds):
            dec = self.stringNext( dec )
        return dec
            
    def stringRightEnc( self, s, nrounds=32 ):
        enc = np.copy(s)
        for i in range(nrounds):
            enc = self.stringRightPrev( enc, np.random.randint(2, size=(self.radius<<1)))
        return enc

    def stringLeftEnc( self, s, nrounds=32 ):
        enc = np.copy(s)
        for i in range(nrounds):
            enc = self.stringLeftPrev( enc, np.random.randint(2, size=(self.radius<<1)))
        return enc

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Explore cellular automata.')
    parser.add_argument('--threads',
                        dest='threads', metavar='N', type=int, default=255,
                        help='number of threads')
    parser.add_argument('--radius',
                        dest='radius', metavar='N', type=int, default=3,
                        help='size of preimage')
    parser.add_argument('--rule',
                        dest='rule', metavar='N', type=int, default=1,
                        help='rule number (Wolfram notation)')
    args = parser.parse_args()
    if 0 == args.threads & 1:
        args.threads += 1

    def toBinarray( x, nn=8 ):
        rule_array = np.zeros( nn, dtype=np.ubyte )
        s = format( x, '0%db' % (nn) )
        for i in range( nn ):
            rule_array[i] = 1 if s[nn-1-i]=='1' else 0
        return rule_array

    def toInteger( arr ):
        ret, exp = 0, 1
        for a in arr:
            ret += exp*a
            exp <<= 1
        return ret
    
    # Instantiate CA
    ca = CAEngine( args.radius, args.rule )
    n  = args.radius+args.radius+1
    nn = 1<<n
    hh = np.zeros( 256, dtype=np.ubyte )
    g30  = nx.Graph()
    dg30 = nx.DiGraph()
    print "digraph G%d {" % (args.rule)
    for x in range(256):
        # print x, toInteger(ca.rowNext( toBinarray(x, nn)) )
        y = toInteger(ca.rowNext( toBinarray(x, nn) ) )
        hh[y] += 1
        g30.add_edge( x, y )
        dg30.add_edge( x, y )
        print "%d -> %d;" % (x, y)
    print "}"
    print "/* Comments to dotfile"
    print "G%d: Nodes w/o antecedents" % (args.rule)
    print np.argwhere(hh==0).flatten()
    print "G%d: %d connected components." % (args.rule, nx.number_connected_components(g30) )
    print [ len(c) for c in nx.connected_components(g30) ]
    print "G%d: %d cycles." % (args.rule,  len(list(nx.simple_cycles(dg30))))
    print "*/"
    
    # Display cylindric iterations
    # row = np.zeros( args.threads, dtype=np.ubyte )
    # row[ (args.threads-1)>>1 ] = 1
    # img = ca.bitmap( row, (args.threads-1)>>1 )
    # # Print img
    # plt.title( "Rule %d" % (args.rule) )
    # imgplot = plt.imshow( np.array(img, dtype=np.float32), interpolation='none'  )
    # plt.show()

    # String operations
    # s = np.random.randint(2, size=32)
    # print s
    # print ca.stringNext(s)
    # print
    # if ca.ruleRTogglep( ca.rule ):
    #     reed =  np.random.randint(2, size=(args.radius<<1))
    #     prev =  ca.stringRightPrev( s, reed )
    #     print "Right-toggle"
    #     print prev
    #     print reed
    #     print ca.stringNext(prev)
    #     print s
    #     encoded = ca.stringRightEnc( s, 16 )
    #     print np.packbits(encoded)
    #     print ca.stringDec( encoded, 16 )
    # if ca.ruleLTogglep( ca.rule ):
    #     reed =  np.random.randint(2, size=(args.radius<<1))
    #     prev =  ca.stringLeftPrev( s, reed )
    #     print "Left-toggle"
    #     print prev
    #     print reed
    #     print ca.stringNext(prev)
    #     print s
    #     encoded = ca.stringLeftEnc( s, 16 )
    #     print np.packbits(encoded)
    #     print ca.stringDec( encoded, 16 )

        # print "Right toggle:"
    # for x in range(256):
    #     # Convert rule index to binary array
    #     rule_array = np.zeros( 8, dtype=np.ubyte )
    #     s = format( x, '08b' )
    #     for i in range(8):
    #         rule_array[i] = 1 if s[8-1-i]=='1' else 0
    #     if ca.ruleRTogglep( rule_array ):
    #         print x, s
    # print
    # print "Left toggle:"
    # for x in range(256):
    #     # Convert rule index to binary array
    #     rule_array = np.zeros( 8, dtype=np.ubyte )
    #     s = format( x, '08b' )
    #     for i in range(8):
    #         rule_array[i] = 1 if s[8-1-i]=='1' else 0
    #     if ca.ruleLTogglep( rule_array ):
    #         print x,
    # print
        
    
