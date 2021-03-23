import radia as rad
import radiamodels.ivu as ri
import radiamodels.util as ru

import numpy as np
import matplotlib.pyplot as plt
import time
import pickle
import os.path

# MPI imports
from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE

# Common MPI communication, rank, size
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

show=False
if not show:
    import matplotlib
    matplotlib.use('Agg')

GAP = 4.63
PERIOD = 18
NHALFPERIODS = 11

# Conversion factors
TMM2GCM = 1e3



#variable = 'half_pole_size'
#values = np.linspace(1, 5, size)
#value = [38/2, 21.5, values[rank]]

variable = 'pole_chamfer_shortedge'
values = np.linspace(0.5, 5, size)
value = values[rank]

pickle_name = 'ivu18_'+variable+'.p'
if os.path.exists(pickle_name):
    if rank == 0:
        print('ERROR: output file already exists')
    exit(0)

args = dict({
    'gap': GAP,
    'period': PERIOD,
    'nhalfperiods': NHALFPERIODS,

    'half_pole_size' : [38/2, 21.5, 2.8],
    'pole_body_divisions' : [4, [5, 1/5], 4],
    'pole_tip_divisions' : [5, [6, 1/6], 5],
    'magnet_divisions' : [5, 5, 5],

    'pole_chamfer_shortedge' : 2,
    'pole_chamfer_longedge' : 1,
    'pole_tip_height' : 5
    })
args[variable] = value

if False: # for fast testing only
    args.update({
        'pole_body_divisions' : [1, 1, 1],
        'pole_tip_divisions' : [1, 1, 1],
        'magnet_divisions' : [1, 1, 1],
        })

undulator = ri.get_ivu(**args)
rad.Solve(undulator, 0.0003, 1000)


# Just part to take effective field from
zstart = -PERIOD + PERIOD * NHALFPERIODS%4/4
zstop = zstart + 2 * PERIOD

Z2P = np.linspace(zstart, zstop, 5001)
B2P = [rad.Fld(undulator, 'b', [0, 0, z]) for z in Z2P]
ByEffMag = ru.get_beff(Z2P, [b[1] for b in B2P], 2)

value_vs_beff = [[values[rank], ByEffMag, args]]

if rank == 0:
    # Now wait and collect data from all other processes when it comes in
    for i in range(1, size):
        # Get incoming data
        data = comm.recv(source=ANY_SOURCE)
        value_vs_beff.append(data)

else:
    # Send results back to rank 0
    comm.send(value_vs_beff[0], dest=0)
    exit(0)


value_vs_beff.sort(key=lambda x: x[0])

data = [variable, value_vs_beff]
pickle.dump(data, open(pickle_name, 'wb'))


