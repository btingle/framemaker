import sys, os, math

# preferred, as we may need to modify this to make sure our edge to center ratio is respected while filling the frame
pref_block_width = os.getenv('PREF_BLOCK_WIDTH') or 50 # 5cm, why not
# this is the "preferred" ratio, as edges may need to be shaved off a bit to satisfy width/height requirements
pref_edge_to_center_ratio = os.getenv('PREF_EDGE_TO_CENTER') or 0.5 # why not

def rot90(coords):
    cn = []
    for x, y in coords:
        cn.append((-y, x))
    return cn
def translate(coords, x, y):
    cn = []
    for _x, _y in coords:
        cn.append((_x+x, _y+y))
    return cn
def scale(coords, sx, sy):
    cn = []
    for x, y in coords:
        cn.append((x*sx, y*sy))
    return cn
def mirrorY(coords):
    cn = []
    for x, y in coords:
        cn.append((x, -y))
    return cn

### pregenerate the coordinates for our pieces
# female component xy line definition
fp_xy = [
    (0, 0), (0.375, 0), (0.375-0.125, 0.125), (0.625+0.125, 0.125), (0.625, 0), (1, 0)
]
# female center piece
cfp_xy  = translate(fp_xy, 0, 0)
cfp_xy += translate(rot90(fp_xy), 1, 0)
cfp_xy += translate(rot90(rot90(fp_xy)), 1, 1)
cfp_xy += translate(rot90(rot90(rot90(fp_xy))), 0, 1)

# male component xy line definition
mp_xy = [
    (0, 0), (0.375, 0), (0.375-0.125, -0.125), (0.625+0.125, -0.125), (0.625, 0), (1, 0)
]
# male center piece
cmp_xy  = translate(mp_xy, 0, 0)
cmp_xy += translate(rot90(mp_xy), 1, 0)
cmp_xy += translate(rot90(rot90(mp_xy)), 1, 1)
cmp_xy += translate(rot90(rot90(rot90(mp_xy))), 0, 1)
# edge pieces
edge_xy = []
#efp_xy = mirrorY(translate(fp_xy, 0, 0) + translate(rot90(fp_xy), 1, 0) + translate(rot90(rot90(rot90(fp_xy))), 0, 1))
efp_xy = mirrorY(translate(rot90(fp_xy), 1, 0) + translate(rot90(rot90(rot90(fp_xy))), 0, 1))
#emp_xy = mirrorY(translate(mp_xy, 0, 0) + translate(rot90(mp_xy), 1, 0) + translate(rot90(rot90(rot90(mp_xy))), 0, 1))
emp_xy = mirrorY(translate(rot90(mp_xy), 1, 0) + translate(rot90(rot90(rot90(mp_xy))), 0, 1))
#emp_xy = translate(mp_xy, 0, 0) + translate(rot90(mp_xy), 1, 0) + translate(rot90(rot90(mp_xy)), 1, 1)
#edge_xy = [ # half box with male/female insert - normalized coordinates
#    (1, 1), (1, 0.675), (1-0.125, 0.675+0.125), (1-0.125, 0.375-0.125), (1, 0.375), (1, 0), (0, 0), (0, 1)
#]
#efp_xy  = translate(edge_xy, 0, 0) + translate(fp_xy, 0, 1)
#emp_xy  = translate(edge_xy, 0, 0) + translate(mp_xy, 0, 1)
insert_xy = [ # just a box!
    (1, 1), (1, 0), (0, 0), (0, 1), (1, 1)
]
# corner pieces
# can't wrap my head around scaling these property, just manually generate the pieces in the generate_pieces_geometry function
#cr_xy = [ # corner box - larger than other pieces
#    (1, 1), (2, 1), (2, -1), (0, -1)
#]
#crmp_xy = cr_xy + translate(mp_xy, 0, 0) + translate(rot90(mp_xy), 1, 0)
#crfp_xy = cr_xy + translate(fp_xy, 0, 0) + translate(rot90(fp_xy), 1, 0)

def determine_pieces_layout(width, height):
    # fit block width & ec ratio to width constraint, then scale block height appropriately
    num_center_pieces_x = (width - (2*pref_block_width*pref_edge_to_center_ratio)) // pref_block_width
    num_center_pieces_y = height // pref_block_width
    y_span = num_center_pieces_y * pref_block_width + (2*pref_block_width*pref_edge_to_center_ratio)
    y_scale = height / y_span
    return num_center_pieces_x, num_center_pieces_y, y_scale

# something to keep in mind (haven't accounted for it yet) but the laser cutter lines are approx 0.5mm across, meaning the pieces are sort of loose as of right now
def generate_pieces_geometry(yscale, thickness):
    # easiest part- center pieces
    male_center_xy = [scale(cmp_xy, pref_block_width, pref_block_width*yscale)]
    female_center_xy = [scale(cfp_xy, pref_block_width, pref_block_width*yscale)]
    # edge/corner pieces should be fattned by thickness*2- not affected by yscale (for the ridge inserts)
    top_edge_span = pref_block_width*pref_edge_to_center_ratio*yscale+thickness*2
    side_edge_span = pref_block_width*pref_edge_to_center_ratio+thickness*2

    tab_insert_xy = translate(scale(insert_xy, pref_block_width/2, thickness), pref_block_width/4, thickness) # adjust down a bit & center
    side_tab_insert_xy = translate(scale(insert_xy, pref_block_width*yscale/2, thickness), pref_block_width*yscale/4, thickness)

    top_edge_female_xy  = [translate(scale(efp_xy, pref_block_width, top_edge_span)+scale(fp_xy, pref_block_width, pref_block_width*yscale), 0, top_edge_span), tab_insert_xy]
    top_edge_male_xy    = [translate(scale(emp_xy, pref_block_width, top_edge_span)+scale(mp_xy, pref_block_width, pref_block_width*yscale), 0, top_edge_span), tab_insert_xy]
    side_edge_female_xy  = [rot90(translate(scale(efp_xy, pref_block_width*yscale, side_edge_span)+scale(fp_xy, pref_block_width*yscale, pref_block_width), 0, side_edge_span)), rot90(side_tab_insert_xy)]
    side_edge_male_xy    = [rot90(translate(scale(emp_xy, pref_block_width*yscale, side_edge_span)+scale(mp_xy, pref_block_width*yscale, pref_block_width), 0, side_edge_span)), rot90(side_tab_insert_xy)]
    #side_edge_female_xy = [rot90(scale(edge_xy, pref_block_width, side_edge_span) + translate(scale(fp_xy, pref_block_width, pref_block_width*yscale), 0, side_edge_span)), rot90(tab_insert_xy)]
    #side_edge_male_xy   = [rot90(scale(edge_xy, pref_block_width, side_edge_span) + translate(scale(mp_xy, pref_block_width, pref_block_width*yscale), 0, side_edge_span)), rot90(tab_insert_xy)]

    xspan = pref_block_width
    xsspan = pref_block_width*yscale
    yspan = top_edge_span
    ysspan = side_edge_span
    # i think male and female might be flipped here. dont care. this whole file is a mess anyways
    crf_xy               = translate(scale(mp_xy, ysspan, xspan), xspan, xspan*yscale) + [(xspan+ysspan, xspan*yscale), (xspan+ysspan, -yspan)] + translate(rot90(scale(mp_xy, yspan, xspan*yscale)), 0, -yspan)
    crm_xy               = translate(scale(fp_xy, ysspan, xspan), xspan, xspan*yscale) + [(xspan+ysspan, xspan*yscale), (xspan+ysspan, -yspan)] + translate(rot90(scale(fp_xy, yspan, xspan*yscale)), 0, -yspan)

    corner_female_xy    = [crf_xy + scale(fp_xy, pref_block_width, pref_block_width*yscale) + scale(translate(rot90(fp_xy), 1, 0), pref_block_width, pref_block_width*yscale), 
                            translate(tab_insert_xy, 0, -yspan), 
                            translate(rot90(side_tab_insert_xy), xspan+ysspan, 0)]
    #corner_male_xy      = [scale(cr_xy, top_edge_span, top_edge_span)]
    #corner_female_xy    = [scale(crfp_xy, pref_block_width, pref_block_width*yscale)]
    corner_male_xy      = [crm_xy + scale(mp_xy, pref_block_width, pref_block_width*yscale) + scale(translate(rot90(mp_xy), 1, 0), pref_block_width, pref_block_width*yscale),
                            translate(tab_insert_xy, 0, -yspan),
                            translate(rot90(side_tab_insert_xy), xspan+ysspan, 0)]

   

    cover_center = [(0, 0), (1, 0), (1, 1), (0, 1)]
    cover_center = [scale(cover_center, xspan, xspan*yscale)]

    cxspan = xsspan/2 + top_edge_span
    cover_side   = [(0, 0), (xspan, 0), (xspan, thickness), (xspan*0.75, thickness), (xspan*0.75, thickness*2), (xspan, thickness*2), (xspan, cxspan),
                    (0, cxspan), (0, thickness*2), (xspan*0.25, thickness*2), (xspan*0.25, thickness), (0, thickness)]
    cover_side   = [cover_side]

    xspan = ysspan
    cxspan = yspan
    cover_corner =  [(0, 0), (xspan, 0), (xspan, thickness), (xspan*0.75, thickness), (xspan*0.75, thickness*2), (xspan, thickness*2), (xspan, cxspan),
                    (0, cxspan), (0, thickness*2), (xspan*0.25, thickness*2), (xspan*0.25, thickness), (0, thickness)]
    cover_corner = [cover_corner]

    return [male_center_xy, female_center_xy, top_edge_female_xy, top_edge_male_xy, side_edge_female_xy, side_edge_male_xy, corner_female_xy, corner_male_xy, cover_center, cover_side, cover_corner]


def write_to_svg(outname, pieces_geometry):
    def make_svg_root_elem(width, height):
        root_elem = f"<svg width=\"{width}\" height=\"{height}\" xmlns=\"http://www.w3.org/2000/svg\">\n"
        return root_elem
    def make_svg_path_elem(coords, debug=False):
        ox, oy = coords[0]
        path_elem = f"<path d=\"M {ox} {oy}"
        for x, y in coords[1:]:
            path_elem += f" L {x} {y}"
        path_elem += " Z\" fill=\"transparent\" stroke=\"black\"/>\n"
        if debug:
            path_elem += f"<circle cx=\"{ox}\" cy=\"{oy}\" r=\"2\" fill=\"red\"/>\n"
            for x, y in coords[1:-1]:
                path_elem += f"<circle cx=\"{x}\" cy=\"{y}\" r=\"2\" fill=\"blue\"/>\n"
        return path_elem
    SVG_CANVAS_WIDTH = 1000
    SVG_CANVAS_HEIGHT = 1000
    svg = make_svg_root_elem(SVG_CANVAS_WIDTH, SVG_CANVAS_HEIGHT)
    offsetx = 100
    offsety = 100
    for geometry in pieces_geometry: # space them out on the canvas in whatever fashion
        for subgeom in geometry:
            svg += make_svg_path_elem(translate(subgeom, offsetx, offsety))
        offsetx += SVG_CANVAS_WIDTH//10
        if offsetx >= SVG_CANVAS_WIDTH:
            offsetx = 0
            offsety += SVG_CANVAS_HEIGHT//10
    svg += "</svg>"
    with open(outname, 'w') as svgfile:
        svgfile.write(svg)

def create_frame_pieces_svg(outname, thickness, width, height):

    numx, numy, yscale              = determine_pieces_layout(width, height)
    pieces_geometry                 = generate_pieces_geometry(yscale, thickness)

    # species of pieces:
    # 1. center male
    # 2. center female
    # 3. edge male top
    # 4. edge female top
    # 5. edge male side
    # 6. edge female side
    # 7. corner female
    # 8. corner male
    # 9. cover center
    # 10. cover edge
    # 11. cover corner
    # WIP
    # ridge side male
    # ridge side female
    # ridge corner male
    # ridge corner female (might need even more species to bond the corners?)
    print(f'numx={numx} numy={numy} yscale={yscale}')
    print(f'num center pieces:      male={math.ceil(numx*numy/2)}   female={math.floor(numx*numy/2)}')
    print(f'num side edge pieces:   male={(((numx-2)//2))*2}        female={(((numx-3)//2))*2}')
    print(f'num top edge pieces:    male={(((numy-2)//2))*2}        female={(((numy-3)//2))*2}')
    print(f'num corner pieces:      male={2 if (numx*numy)%2==0 else 0}    female={2 if (numx*numy)%2==0 else 4}')

    print(f'num cover pieces:       center={(numx-1)*(numy-1)}      edge={((numx-1)*2)+((numy-1)*2)}, corner=4')

    write_to_svg(outname, pieces_geometry)

if __name__ == "__main__":
    # units in mm
    outname     = sys.argv[1]
    thickness   = float(sys.argv[2])
    width       = float(sys.argv[3])
    height      = float(sys.argv[4])

    create_frame_pieces_svg(outname, thickness, width, height)