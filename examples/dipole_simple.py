import radia as rad


gap = 10
size = [30, 20, 500]
strength = [0, 1, 0]
divisions = [10, 10, 10]
material = rad.MatLin([0.05, 0.15], [0, 1.3, 0])
color = [0, 0, 1]

center_top = [0, +size[1]/2 + gap/2, 0]
center_bot = [0, -size[1]/2 - gap/2, 0]


magnet_top = rad.ObjFullMag(
    center_top,
    size,
    strength,
    divisions,
    0, #module do later
    material,
    color
)

magnet_bot = rad.ObjFullMag(
    center_bot,
    size,
    strength,
    divisions,
    0, #module do later
    material,
    color
)

space = 20
block_material = rad.MatStd('Xc06')
block_size = [40, size[1]*2+gap, size[2]]
block_center = [-size[0]/2-block_size[0]/2 - space, 0, 0]
block_color = [0, 1, 0]
block_strength = [0, 0, 0]
block_divisions = [10, 10, 10]

block_side = rad.ObjFullMag(
    block_center,
    block_size,
    block_strength,
    block_divisions,
    0, #module do later
    block_material,
    block_color
)

top_size = [size[0]+block_size[0]+space, 30, size[2]]
top_center = [(-block_size[0]-space)/2, size[1]+gap/2+top_size[1]/2, 0]
bot_center = [(-block_size[0]-space)/2, -size[1]-gap/2-top_size[1]/2, 0]

block_top = rad.ObjFullMag(
    top_center,
    top_size,
    block_strength,
    block_divisions,
    0, #module do later
    block_material,
    block_color
)

block_bot = rad.ObjFullMag(
    bot_center,
    top_size,
    block_strength,
    block_divisions,
    0, #module do later
    block_material,
    block_color
)

dipole = rad.ObjCnt([magnet_top, magnet_bot, block_side, block_top, block_bot])
# rad.Solve(dipole, 0.0003, 1000)
rad.Solve(dipole, 0.0003, 1000)

print('field at center', rad.Fld(dipole, 'b', [0, 0, 0]), '(T)')
