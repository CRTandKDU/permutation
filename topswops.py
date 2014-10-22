#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#
# Topswops
# See also: [https://oeis.org/A000375]

global P, N

# Generate permutations
def p_extend( perm, n, Q ):
    for i in range( 1+len(perm) ):
        Q += [ perm[:i] + [ n ] + perm[i:] ]
    return Q

def pset_next( n, Q, PSET ):
    for perm in Q:
        p_extend( perm, n, PSET )
    return PSET

# x_0 reverse operation
def op_reverse( perm ):
    rev = []
    x0  = perm[0]
    for i in range(x0):
        rev += [ perm[x0-i-1] ]
    rev += perm[x0:]
    # print rev
    return rev

def op_reverse_fp( perm ):
    count = 0
    while 1 != perm[0]:
        count += 1
        perm = op_reverse( perm )
    return count

def op_reverse_max( Q ):
    M = 0
    for perm in Q:
        count = op_reverse_fp( perm )
        if count>M:
            M = count
    return M

def op_wilf( perm ):
    wilf = 0
    for i in range(len(perm)):
        if i+1==perm[i]:
            wilf += 2**(i+1)
    return wilf

def op_name( perm ):
    return "\"%s (%2d)\"" % (''.join(map(str,perm)), op_wilf(perm))
            
if __name__ == "__main__":
    # Produce graph in dot language
    N = 4
    P = [ [1] ]
    for i in range(2,N+1):
        P = pset_next(i, P, [])
    print "digraph TOPSWOPS{"
    invariants = []
    for perm in P:
        if 1 != perm[0]:
            print "%s -> %s" % ( op_name(perm), op_name(op_reverse(perm)) )
        else:
            invariants += [ perm ]
    # Align invariants (1 in first position) at bottom of page
    print "{ rank=same;", " ".join([op_name(x) for x in invariants ]), "}"
    print "}"

    # # Compute Wilf index of perm and op_reverse(perm)
    # for perm in P:
    #     print perm, op_wilf(perm), op_wilf( op_reverse(perm) )
         
    # Uncomment to compute list of maximum number of moves
    # print "N\tMAX\tTOT.\tBINS"
    # for n in range(2,6):
    #     N = n+1
    #     # Generate permutation set
    #     P = []
    #     P += [ [1] ]
    #     for i in range(2, N):
    #         P = pset_next( i, P, [] )
    #     # Enumerate op counts
    #     M = 1+op_reverse_max(P)
    #     bins = [ 0 for x in range(M) ]
    #     for perm in P:
    #         count = op_reverse_fp(perm)
    #         bins[ count ] += 1
    #     print "%d\t%d\t%d\t%s" % (n, M-1, sum(bins), bins )
        
