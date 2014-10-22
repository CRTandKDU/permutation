# all pairs of a,b
pairs = [ (a,b) for a in range(2,99+1) for b in range(2,99+1) if a>=b ]

# calculates map of solutions
def calc_map(oper):
    M={}
    for a,b in pairs:
        m = oper(a,b)
        if not m in M:
            M[m] = []
        M[m].append( (a,b) )
    return M

# function that tests for single solution
single = lambda lx: len(lx) == 1

# maps that hold the sum and the product solutions, 
# dictionaries with list values
S = calc_map(lambda a,b: a+b)
P = calc_map(lambda a,b: a*b)

# Rules list
rule_MrP_dont_know      = lambda p: not single (P[p])

rule_MrS_dont_know      = lambda s: not single (S[s])

rule_MrS_knew_MrP_doesnt_know = lambda s: all( [rule_MrP_dont_know( a*b ) 
                                                        for a,b in S[s] ] )
        
rule_MrP_now_knows      = lambda p: single( [ (a,b) for a,b in P[p] 
                                        if rule_MrS_knew_MrP_doesnt_know(a+b) ])

rule_MrS_knows_MrP_now_know = lambda s: single([ (a,b) for a,b in S[s] 
                                            if rule_MrP_now_knows(a*b) ])


# Solve it
for a, b in pairs:
    s,p = a+b, a*b
    if rule_MrP_dont_know(p) \
            and rule_MrS_dont_know(s) \
            and rule_MrS_knew_MrP_doesnt_know(s)\
            and rule_MrP_now_knows(p) \
            and rule_MrS_knows_MrP_now_know(s):
        print "Answer is:" , a,b
