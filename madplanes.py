# Mad Planes on 3x3 board -- 16 solutions including symmetries.
# Set contains twice the same card, so there are 2 primitive solutions.

import maddlx as dlx    # Knuth's Mad Dancing Links implementation
import collections
import cairo

global CELLS, BLOCKS, COLORS
global rowidentifiers, d
global ctx
global RECT, STEP, WIDTH, HEIGHT, ORIX, ORIY

RECT = 100
STEP = RECT/3
WIDTH, HEIGHT = 4*5*RECT, 4*5*RECT

# Cell number to its four edges numbers, N-E-S-W; 0 for outer edge, 1-12 for inner edges
CELLS = [ [0,1,7,0],  [0,4,8,1],  [0,0,9,4],
          [7,2,10,0], [8,5,11,2], [9,0,12,5],
          [10,3,0,0], [11,6,0,3], [12,0,0,6]
          ]
# The 9 blocks (or cards) in the puzzle, N-E-S-W orientation, [H]ead or [T]ail followed
# by head or tail color [y]ellow, [g]reen, [w]hite, [b]lue.
BLOCKS = [ "TyHgHwTg",
           "TyTgHbHw",
           "TyTwHgHb",
           "TyHgHwTb",
           "TyHbHgTw",
           "HyTbTwHb",
           "HyTgTwHb",
           "HyTbTwHg",
           "HyTgTwHb"
           ]
COLORS = dict([("y",[255,255,0]),
               ("g",[0,255,0]),
               ("w",[255,255,255]),
               ("b",[0,0,255])
               ])

def cell_to_row( cell, b ):
    # Cells are lists of 4 edge numbers, starting at 1, in N-E-S-W orientation; 0 means no edge
    r = []
    orientation = 0
    for edge in cell:
        if 0 != edge:
            if 'H'==b[orientation]: r += [2*edge-2]
            if 'T'==b[orientation]: r += [2*edge-1]
        orientation += 1
    return r
            

def block_to_rows( block, bidx ):
    # Block string is [H|T][y|g|w|b] 4 times clockwise
    # Head or Tail; Yellow, Green, White or Blue.
    # Each block goes in 9 cells, in four orientations.
    rows = []
    b = collections.deque( [block[0], block[2], block[4], block[6] ] )
    for orientation in range(4):
        b.rotate(1)
        for cell in CELLS:
            rows += [ cell_to_row( cell, b ) + [ bidx + 24 ] ]
    return rows

def samecolor( row, partialsolution ):
    global rowidentifiers, d
    # About to add row to solution, identify block
    (block, orientation, cell) = d.getrow( row, rowidentifiers )
#     print block, orientation, cell, partialsolution
#     print CELLS[cell]
    # Rotate this block's colors in place
    b = collections.deque( [ block[1], block[3], block[5], block[7] ] )
    b.rotate( orientation )
    # Check matching colors in partial solution
    for ridx in partialsolution:
        # Identify each block in partial solution
        (bsol, osol, csol) = d.getrow( ridx, rowidentifiers )
        # Search for common edge with the candidate block
        for i in CELLS[cell]:
            if 0!=i:
                if i in CELLS[csol]:
                    b0 = collections.deque( [ bsol[1], bsol[3], bsol[5], bsol[7] ] )
                    b0.rotate( osol )
                    if b[ CELLS[cell].index(i) ] != b0[ CELLS[csol].index(i) ]:
                        return False
    return True

# Displaying and painting solutions        

def display( solution ):
    bmap = [ "  " for i in range(81) ]
    places = [ [1, 11, 19, 9], [4, 14, 22, 12], [7, 17, 25, 15] ]
    for (block, orientation, cell) in solution:
        b = collections.deque( [ block[0:2], block[2:4], block[4:6], block[6:8] ] )
        b.rotate( orientation )
        p = places[ cell%3 ]
        p0 = 27*(cell/3)
        for i in range(4):
            bmap[ p0 + p[i] ] = b[i]
    # Print bitmap
    for i in range(9):
        s = ""
        for j in range(9):
            s += bmap[9*i+j]
        print s
    return bmap

def paint( bmap, bmap_id ):
    global ctx, ORIX, ORIY
    # Draw outline, background
    ctx.set_source_rgb (0.5, 0.5, 0.5) # Gray
    ctx.set_line_width (1)    
    for i in range(3):
        for j in range(3):
            ctx.rectangle( ORIX+RECT+j*RECT, ORIY+RECT+i*RECT, RECT, RECT )
    ctx.stroke()
    ctx.set_source_rgb (0.8, 0.8, 0.8) # Gray
    for i in range(3):
        for j in range(3):
            ctx.rectangle( ORIX+RECT+j*RECT+1, ORIY+RECT+i*RECT+1, RECT-2, RECT-2 )
    ctx.fill()
    # Draw configuration
    for i in range(9):
        for j in range(9):
            x, y = ORIX+RECT+i*STEP, ORIY+RECT+j*STEP
            if '  ' != bmap[9*i+j]:
                if 'T' == bmap[9*i+j][0]:
                    if 1 != (j%3):
                        ctx.rectangle( x+STEP/3, y, STEP/3, STEP )
                    else:
                        ctx.rectangle( x, y+STEP/3, STEP, STEP/3 )
                else:
                    if 0 == (j%3):
                        ctx.move_to( x, y )
                        ctx.line_to( x+STEP/2, y+STEP/2 )
                        ctx.line_to( x+STEP, y )
                    if 2 == (j%3):
                        ctx.move_to( x, y+STEP )
                        ctx.line_to( x+STEP/2, y+STEP/2 )
                        ctx.line_to( x+STEP, y+STEP )
                    if 1 == (j%3):
                        if 0 == (i%3):
                            ctx.move_to( x, y )
                            ctx.line_to( x+STEP/2, y+STEP/2 )
                            ctx.line_to( x, y+STEP )
                        else:
                            ctx.move_to( x+STEP, y )
                            ctx.line_to( x+STEP/2, y+STEP/2 )
                            ctx.line_to( x+STEP, y+STEP )
                r = COLORS[ bmap[9*i+j][1] ][0]
                g = COLORS[ bmap[9*i+j][1] ][1]
                b = COLORS[ bmap[9*i+j][1] ][2]
                ctx.set_source_rgb( r, g, b )
                ctx.fill()


# Testing code
if __name__ == '__main__':
    columns = [ 
        # Each edge has one head, one tail, to be matched, hence 24 primary columns
        ('H1', dlx.DLX.PRIMARY),
        ('T1', dlx.DLX.PRIMARY),
        ('H2', dlx.DLX.PRIMARY),
        ('T2', dlx.DLX.PRIMARY),
        ('H3', dlx.DLX.PRIMARY),
        ('T3', dlx.DLX.PRIMARY),
        ('H4', dlx.DLX.PRIMARY),
        ('T4', dlx.DLX.PRIMARY),
        ('H5', dlx.DLX.PRIMARY),
        ('T5', dlx.DLX.PRIMARY),
        ('H6', dlx.DLX.PRIMARY),
        ('T6', dlx.DLX.PRIMARY),
        ('H7', dlx.DLX.PRIMARY),
        ('T7', dlx.DLX.PRIMARY),
        ('H8', dlx.DLX.PRIMARY),
        ('T8', dlx.DLX.PRIMARY),
        ('H9', dlx.DLX.PRIMARY),
        ('T9', dlx.DLX.PRIMARY),
        ('H10', dlx.DLX.PRIMARY),
        ('T10', dlx.DLX.PRIMARY),
        ('H11', dlx.DLX.PRIMARY),
        ('T11', dlx.DLX.PRIMARY),
        ('H12', dlx.DLX.PRIMARY),
        ('T12', dlx.DLX.PRIMARY),
        # Blocks are used once, hence 9 primary columns
        ('B0', dlx.DLX.PRIMARY),
        ('B1', dlx.DLX.PRIMARY),
        ('B2', dlx.DLX.PRIMARY),
        ('B3', dlx.DLX.PRIMARY),
        ('B4', dlx.DLX.PRIMARY),
        ('B5', dlx.DLX.PRIMARY),
        ('B6', dlx.DLX.PRIMARY),
        ('B7', dlx.DLX.PRIMARY),
        ('B8', dlx.DLX.PRIMARY)
        ]
    d = dlx.DLX(columns)
    # Build rows
    rows = []
    bidx = 0
    for block in BLOCKS:
        rows += block_to_rows( block, bidx )
        bidx += 1
    print "%d rows total." % len(rows)
    # Keep backward link between rows and (block, orientation, cell) data in row names
    # and `rowidentifiers' globale.
    rownames = []
    for block in BLOCKS:
        for orientation in range(4):
            for cell in range(9):
                rownames += [ (block,  orientation+1, cell) ]
    rowidentifiers = d.appendRows(rows, rownames) 
#    print len(rows), "==", len(rownames), "rows"
#    print len(rowidentifiers), rowidentifiers
#    print len(d.Nrows),d.Nrows

    # Solve
    nsol = 0
    surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context (surface)
    for solution in d.solve( valueconstraint=samecolor ):
        ORIX, ORIY = (nsol%4)*RECT*4, (nsol/4)*RECT*4
        nsol += 1
        print "Statistics: %d" % nsol
        print d.statistics.nodes
        print d.statistics.updates
        print "Solution:   %d" %nsol
#        print solution
#        d.printSolution( solution )
#        print [ rownames[ridx] for ridx in d.partialsolution ]
#        print [ d.getrow(ridx, rowidentifiers) for ridx in solution ]
        paint( display( [ d.getrow(ridx, rowidentifiers) for ridx in solution ] ), nsol )
    surface.write_to_png ( "madsolutions.png" ) # Output to PNG
    print "%d solutions." % nsol
