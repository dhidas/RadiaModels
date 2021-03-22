import radia as rad

import time
import matplotlib.pyplot as plt
import numpy as np




gap = 5
period = 20
nperiods = 10

magnet_size = [40, 20, 0.7*period/4]
pole_size = [magnet_size[0]/2, magnet_size[1]/2, period/2-2*magnet_size[2]]
print('magnet width', magnet_size[2], 'pole width', pole_size[2])

strength = [0, 1, 0]
#divisions = [2, [6, 1/6], 3]
divisions = [5, 5, 5]



magnet_color = [0, 0, 1]
pole_color = [0, 1, 0]

magnet_material = rad.MatLin([0.05, 0.15], [0, 0, 1.30])
pole_material = rad.MatStd('Xc06')




# Just as a test this will be an even number of half-periods
# We start by constricting module centered at 0, then clone this module and place it
# starting downstream, then reflect it for upstream and bottom
magnet_us = rad.ObjFullMag(
    [0, magnet_size[1]/2, -pole_size[2]/2-magnet_size[2]/2], # center,
    magnet_size,
    [0, 0, 1], # strength,
    [1, 1, 1], #divisions,
    0, #module do later
    magnet_material,
    magnet_color
)
rad.ObjDivMag(magnet_us, divisions)
magnet_ds = rad.ObjDpl(magnet_us)
rad.TrfOrnt(magnet_ds, rad.TrfPlSym([0, 0, 0], [0, 0, 1]))

pole = rad.ObjFullMag(
    [0, pole_size[1]/2, 0], # center,
    pole_size,
    [0, 0, 0], # strength,
    [1, 1, 1], #divisions,
    0, #module do later
    pole_material,
    pole_color
)
#rad.ObjDivMag(pole, divisions)


module = rad.ObjCnt([magnet_us, pole, magnet_ds])


girder_td = rad.ObjCnt([])
for i in range(nperiods):
    zpos = period/4 + i * period/2
    this_module = rad.ObjDpl(module)
    if i % 2:
        rad.TrfOrnt(this_module, rad.TrfInv())

    rad.TrfOrnt(this_module, rad.TrfTrsl([0, 0, zpos]))
    rad.ObjAddToCnt(girder_td, [this_module])


girder_tu = rad.ObjDpl(girder_td)
rad.TrfOrnt(girder_tu, rad.TrfPlSym([0, 0, 0], [0, 0, 1]))
rad.TrfOrnt(girder_tu, rad.TrfInv())


# undulator is the top girder, adjusted for gap, and reflected symmetry
undulator = rad.ObjCnt([girder_tu, girder_td])
rad.TrfOrnt(undulator, rad.TrfTrsl([0, +gap/2, 0]))
rad.TrfZerPara(undulator, [0,0,0], [0,1,0])

# Solve and print solved time
tstart = time.time()
rad.Solve(undulator, 0.0003, 1000)
print('solve time', round(time.time() - tstart, 3), '(s)')



# Plot the field along z
zstart = -1.3*period*nperiods/2
zstop = -zstart
Z = np.linspace(zstart, zstop, 501)
B = [rad.Fld(undulator, 'b', [0, 0, z]) for z in Z]

plt.figure()
plt.title('Untulator field along Z')
plt.xlabel('Z Position (mm)')
plt.ylabel('Field (T)')
plt.plot(Z, [b[0] for b in B], label='$B_x$')
plt.plot(Z, [b[1] for b in B], label='$B_y$')
plt.plot(Z, [b[2] for b in B], label='$B_z$')
plt.legend()
plt.savefig('hybrid_blocks.png')
plt.show()
