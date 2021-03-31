import radia as rad
import radiamodels.ivu as ri
import radiamodels.util as ru
from ivu18_defaults import ivu18args

import numpy as np
import matplotlib.pyplot as plt
import time
import pickle
import os.path

#Initialize MPI
rank = rad.UtiMPI('on')

show=True
if not show:
    import matplotlib
    matplotlib.use('Agg')


# Conversion factors
TMM2GCM = 1e3


variable = 'half_pole_size'
value = [38/2, 21.5, 2.8]



# Change default arguments here
ivu18args.update({
#    'gap': 5.00,
#    'pole_body_divisions' : [1, 1, 1],
#    'pole_tip_divisions' : [1, 1, 1],
#    'magnet_divisions' : [1, 1, 1],
    })
ivu18args.update({
    'half_pole_size': [20.0, 22.173913043478258, 2.9130434782608696],
    'pole_chamfer_shortedge': 6.5,
    'pole_chamfer_longedge': 0,
    'magnet_chamfer_gapside': 0,
    'quartermagnet_size_xy': [30, 35],
    'pole_offset_y': 0,
    })

undulator = ri.get_ivu(**ivu18args)

#Construct Interaction Matrix
t0 = time.time()
IM = rad.RlxPre(undulator)
if(rank <= 0): print('Interaction Matrix was set up in:', round(time.time() - t0, 2), 's')


#Perform the Relaxation
t0 = time.time()
res = rad.RlxAuto(IM, 0.001, 5000)

if(rank <= 0): 
    print('Relaxation took:', round(time.time() - t0, 2), 's')
    print('Relaxation Results:', res)

# get some basic ID info
PERIOD = ivu18args['period']
NHALFPERIODS = ivu18args['nhalfperiods']

# Just part to take effective field from
zstart = -PERIOD + PERIOD * NHALFPERIODS%4/4
zstop = zstart + 2 * PERIOD

# effective field from 0 and +/- 5mm
ZE = np.linspace(zstart, zstop, 5001)
BE0 = [rad.Fld(undulator, 'b', [0, 0, z]) for z in ZE]
BEP = [rad.Fld(undulator, 'b', [5, 0, z]) for z in ZE]

if rank == 0:
    ByEffMag0 = ru.get_beff(ZE, [b[1] for b in BE0], 2)
    ByEffMagP = ru.get_beff(ZE, [b[1] for b in BEP], 2)
    print(f'Beff 0: {ByEffMag0:.3f}  +: {ByEffMagP:.3f}')
    print(f'Keff 0: {ru.b2k_mm(ByEffMag0, PERIOD):.3f}  +: {ru.b2k_mm(ByEffMagP, PERIOD):.3f}')

rad.UtiMPI('off')
