import radia as rad

import numpy as np


def get_ppmu (
    nhalfperiods=20,
    period=49,
    gap=40,
    elevation=0,
    taper=0,
    tilt=0,
    magnet_size_xy=[80, 40],
    magnet_divisions=[1, 1, 1],
    Br=1.25,
    debug=False
):
    # First magnet will be half length vertical, last will be half length vertical

    end_outer_length = 3 * period / 20
    end_inner_length = period / 8
    # total length including terminations
    length = nhalfperiods * period / 2 + 2 * end_outer_length
    
    magnet_size = [magnet_size_xy[0], magnet_size_xy[1], period/4]
    if debug: print('magnet_size:', magnet_size)

    taper_mm_per_mm = taper / length
    tilt_mm_per_mm = tilt / length

    nperiods = int(length / period)
    nhalfperiods = int(2 * length / period)
    if debug: print(f'nperiods {nperiods} nhalfperiods {nhalfperiods}')
    
    # Extra offset if half period exists
    extrahalf_offset = period / 4 if nhalfperiods % 2 else 0

    # Magnet material
    magnet_material = rad.MatStd('NdFeB', Br)

    magnet_strengths = [
        [0,  0, +1],
        [0, -1,  0],
        [0,  0, -1],
        [0, +1,  0],

    ]
    magnet_color = [0, 0, 1]

    girder_top = rad.ObjCnt([])
    nmagnets = nhalfperiods * 2 + 1
    for i in range(-2, nmagnets):
        this_magnet_strength = magnet_strengths[i % 4]
        this_magnet_center = [0, 0, -length / 2 + end_outer_length + end_inner_length + i * magnet_size[2] + magnet_size[2] / 2]
        this_magnet_size = magnet_size
        if i == -2:
            this_magnet_center = [0, 0, -length / 2 + end_outer_length / 2]
            this_magnet_size = magnet_size[0:2] + [end_outer_length]
        elif i == -1:
            this_magnet_center = [0, 0, -length / 2 + end_outer_length + end_inner_length / 2]
            this_magnet_size = magnet_size[0:2] + [magnet_size[2]/2]
        elif i == nmagnets - 2:
            this_magnet_center = [0, 0, length / 2 - end_outer_length - end_inner_length / 2]
            this_magnet_size = magnet_size[0:2] + [end_inner_length]
            # print('end inner:', this_magnet_center, this_magnet_size)
        elif i == nmagnets - 1:
            this_magnet_center = [0, 0, length / 2 - end_outer_length / 2]
            this_magnet_size = magnet_size[0:2] + [end_outer_length]
            # print('end outer:', this_magnet_center, this_magnet_size)

        # print('mag:', this_magnet_strength[1:], this_magnet_center[2], this_magnet_size[2])

        magnet = rad.ObjFullMag(
            this_magnet_center,
            this_magnet_size,
            this_magnet_strength,
            magnet_divisions,
            girder_top,
            magnet_material,
            magnet_color
        )

        
    girder_bot = rad.ObjDpl(girder_top)

    # Transform top
    rad.TrfOrnt(girder_top, rad.TrfTrsl([0, +magnet_size[1]/2, 0]))

    # Transform bot
    rad.TrfOrnt(girder_bot, rad.TrfRot([0, 0, 0], [0, 0, 1], np.pi))
    rad.TrfOrnt(girder_bot, rad.TrfInv())

    rad.TrfOrnt(girder_bot, rad.TrfTrsl([0, -magnet_size[1]/2, 0]))


    # Adjust for taper
    phi_taper = np.arcsin(taper_mm_per_mm/2)
    rad.TrfOrnt(girder_top, rad.TrfRot([0, 0, 0], [-1, 0, 0], phi_taper))
    rad.TrfOrnt(girder_bot, rad.TrfRot([0, 0, 0], [+1, 0, 0], phi_taper))

    # Adjust for gap
    rad.TrfOrnt(girder_top, rad.TrfTrsl([0, +gap/2, 0]))
    rad.TrfOrnt(girder_bot, rad.TrfTrsl([0, -gap/2, 0]))

    # Build undulator
    undulator = rad.ObjCnt([girder_top, girder_bot])

    # Adjust for tilt
    phi_tilt = np.arcsin(tilt_mm_per_mm)
    rad.TrfOrnt(undulator, rad.TrfRot([0, 0, 0], [1, 0, 0], phi_tilt))

    # Adjust for elevation
    rad.TrfOrnt(undulator, rad.TrfTrsl([0, 0, elevation]))

    return undulator


