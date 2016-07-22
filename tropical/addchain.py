"""@package Tropical
Exploration of group-based encryption in the tropical semiring.

Exploring add chains for tropical hessian group law.

"""

global pos, neg

vectors = [ "0011", "0102", "0201", "1020", "1100", "2010",
            "0001", "0010", "0100", "0120", "0210", "0211", "2001", "2011", "1000", "1002", "1102", "1120"]

arr = [ [ ([0,1,0,0], [2,0,1,1], [1,0,2,0], [0,2,0,1]),
          ([1,1,0,2], [0,0,1,0], [1,0,2,0], [0,2,0,1])],
        [ ([1,1,2,0], [0,0,0,1], [0,1,0,2], [2,0,1,0]),
          ([1,0,0,0], [0,2,1,1], [0,1,0,2], [2,0,1,0])],
        [ ([1,0,0,2], [0,2,1,0], [1,1,0,0], [0,0,1,1]),
          ([0,1,2,0], [2,0,0,1], [1,1,0,0], [0,0,1,1])]
    ]

def node_def( vects, attrs_p, attrs_n ):
    alph = ['0', '1', '2']
    for i in range(4):
        s = ''
        v = vects[i]
        for j in range(4):
            s += alph[ v[j] ]
        if i<2:
            print "%s %s;" % (s, attrs_p)
        else:
            print "%s %s;" % (s, attrs_n)

def nodes( a ):
    attrs_p = [ "[color=blue]", "[color=red]", "[color=green]" ]
    attrs_n = [ "[style=filled, fillcolor=lightblue]", "[style=filled, fillcolor=red]", "[style=filled,fillcolor=green]" ]
    for i in range(len(a)):
        coeffs = a[i]
        node_def( coeffs[0], attrs_p[i], attrs_n[i] )
        node_def( coeffs[1], attrs_p[i], attrs_n[i] )

def step( s1, s2 ):
    dif = int(s1)-int(s2)
    return dif==1 or dif==10 or dif==100 or dif==1000 or dif==2 or dif==20 or dif == 200 or dif == 2000

if __name__ == '__main__':
    # Output some dot file for graphviz
    print "digraph add_chain{"
    nodes( arr )
    for i in range(len(vectors)):
        for j in range(len(vectors)):
            if step(vectors[j],vectors[i]):
                print "\"%s\" -> \"%s\"" % (vectors[i],vectors[j])
    print "}"
