import radia as rad
import radiamodels.ivu as ri
import radiamodels.util as ru

import numpy as np
import matplotlib.pyplot as plt

show=False

PERIOD = 18
NHALFPERIODS = 11

undulator = ri.get_ivu(
    gap=4.63,
    period=PERIOD,
    nhalfperiods=NHALFPERIODS,
)

rad.Solve(undulator, 0.0003, 1000)



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
plt.savefig('ivu18_bfield.png')
if show: plt.show()

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
plt.savefig('ivu18_beff.png')
if show: plt.show()

print('Keff', 0.09336*ByEffMag*PERIOD)


# Look at first field integral
X = np.linspace(-10, 10, 21)
I1Y = [TMM2GCM*rad.FldInt(undulator, 'inf', 'iby', [x, 0, -10], [x, 0, 10]) for x in X]

plt.figure()
plt.title('Undulator first field Integrals')
plt.xlabel('Horizontal position (mm)')
plt.ylabel('Field Integral (Gcm)')
plt.plot(X, I1Y, label='I1Y')
# plt.ylim([-100, 100])
plt.axhline(+50, linestyle='--', color='tab:cyan', label=f'$\\pm$ 50 Gcm')
plt.axhline(-50, linestyle='--', color='tab:cyan')
plt.legend()
plt.show()

