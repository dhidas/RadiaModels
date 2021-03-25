import radia as rad
import radiamodels.ivu as ri
import radiamodels.util as ru
from ivu18_defaults import ivu18args

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


# Conversion factors
TMM2GCM = 1e3

# default is just variable name unless name added/defined
name = None

# pole height
variable = 'half_pole_size'
name = variable + '_y'
values = np.linspace(15, 50, size)
value = [ivu18args[variable][0], values[rank], ivu18args[variable][2]]

#variable = 'pole_chamfer_shortedge'
#values = np.linspace(0.1, 9.4, size)
#value = values[rank]

#variable = 'pole_chamfer_longedge'
#values = np.linspace(0, 1.3, size)
#value = values[rank]

#variable = 'half_pole_size'
#values = np.linspace(10, 50, size)
#value = [38/2, values[rank], 2.8]

#variable = 'magnet_divisions'
#values = np.linspace(1, 6, size)
#value = [rank+1, rank+1, rank+1]

if name is None:
    name = variable
pickle_name = 'ivu18_'+name+'.p'
if os.path.exists(pickle_name):
    if rank == 0:
        print('ERROR: output file already exists:', pickle_name)
    exit(0)

# Update the parameter of interest
ivu18args[variable] = value

if False: # for fast testing only
    ivu18args.update({
        'pole_body_divisions' : [1, 1, 1],
        'pole_tip_divisions' : [1, 1, 1],
        'magnet_divisions' : [1, 1, 1],
        })

undulator = ri.get_ivu(**ivu18args)
rad.Solve(undulator, 0.0003, 1000)


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

ByEffMag0 = ru.get_beff(ZE, [b[1] for b in BE0], 2)
ByEffMagP = ru.get_beff(ZE, [b[1] for b in BEP], 2)
#print(f'Beff 0: {ByEffMag0:.3f}  +: {ByEffMagP:.3f}')
#print(f'Keff 0: {ru.b2k_mm(ByEffMag0, PERIOD):.3f}  +: {ru.b2k_mm(ByEffMagP, PERIOD):.3f}')

thisdata = dict({
    'value': values[rank],
    'ByEffMag0': ByEffMag0,
    'ByEffMagP': ByEffMagP,
    'ivu18args': ivu18args
    })


value_vs_beff = [thisdata]

if rank == 0:
    # Now wait and collect data from all other processes when it comes in
    for i in range(1, size):
        # Get incoming data
        data = comm.recv(source=ANY_SOURCE)
        value_vs_beff.append(data)

else:
    # Send results back to rank 0
    comm.send(thisdata, dest=0)
    exit(0)


value_vs_beff.sort(key=lambda x: x['value'])

data = [variable, value_vs_beff]
pickle.dump(data, open(pickle_name, 'wb'))


