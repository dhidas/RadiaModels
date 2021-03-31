import radia as rad
import radiamodels.util as ru

ivu18args = dict({
    'gap': 4.63,
    'taper': 0,
    'tilt': 0,
    'period': 18,
    'nhalfperiods': 8,

    'half_pole_size': [38/2, 21.5, 2.8],
    'pole_material': ru.get_magnetic_material_permendur(),
    'pole_body_divisions': [6, [5, 5], 4],
    'pole_tip_divisions': [5, [5, 6], 5],
    'pole_chamfer_shortedge': 3,
    'pole_chamfer_longedge': 0.05,
    'pole_tip_height': 5,
    'pole_offset_y': 0,

    'quartermagnet_size_xy': [58/2, 30],
    'magnet_material': rad.MatLin([0.05, 0.15], [0, 0, 1.30]),
    'magnet_divisions': [5, 5, 5],
    'magnet_chamfer_corner': 1,
    'magnet_chamfer_outerside': 0,
    'magnet_chamfer_gapside': 0,
    'magnet_chamfer_farside': 0,
    'magnet_offset_y': 0,
    'air_gap': 0.05,

    'end1_pole_height': 15,
    'end1_magnet_height': 20,
    'end2_pole_height': 6,
    'end2_magnet_height': 9,

    'girder_top_roll_rad': 0,
    'girder_bot_roll_rad': 0,
    'returnobject': 0,

    'debug': False,


    })
