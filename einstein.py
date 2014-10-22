#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#

# The so-called Einstein problem translated to DIMACS-formatted CNF constraints.

# ·  L'Anglais habite la maison rouge.
# ·  L'Espagnol adore son chien.
# ·  L'Islandais est ingénieur.
# ·  On boit du café dans la maison verte.
# ·  La maison verte est située immédiatement à gauche de la maison blanche.
# ·  Le sculpteur possède un âne.
# ·  Le diplomate habite la maison jaune.
# ·  Le Norvégien habite la première maison à gauche.
# ·  Le médecin habite la maison voisine de celle où demeure le propriétaire du renard.
# ·  La maison du diplomate est voisine de celle où il y a un cheval.
# ·  On boit du lait dans la maison du milieu.
# ·  Le Slovène boit du thé.
# ·  Le violoniste boit du jus d'orange.
# ·  Le Norvégien demeure à côté de la maison bleue

import argparse, string
# N: Number of individual objects -- here houses
global N, fr

N = 5
fr = { "rouge": 0, "vert": 1, "blanc": 2, "bleu": 3, "jaune": 4,
       "anglais": 5, "espagnol": 6, "islandais": 7, "norvégien": 8, "slovène": 9,
       "thé": 10, "café": 11, "eau": 12, "jus": 13, "lait": 14,
       "cheval": 15, "âne": 16, "renard": 17, "chien": 18, "zèbre": 19,
       "diplomate": 20, "sculpteur": 21, "médecin": 22, "violoniste": 23, "ingénieur": 24
       }

def val_constraint( x, y ):
    return x + N*y

def val_unique( writep, f, low, hi ):
    cnf_count = 0;
    for x in range(low, hi):
        dimacs = ""
        for house in range(1,N+1):
            dimacs += "%d " % val_constraint( house, x )
        dimacs += "0\n"
        cnf_count += 1
        if writep: 
            f.write( dimacs )
        for house in range(1,N+1):
            for other_house in range(1,house):
                cnf_count += 1
                if writep:
                    f.write( "-%d -%d 0\n" % ( val_constraint( house, x ), 
                                               val_constraint( other_house, x ) ) )
            for other_x in range(low, hi):
                if other_x!=x:
                    cnf_count += 1
                    if writep: 
                        f.write( "-%d -%d 0\n" % ( val_constraint( house, x ), 
                                                   val_constraint( house, other_x ) ) )
    return cnf_count

def dimacs_gen( f,  writep ):
    cnf_count = 0
    # Generate DIMACS output
    cnf_count += val_unique( writep, f,   0, N )                    
    cnf_count += val_unique( writep, f,   N, 2*N )                    
    cnf_count += val_unique( writep, f, 2*N, 3*N )                    
    cnf_count += val_unique( writep, f, 3*N, 4*N )                    
    cnf_count += val_unique( writep, f, 4*N, 5*N )                    

# ·  L'Anglais habite la maison rouge.
    for house in range(1,N+1):
        cnf_count += 2
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house, fr["anglais"] ),
                                      val_constraint( house, fr["rouge"] ) ))
            f.write( "%d -%d 0\n" % ( val_constraint( house, fr["anglais"] ),
                                      val_constraint( house, fr["rouge"] ) ))
    
# ·  L'Espagnol adore son chien.
    for house in range(1,N+1):
        cnf_count += 2
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house, fr["espagnol"] ),
                                      val_constraint( house, fr["chien"] ) ))
            f.write( "%d -%d 0\n" % ( val_constraint( house, fr["espagnol"] ),
                                      val_constraint( house, fr["chien"] ) ))

# ·  L'Islandais est ingénieur.
    for house in range(1,N+1):
        cnf_count += 2
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house, fr["islandais"] ),
                                      val_constraint( house, fr["ingénieur"] ) ))
            f.write( "%d -%d 0\n" % ( val_constraint( house, fr["islandais"] ),
                                      val_constraint( house, fr["ingénieur"] ) ))
# ·  On boit du café dans la maison verte.
    for house in range(1,N+1):
        cnf_count += 2
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house, fr["café"] ),
                                      val_constraint( house, fr["vert"] ) ))
            f.write( "%d -%d 0\n" % ( val_constraint( house, fr["café"] ),
                                      val_constraint( house, fr["vert"] ) ))
# ·  La maison verte est située immédiatement à gauche de la maison blanche.
    cnf_count += 2
    if writep:
        f.write( "-%d 0\n" %  val_constraint( 1, fr["blanc"] ) )
        f.write( "-%d 0\n" %  val_constraint( 5, fr["vert"] ) )
    for house in range(2,N+1):
        cnf_count += 1
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house-1, fr["vert"] ),
                                      val_constraint( house, fr["blanc"] ) ))
# ·  Le sculpteur possède un âne.
    for house in range(1,N+1):
        cnf_count += 2
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house, fr["sculpteur"] ),
                                      val_constraint( house, fr["âne"] ) ))
            f.write( "%d -%d 0\n" % ( val_constraint( house, fr["sculpteur"] ),
                                      val_constraint( house, fr["âne"] ) ))
# ·  Le diplomate habite la maison jaune.
    for house in range(1,N+1):
        cnf_count += 2
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house, fr["diplomate"] ),
                                      val_constraint( house, fr["jaune"] ) ))
            f.write( "%d -%d 0\n" % ( val_constraint( house, fr["diplomate"] ),
                                      val_constraint( house, fr["jaune"] ) ))
# ·  Le Norvégien habite la première maison à gauche.
    cnf_count += 1
    if writep:
        f.write( "%d 0\n" %  val_constraint( 1, fr["norvégien"] ) )
# ·  Le médecin habite la maison voisine de celle où demeure le propriétaire du renard.
    cnf_count += 2
    if writep:
        f.write( "-%d %d 0\n" % ( val_constraint( 1, fr["médecin"] ),
                                  val_constraint( 2, fr["renard"] ) ))
        f.write( "-%d %d 0\n" % ( val_constraint( 5, fr["médecin"] ),
                                  val_constraint( 4, fr["renard"] ) ))
    for house in range(2,N):
        cnf_count += 1
        if writep:
            f.write( "-%d %d %d 0\n" % ( val_constraint( house, fr["médecin"] ),
                                         val_constraint( house-1, fr["renard"]),
                                         val_constraint( house+1, fr["renard"] ) ))
# ·  La maison du diplomate est voisine de celle où il y a un cheval.
    cnf_count += 2
    if writep:
        f.write( "-%d %d 0\n" % ( val_constraint( 1, fr["diplomate"] ),
                                  val_constraint( 2, fr["cheval"] ) ))
        f.write( "-%d %d 0\n" % ( val_constraint( 5, fr["diplomate"] ),
                                  val_constraint( 4, fr["cheval"] ) ))
    for house in range(2,N):
        cnf_count += 1
	if writep:        
            f.write( "-%d %d %d 0\n" % ( val_constraint( house, fr["diplomate"] ),
                                         val_constraint( house-1, fr["cheval"] ),
                                         val_constraint( house+1, fr["cheval"] ) ))
# ·  On boit du lait dans la maison du milieu.
    cnf_count += 1
    if writep:
        f.write( "%d 0\n" %  val_constraint( 3, fr["lait"] ) )
# ·  Le Slovène boit du thé.
    for house in range(1,N+1):
        cnf_count += 2
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house, fr["slovène"] ),
                                      val_constraint( house, fr["thé"] ) ))
            f.write( "%d -%d 0\n" % ( val_constraint( house, fr["slovène"] ),
                                      val_constraint( house, fr["thé"] ) ))
# ·  Le violoniste boit du jus d'orange.
    for house in range(1,N+1):
        cnf_count += 2
	if writep:
            f.write( "-%d %d 0\n" % ( val_constraint( house, fr["violoniste"] ),
                                      val_constraint( house, fr["jus"] ) ))
            f.write( "%d -%d 0\n" % ( val_constraint( house, fr["violoniste"] ),
                                      val_constraint( house, fr["jus"] ) ))
# ·  Le Norvégien demeure à côté de la maison bleue
    cnf_count += 2
    if writep:
        f.write( "-%d %d 0\n" % ( val_constraint( 1, fr["norvégien"] ),
                                  val_constraint( 2, fr["bleu"] ) ))
        f.write( "-%d %d 0\n" % ( val_constraint( 5, fr["norvégien"] ),
                                  val_constraint( 4, fr["bleu"] ) ))
    for house in range(2,N):
        cnf_count += 1
        if writep:
            f.write( "-%d %d %d 0\n" % ( val_constraint( house, fr["norvégien"] ),
                                         val_constraint( house-1, fr["bleu"] ),
                                         val_constraint( house+1, fr["bleu"] ) ))
    return cnf_count

def reverse_fr( val ):
    for (k,v) in fr.iteritems():
        if val==v:
            return k.decode('latin1')
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sole some SAT problems.')
    parser.add_argument('--gen', dest='cnf_file', 
                        type=argparse.FileType('wt', 0),
                        help='Generate CNF file in DIMACS format.')
    parser.add_argument('--res', dest='res_file', 
                        type=argparse.FileType('r'),
                        help='Pretty print resulting MINISAT output file.')
    parser.add_argument('--neg', dest='neg_file', 
                        type=argparse.FileType('r'),
                        help='Negate result of MINISAT in file' )
    parser.add_argument('--add', dest='add_file', 
                        type=argparse.FileType('r'),
                        help='Add negated result to CNF file' )
    parser.add_argument('--into', dest='into_file', 
                        type=argparse.FileType('wt'),
                        help='Resulting CNF file' )
    args = parser.parse_args()

    if args.cnf_file:
        ncnf = dimacs_gen( args.cnf_file, False )
        args.cnf_file.write( "p cnf 125 %d\n" % ncnf )
        ignore = dimacs_gen( args.cnf_file, True )
        args.cnf_file.close()
    else: 
        if args.res_file:
            # Skip first line, which should be SAT 
            line = args.res_file.readline()
            line = args.res_file.readline()
            bool_vars = [ int(s) for s in line.split( ' ' ) ]
            for x in bool_vars:
                if x>0:
                    print x,
            print
            args.res_file.close()
            # Pretty print results
            objs = [ [] for i in range(N) ]
            for val in bool_vars:
                if val>0:
                    house = val%N
                    var   = val/N
                    if 0==house:
                        house = 5
                        var -= 1
                    objs[ house-1 ] += [ reverse_fr( var ) ]
            print "%s\t%10s  %10s  %10s  %10s  %10s" % ("Maison", 
                                                        "Couleur", 
                                                        "Pays",
                                                        "Boisson",
                                                        "Animal",
                                                        "Métier" )
            house = 0
            for x in objs: 
                house += 1
                print "%d\t%10s  %10s  %10s  %10s  %10s" % (house, x[0], x[1], x[2], x[3], x[4] )
        else:
            if args.neg_file and args.add_file and args.into_file:
                line = args.neg_file.readline()
                if line[0:3]=="SAT":
                    line = args.neg_file.readline()
                    bool_vars = [ int(s) for s in string.split( line, ' ' ) ]
                    out = ""
                    for var in bool_vars:
                        out += "%d " % (-var)
                    out += "\n"
                    # Process header
                    line = args.add_file.readline()
                    header = line[:len(line)-1].split(' ')
                    args.into_file.write( "%s %s %d %d\n" % ( header[0], header[1], int(header[2]), int(header[3])+1 ) )
                    args.into_file.write(out)
                    line = args.add_file.readline()
                    while ''!=line:
                        args.into_file.write(line)
                        line = args.add_file.readline()
                args.add_file.close()
                args.neg_file.close()
                args.into_file.close()



