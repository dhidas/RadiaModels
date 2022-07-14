# Run: srun -n 24 python IVU18_Model_MPI.py

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
# from mpi4py import MPI
# from mpi4py.MPI import ANY_SOURCE

# # Common MPI communication, rank, size
# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()
# size = comm.Get_size()

#Initialize MPI
rank = rad.UtiMPI('on')

show=False
if not show:
    import matplotlib
    matplotlib.use('Agg')


ivu18args.update({
    'nhalfperiods': 2, #15,
    'pole_chamfer_longedge': 0.5,
    'magnet_chamfer_gapside': 0.5,
})

if True:
    ivu18args.update({
        'pole_body_divisions': [1, 1, 1],
        'pole_tip_divisions': [1, 1, 1],
        'magnet_divisions': [1, 1, 1],
    })

PERIOD = ivu18args['period']
NHALFPERIODS = ivu18args['nhalfperiods']

undulator = ri.get_ivu(**ivu18args)

t0 = time.time()
IM = rad.RlxPre(undulator)
if(rank <= 0): print('Interaction Matrix was set up in:', round(time.time() - t0, 2), 's')

#Perform the Relaxation
t0 = time.time()
res = rad.RlxAuto(IM, 0.001, 5000)

if(rank <= 0): 
    print('Relaxation took:', round(time.time() - t0, 2), 's')
    print('Relaxation Results:', res)
    
   # Full undulator
    Z = np.linspace(-1.7*PERIOD*NHALFPERIODS/4, 1.7*PERIOD*NHALFPERIODS/4, 1001)
    B = [rad.Fld(undulator, 'b', [0, 0, z]) for z in Z]

    # Just part to take effective field from
    zstart = -PERIOD + PERIOD * NHALFPERIODS%4/4
    zstop = zstart + 2 * PERIOD

    # Show full field and where effective field is taken from
    plt.figure()
    plt.title(f'Undulator Magnetic Field')
    plt.xlabel('Z (mm)')
    plt.ylabel('Magnetic Field (T)')
    plt.plot(Z, [b[0] for b in B], label='Bx')
    plt.plot(Z, [b[1] for b in B], label='By')
    plt.plot(Z, [b[2] for b in B], label='Bz')
    mymax=[max([np.abs(b[i]) for b in B]) for i in range(3)]
    plt.axhline(+mymax[1], linestyle='--', color='tab:cyan', label=f'$\\pm$ {round(mymax[1], 2)}')
    plt.axhline(-mymax[1], linestyle='--', color='tab:cyan')
    plt.axvline(zstart, color='tab:purple', linestyle='-.', linewidth=1, label='$B_{eff}$ Region')
    plt.axvline(zstop, color='tab:purple', linestyle='-.', linewidth=1)
    plt.legend()
    plt.tight_layout()
    plt.savefig('fig1.png')

    Z2P = np.linspace(zstart, zstop, 5001)
    B2P = [rad.Fld(undulator, 'b', [0, 0, z]) for z in Z2P]
    ByEffMag = ru.get_beff(Z2P, [b[1] for b in B2P], 2)
    ByEff = [-ByEffMag*np.sin(2*np.pi/PERIOD * z + 2*np.pi*(NHALFPERIODS%4/4)) for z in Z2P]
    plt.figure()
    plt.title(f'Undulator Magnetic Field')
    plt.xlabel('Z (mm)')
    plt.ylabel('Magnetic Field (T)')
    plt.plot(Z2P, [b[0] for b in B2P], label='Bx')
    plt.plot(Z2P, [b[1] for b in B2P], label='By')
    plt.plot(Z2P, [b[2] for b in B2P], label='Bz')
    plt.plot(Z2P, ByEff, '--', label='$By_{eff}$ = ' + f'{round(ByEffMag, 2)}')
    plt.legend()
    plt.grid()
    plt.savefig('fig2.png')

    print('Keff', 0.09336*ByEffMag*PERIOD) 
    
    
    
rad.UtiMPI('off')
