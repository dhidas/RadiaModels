# Run: srun python IVU18_Model.py

import radia as rad
import radiamodels.ivu as ri
import radiamodels.util as ru
from ivu18_defaults import ivu18args

import numpy as np
import matplotlib.pyplot as plt
import time
import pickle
import os.path


show=False
if not show:
    import matplotlib
    matplotlib.use('Agg')


ivu18args.update({
    'nhalfperiods': 15, #15,
    'pole_chamfer_longedge': 0.3,
    'pole_chamfer_shortedge': 5.0,
    'pole_body_divisions': [6, [12, 5], 7],
    'pole_tip_divisions': [7, [15, 6], 9],

    'magnet_chamfer_gapside': 0.3,
    'magnet_chamfer_outerside': 0.5,
    'magnet_chamfer_outerside': 0.5,
    'magnet_divisions': [4, 9, 11],
})

if False:
    ivu18args.update({
        'pole_body_divisions': [1, 1, 1],
        'pole_tip_divisions': [1, 1, 1],
        'magnet_divisions': [1, 1, 1],
    })

PERIOD = ivu18args['period']
NHALFPERIODS = ivu18args['nhalfperiods']

print(ivu18args)

undulator = ri.get_ivu(**ivu18args)
rad.Solve(undulator, 0.0003, 5000)

    
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
    
    
    
