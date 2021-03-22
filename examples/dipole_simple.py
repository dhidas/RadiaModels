import radia as rad
import matplotlib.pyplot as plt
import numpy as np

# Parameters to change
gap = 10
space = 20
magnet_size = [30, 20, 100]
iron_top_height = 30
iron_side_width = 40
divisions = [5, 5, 5]

strength = [0, 0, 0]

# Magnet and iron properties
magnet_material = rad.MatLin([0.05, 0.15], [0, 1.3, 0])
magnet_color = [0, 0, 1]
iron_material = rad.MatStd('Xc06')
iron_color = [0, 1, 0]


magnet_center = [0, magnet_size[1] / 2 + gap / 2, 0]
iron_top_size = [magnet_size[0] + space, iron_top_height, magnet_size[2]]
iron_halfside_size = [iron_side_width, magnet_size[1] + gap / 2 + iron_top_size[1], magnet_size[2]]
iron_top_center = [+(magnet_size[0] - iron_top_size[0])/2, magnet_size[1] + gap/2 + iron_top_size[1]/2, 0]
iron_halfside_center = [-(magnet_size[0]/2 + space + iron_halfside_size[0]/2), iron_halfside_size[1]/2, 0]


dipole = rad.ObjCnt([])

magnet_top = rad.ObjFullMag(
    magnet_center,
    magnet_size,
    strength,
    divisions,
    dipole, #module do later
    magnet_material,
    magnet_color
)


iron_top = rad.ObjFullMag(
    iron_top_center,
    iron_top_size,
    strength,
    divisions,
    dipole, #module do later
    iron_material,
    iron_color
)

iron_halfside = rad.ObjFullMag(
    iron_halfside_center,
    iron_halfside_size,
    strength,
    divisions,
    dipole, #module do later
    iron_material,
    iron_color
)
rad.TrfZerPara(dipole, [0,0,0], [0,1,0])


rad.Solve(dipole, 0.0003, 1000)

print('field at center', rad.Fld(dipole, 'b', [0, 0, 0]), '(T)')


# Make some plots

zstart = -magnet_size[2]
zstop = -zstart
Z = np.linspace(zstart, zstop, 1501)
B1 = rad.FldLst(dipole, 'b', [0, 0, zstart], [0, 0, zstop], len(Z), 'noarg')

plt.figure()
plt.title('Dipole field along Z')
plt.xlabel('Z Position (mm)')
plt.ylabel('Field (T)')
plt.plot(Z, [b[0] for b in B1], label='$B_x$')
plt.plot(Z, [b[1] for b in B1], label='$B_y$')
plt.plot(Z, [b[2] for b in B1], label='$B_z$')
plt.legend()
plt.show()



xstart = 0
xstop = 2 * magnet_size[0]
X = np.linspace(xstart, xstop, 1501)
B2 = rad.FldLst(dipole, 'b', [xstart, 0, 0], [xstop, 0, 0], len(X), 'noarg')

plt.figure()
plt.title('Dipole field along X')
plt.xlabel('X Position (mm)')
plt.ylabel('Field (T)')
plt.plot(X, [b[0] for b in B2], label='$B_x$')
plt.plot(X, [b[1] for b in B2], label='$B_y$')
plt.plot(X, [b[2] for b in B2], label='$B_z$')
plt.legend()
plt.show()
