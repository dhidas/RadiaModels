import radia as rad
import radiamodels.util as ru
import numpy as np

from radiamodels.common import *

def get_quartermagnet (
    size,
    material,
    divisions=[1, 1, 1],
    chamfer_corner=0,
    chamfer_outerside=0,
    chamfer_gapside=0,
    chamfer_farside=0,
    center_z=0,
    offset_y=0,
    color=[0, 0, 1],
    module=0,
    strength=[0, 0, 1],
):
    # This gives a magnet in the +x, +y quadrent meant to be a quarter magnet
    
    center = [size[0]/2, size[1]/2, center_z]

    magnet = rad.ObjFullMag(
        center,
        size,
        strength,
        divisions,
        module, #module do later
        material,
        color
    )
    rad.MatApl(magnet, material) # Do I need this?

    # corner chamfers
    magnet = rad.ObjCutMag(magnet,  [size[0]-chamfer_corner, 0, 0], [1, -1, 0])[0]
    magnet = rad.ObjCutMag(magnet,  [size[0]-chamfer_corner, size[1], 0], [1, +1, 0])[0]

    # long edge camfers: outerside, gapside, farside
    # outerside
    magnet = rad.ObjCutMag(magnet,  [size[0]-chamfer_outerside, 0, center_z+size[2]/2], [1, 0, +1])[0]
    magnet = rad.ObjCutMag(magnet,  [size[0]-chamfer_outerside, 0, center_z-size[2]/2], [1, 0, -1])[0]
    # gapside
    magnet = rad.ObjCutMag(magnet,  [0, 0, center_z + size[2]/2 - chamfer_gapside], [0, -1, +1])[0]
    magnet = rad.ObjCutMag(magnet,  [0, 0, center_z - size[2]/2 + chamfer_gapside], [0, -1, -1])[0]
    # farside
    magnet = rad.ObjCutMag(magnet,  [0, size[1], center_z + size[2]/2 - chamfer_farside], [0, +1, +1])[0]
    magnet = rad.ObjCutMag(magnet,  [0, size[1], center_z - size[2]/2 + chamfer_farside], [0, +1, -1])[0]

    # Shift magnet for offset_y
    rad.TrfOrnt(magnet, rad.TrfTrsl([0, offset_y, 0]))

    rad.ObjDrwAtr(magnet, color) # I DO need to do this

    return magnet

def get_halfpole (
    size,
    material,
    body_divisions=[1, 1, 1],
    tip_divisions=[1, 1, 1],
    chamfer_shortedge=0,
    chamfer_longedge=0,
    tip_height=1,
    center_z=0,
    offset_y=0,
    pole_color=[1, 0, 0],
    tip_color=[0, 1, 0],
    module = 0,
    strength=[0, 1, 0],
):
    # This gives a pole in the +x, +y quadrant with a chamfer on the +x end at 45-deg

    # Calculate center based on input center_z and pole size
    center = [size[0]/2, size[1]/2, center_z]
    divisions = [1, 1, 1]
    pole = rad.ObjFullMag(
        center,
        size,
        strength,
        divisions,
        0, #module do later
        material,
        pole_color
    )
    rad.MatApl(pole, material) # Do I need this?

    # short (top) and long edge (bottom 2) chamfer
    pole = rad.ObjCutMag(pole,  [size[0]-chamfer_shortedge, 0, 0], [1, -1, 0])[0]
    pole = rad.ObjCutMag(pole,  [0, 0, center_z + size[2]/2 - chamfer_longedge], [0, -1, +1])[0]
    pole = rad.ObjCutMag(pole,  [0, 0, center_z - size[2]/2 + chamfer_longedge], [0, -1, -1])[0]
    rad.ObjDrwAtr(pole, pole_color) # I DO need to do this

    # If there is a pole tip height defined use it, otherwise just one block
    if tip_height > 0:
        # Cut pole with a plane in +y.  negative side is the tip
        pole_body, pole_tip  = rad.ObjCutMag(pole,  [0, tip_height, 0], [0, -1, 0])

        # Body and tip divisions
        rad.ObjDivMag(pole_body, body_divisions)
        rad.ObjDivMag(pole_tip, tip_divisions)

        # Color#
        rad.ObjDrwAtr(pole_body, pole_color) # I DO need to do this
        rad.ObjDrwAtr(pole_tip,  tip_color) # I DO need to do this

        # Shift for offset_y
        rad.TrfOrnt(pole_body, rad.TrfTrsl([0, offset_y, 0]))
        rad.TrfOrnt(pole_tip,  rad.TrfTrsl([0, offset_y, 0]))

        if module != 0:
            rad.ObjAddToCnt(module, [pole_body, pole_tip])
        return rad.ObjCnt([pole_body, pole_tip])

    # Shift for offset_y
    rad.TrfOrnt(pole, rad.TrfTrsl([0, offset_y, 0]))

    if module != 0:
        rad.ObjAddToCnt(module, [pole])

    return rad.ObjCnt([pole])




def get_ivu (
    gap = 5,
    taper = 0,
    tilt = 0,
    period = 18,
    nhalfperiods = 2,
    
    half_pole_size = [38/2, 21.5, 2.8],
    pole_material = ru.get_magnetic_material_permendur(),
    pole_body_divisions = [3, 3, 3],
    pole_tip_divisions = [5, [5, 6], 5],
    pole_chamfer_shortedge = 2,
    pole_chamfer_longedge = 1,
    pole_tip_height = 2,
    pole_offset_y = 0,
    
    quartermagnet_size_xy = [58/2, 30],
    magnet_material = rad.MatLin([0.05, 0.15], [0, 0, 1.30]),
    magnet_divisions = [3, 3, 3],
    magnet_chamfer_corner = 1,
    magnet_chamfer_outerside = 0,
    magnet_chamfer_gapside = 0,
    magnet_chamfer_farside = 0,
    magnet_offset_y = 0,
    air_gap = 0.05,
    magnet_angle = 0,

    end1_pole_height = 15,
    end1_magnet_height = 20,
    end2_pole_height = 6,
    end2_magnet_height = 9,

    girder_top_roll_rad = 0,
    girder_bot_roll_rad = 0,
    returnobject = 0,

    debug = False,
):
    # build the IVU

    length = period * nhalfperiods/2
    
    # air_gap is taken out of the magnet
    quartermagnet_size = [quartermagnet_size_xy[0], quartermagnet_size_xy[1], (period/2 - 2*air_gap - half_pole_size[2])/2]
    if debug: print('quartermagnet_size', quartermagnet_size)
    
    # First build the basic module consisting of 1 half-pole and 2 quarter-magnets
    halfpole = get_halfpole(
        size=half_pole_size,
        material=pole_material,
        body_divisions=pole_body_divisions,
        tip_divisions=pole_tip_divisions,
        chamfer_shortedge=pole_chamfer_shortedge,
        chamfer_longedge=pole_chamfer_longedge,
        tip_height=pole_tip_height,
        offset_y=pole_offset_y,
    )
    quartermagnet_plusz = get_quartermagnet(
        size=quartermagnet_size,
        material=magnet_material,
        divisions=magnet_divisions,
        chamfer_corner=magnet_chamfer_corner,
        chamfer_outerside=magnet_chamfer_outerside,
        chamfer_gapside=magnet_chamfer_gapside,
        chamfer_farside=magnet_chamfer_farside,
        center_z=half_pole_size[2]/2 + quartermagnet_size[2]/2 + air_gap,
        offset_y=magnet_offset_y,
        strength=[0, np.sin(magnet_angle), np.cos(magnet_angle)],
    )
    quartermagnet_minusz = rad.ObjDpl(quartermagnet_plusz)
    rad.TrfOrnt(quartermagnet_minusz, rad.TrfPlSym([0, 0, 0], [0, 0, 1]))
    if debug: print('calc half period', half_pole_size[2] + quartermagnet_size[2]*2 + air_gap*2)

    # The basic module building block
    module = rad.ObjCnt([quartermagnet_minusz, halfpole, quartermagnet_plusz])
    if returnobject == 1:
        return module
    
    # Placement of first module depends on nhalfperiods being even or odd
    z_first_module = period/2 if nhalfperiods % 2 else period/4
    if debug: print('z_first_module', z_first_module)
   
    # Top outer downstream section
    girder_tod = rad.ObjCnt([])
    for i in range(nhalfperiods//2):
        z_piece = z_first_module + i * period/2
        piece = rad.ObjDpl(module)
        rad.TrfOrnt(piece, rad.TrfTrsl([0, 0, z_piece]))
        # Adjust for alternating field
        if i % 2 == 0:
            rad.TrfOrnt(piece, rad.TrfInv()) 
        rad.ObjAddToCnt(girder_tod, [piece])

    if returnobject == 2:
        return girder_tod
    
    
    # Add closest (#1) end section
    end1_half_pole_size = [half_pole_size[0], end1_pole_height, half_pole_size[2]]
    end1_halfpole = get_halfpole(
        size=end1_half_pole_size,
        material=pole_material,
        body_divisions=pole_body_divisions,
        tip_divisions=pole_tip_divisions,
        chamfer_shortedge=pole_chamfer_shortedge,
        chamfer_longedge=pole_chamfer_longedge,
        tip_height=pole_tip_height,
        offset_y=pole_offset_y,
    )
    end1_quartermagnet_size = [quartermagnet_size[0], end1_magnet_height, quartermagnet_size[2]]
    end1_quartermagnet_plusz = get_quartermagnet(
        size=end1_quartermagnet_size,
        material=magnet_material,
        divisions=magnet_divisions,
        chamfer_corner=magnet_chamfer_corner,
        chamfer_outerside=magnet_chamfer_outerside,
        chamfer_gapside=magnet_chamfer_gapside,
        chamfer_farside=magnet_chamfer_farside,
        center_z=half_pole_size[2]/2 + quartermagnet_size[2]/2 + air_gap,
        offset_y=magnet_offset_y,
        strength=[0, np.sin(magnet_angle), np.cos(magnet_angle)],
    )   
    end1_quartermagnet_minusz = rad.ObjDpl(end1_quartermagnet_plusz)
    rad.TrfOrnt(end1_quartermagnet_minusz, rad.TrfPlSym([0, 0, 0], [0, 0, 1]))
    end1_module = rad.ObjCnt([end1_quartermagnet_minusz, end1_halfpole, end1_quartermagnet_plusz])
    rad.TrfOrnt(end1_module, rad.TrfTrsl([0, 0, z_first_module + ((nhalfperiods)//2 + 0) * period/2]))
    if nhalfperiods//2 % 2 == 0:
        rad.TrfOrnt(end1_module, rad.TrfInv())
    rad.ObjAddToCnt(girder_tod, [end1_module])

    if returnobject == 3:
        return girder_tod

    # Add #2 end section
    end2_half_pole_size = [half_pole_size[0], end2_pole_height, half_pole_size[2]]
    end2_halfpole = get_halfpole(
        size=end2_half_pole_size,
        material=pole_material,
        body_divisions=pole_body_divisions,
        tip_divisions=pole_tip_divisions,
        chamfer_shortedge=pole_chamfer_shortedge,
        chamfer_longedge=pole_chamfer_longedge,
        tip_height=pole_tip_height,
        offset_y=pole_offset_y,
    )
    end2_quartermagnet_size = [quartermagnet_size[0], end2_magnet_height, quartermagnet_size[2]]
    end2_quartermagnet_plusz = get_quartermagnet(
        size=end2_quartermagnet_size,
        material=magnet_material,
        divisions=magnet_divisions,
        chamfer_corner=magnet_chamfer_corner,
        chamfer_outerside=magnet_chamfer_outerside,
        chamfer_gapside=magnet_chamfer_gapside,
        chamfer_farside=magnet_chamfer_farside,
        center_z=half_pole_size[2]/2 + quartermagnet_size[2]/2 + air_gap,
        offset_y=magnet_offset_y,
        strength=[0, np.sin(magnet_angle), np.cos(magnet_angle)],
    )   
    end2_quartermagnet_minusz = rad.ObjDpl(end2_quartermagnet_plusz)
    rad.TrfOrnt(end2_quartermagnet_minusz, rad.TrfPlSym([0, 0, 0], [0, 0, 1]))
    end2_module = rad.ObjCnt([end2_quartermagnet_minusz, end2_halfpole, end2_quartermagnet_plusz])
    rad.TrfOrnt(end2_module, rad.TrfTrsl([0, 0, z_first_module + ((nhalfperiods)//2 + 1) * period/2]))
    if nhalfperiods//2 % 2 == 1:
        rad.TrfOrnt(end2_module, rad.TrfInv())
    rad.ObjAddToCnt(girder_tod, [end2_module])

    if returnobject == 4:
        return girder_tod  

    # clone for top outer upsteam portion
    girder_tou = rad.ObjDpl(girder_tod)
    rad.TrfOrnt(girder_tou, rad.TrfPlSym([0, 0, 0], [0, 0, 1]))
    if nhalfperiods % 2 == 0:
        rad.TrfOrnt(girder_tou, rad.TrfInv())
    girder_to = rad.ObjCnt([girder_tod, girder_tou])
    if nhalfperiods % 2:
        rad.ObjAddToCnt(girder_to, [module])

    if returnobject == 5:
        return girder_to

    # clone and reflect for top inner
    girder_ti = rad.ObjDpl(girder_to)
    rad.TrfOrnt(girder_ti, rad.TrfPlSym([0, 0, 0], [1, 0, 0]))

    # Top girder
    girder_top = rad.ObjCnt([girder_to, girder_ti])
    if returnobject == 6:
        return girder_top


    # Best is if this is symmetric
    if girder_top_roll_rad == -girder_bot_roll_rad and tilt == 0:
        if debug: print('fast symmetric')

        # Roll for top and bottom girder
        if girder_top_roll_rad != 0:
            rad.TrfOrnt(girder_top, rad.TrfRot([0, 0, 0], [0, 0, 1], girder_top_roll_rad))

        # Taper
        if taper != 0:
            taper_mm_per_mm = taper / length
            phi_taper = np.arcsin(taper_mm_per_mm/2)
            rad.TrfOrnt(girder_top, rad.TrfRot([0, 0, 0], [-1, 0, 0], phi_taper))

        # Do the gap shift and mirror symmetry
        rad.TrfOrnt(girder_top, rad.TrfTrsl([0, +gap/2, 0]))
        rad.TrfZerPara(girder_top, [0,0,0], [0,1,0])
        return girder_top


    # CAREFUL: below here will take longer
    if debug: print('Nonsymmetric and will take longer to compute')


   
    # Bottom girder
    girder_bot = rad.ObjDpl(girder_top)
    rad.TrfOrnt(girder_bot, rad.TrfPlSym([0, 0, 0], [0, 1, 0]))
    rad.TrfOrnt(girder_bot, rad.TrfInv())

    # Top and Bottom girder roll
    if girder_top_roll_rad != 0:
        rad.TrfOrnt(girder_top, rad.TrfRot([0, 0, 0], [0, 0, 1], girder_top_roll_rad))
    if girder_bot_roll_rad != 0:
        rad.TrfOrnt(girder_bot, rad.TrfRot([0, 0, 0], [0, 0, 1], girder_bot_roll_rad))


    # for taper
    if taper != 0:
        taper_mm_per_mm = taper / length
        phi_taper = np.arcsin(taper_mm_per_mm/2)
        rad.TrfOrnt(girder_top, rad.TrfRot([0, 0, 0], [-1, 0, 0], phi_taper))
        rad.TrfOrnt(girder_bot, rad.TrfRot([0, 0, 0], [+1, 0, 0], phi_taper))



    # Adjust for gap
    rad.TrfOrnt(girder_top, rad.TrfTrsl([0, +gap/2, 0]))
    rad.TrfOrnt(girder_bot, rad.TrfTrsl([0, -gap/2, 0]))
        
    # Construct undulator
    undulator = rad.ObjCnt([girder_top, girder_bot])

    # Adjust for tilt
    if tilt is not None:
        tilt_mm_per_mm = tilt / length
        phi_tilt = np.arcsin(tilt_mm_per_mm)
        rad.TrfOrnt(undulator, rad.TrfRot([0, 0, 0], [1, 0, 0], phi_tilt))

    return undulator
