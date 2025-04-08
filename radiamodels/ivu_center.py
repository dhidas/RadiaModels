import time
import numpy as np
import matplotlib.pyplot as plt

import radia as rad
import radiamodels.util as ru


default_params = {
    'gap': 5.0,
    'period': 20.0,
    'airgap': 0.050,
    'pole_size': [40, 22.5, 3.24],
    'magnet_size': [59, 28],
    'pole_tip_height': 4,
    'br': 1.3,
    'mag_color': [0, 0, 1],
    'pole_color': [1, 0, 0],
    'pole_tip_color': [1, 1, 0],
    'pole_center_divisions': [8, [15, 1], 4],
    'pole_side_divisions': [3, [9, 4], 3],
    'pole_center_tip_divisions': [8, [23, 6], 4],
    'debug': False,
}


def get_ivu_center (
    gap = 5.0,
    period = 20.0,
    airgap = 0.050,
    pole_size = [40, 22.5, 3.24],
    magnet_size = [59, 28],
    pole_tip_height = 4,
    br = 1.3,
    mag_color = [0, 0, 1],
    pole_color = [1, 0, 0],
    pole_tip_color = [1, 1, 0],
    pole_center_divisions = [8, [15, 1], 4],
    pole_side_divisions = [3, [9, 4], 3],
    pole_center_tip_divisions = [8, [23, 6], 4],
    debug=False,
):
    """
    Get an IVU model where the center magnest and poles have higher segmentation to estimate final Beff and Bn efficiently.
    """
    
    if len(magnet_size) > 2:
        raise ValueError(f'magnet size should not include the z-width: magnet_size={magnet_size}')
    
    pole_material = ru.get_magnetic_material_permendur()

    magnet_size = magnet_size[:] + [period/2 - pole_size[2] - 2*airgap]
    mag_material = rad.MatStd('NdFeB', br)
    if debug:
        print(f'magnet_size={magnet_size}')


    mag_center = rad.ObjRecMag(
        [magnet_size[0]/4, magnet_size[1]/2 + gap/2, magnet_size[2]/4],
        [magnet_size[0]/2, magnet_size[1], magnet_size[2]/2],
        [0, 0, 1],
    )
    mag_side = rad.ObjDpl(mag_center)

    rad.MatApl(mag_center, mag_material)
    rad.ObjDrwAtr(mag_center, mag_color)
    rad.ObjDivMag(mag_center, [[4, 1], [13, 3], [4, 1]])

    rad.MatApl(mag_side, mag_material)
    rad.ObjDrwAtr(mag_side, mag_color)
    rad.ObjDivMag(mag_side, [[2, 1], [2, 1], [2, 1]])


    pole_center = rad.ObjRecMag(
        [pole_size[0]/4, pole_size[1]/2 + gap/2, magnet_size[2]/2 + airgap + pole_size[2]/4],
        [pole_size[0]/2, pole_size[1], pole_size[2]/2],
    )
    pole_side = rad.ObjDpl(pole_center)
    rad.MatApl(pole_center, pole_material)
    rad.MatApl(pole_side, pole_material)

    if pole_tip_height > 0:
        pole_center_body, pole_center_tip = rad.ObjCutMag(
            pole_center,
            [0, gap/2 + pole_tip_height, 0],
            [0, -1, 0]
        )
        rad.ObjDivMag(pole_center_body, pole_center_divisions)
        rad.ObjDivMag(pole_center_tip, pole_center_tip_divisions)
        
        rad.ObjDrwAtr(pole_center_body, pole_color)
        rad.ObjDrwAtr(pole_center_tip, pole_tip_color)
        
        pole_center = rad.ObjCnt([pole_center_body, pole_center_tip])
    else:

        rad.ObjDrwAtr(pole_center, pole_color)
        rad.ObjDivMag(pole_center, pole_center_divisions)

    rad.ObjDrwAtr(pole_side, pole_color)
    rad.ObjDivMag(pole_side, pole_side_divisions)

    und_center = rad.ObjCnt([pole_center, mag_center])
    rad.TrfZerPerp(und_center, [0, 0, period/4], [0, 0, 1])
    und_center = rad.ObjDpl(und_center, 'FreeSym->True')

    rad.TrfZerPara(und_center, [0, 0, +period/2], [0, 0, 1])

    und_side = rad.ObjCnt([mag_side, pole_side])
    rad.TrfZerPerp(und_side, [0, 0, period/4], [0, 0, 1])
    und_side = rad.ObjDpl(und_side, 'FreeSym->True')

    rad.TrfOrnt(und_side, rad.TrfTrsl([0, 0, period]))
    rad.TrfZerPara(und_side, [0, 0, period*1.5], [0, 0, 1])
    rad.TrfZerPara(und_side, [0, 0, period*2], [0, 0, 1])
    rad.TrfZerPara(und_side, [0, 0, period*3], [0, 0, 1])
    # rad.TrfZerPara(und_side, [0, 0, period*5], [0, 0, 1])


    trfLong = rad.TrfCmbR(rad.TrfPlSym([0, 0, 0], [0, 0, 1]), rad.TrfInv())
    trfHor = rad.TrfPlSym([0, 0, 0], [1, 0, 0])

    und_center = rad.TrfMlt(und_center, trfLong, 2)
    und_center = rad.TrfMlt(und_center, trfHor, 2)

    und_side = rad.TrfMlt(und_side, trfLong, 2)
    und_side = rad.TrfMlt(und_side, trfHor, 2)
    und = rad.ObjCnt([und_center, und_side])

    rad.TrfZerPara(und, [0, 0, 0], [0, 1, 0])
    
    return und


def get_solve_beff (**params):
    """
    get a center ivu from params, solve it, and return the Beff, Bmax, and Bns.
    This is useful for doing some optimizations, eg pole widths, etc.

    Args:
        params: dict of params

    Returns:
        [Beff, Bmax, Bns]
    """
    debug = params['debug']
    period = params['period']

    und = get_ivu_center(**params)

    t0 = time.time()
    rad.Solve(und, 0.0001, 10000)
    if debug:
        print(f'{time.time() - t0:.2f} s')

    Z = np.linspace(-period/2, period/2, 501)
    B = [rad.Fld(und, 'b', [0, 0, z]) for z in Z]
    
    if debug:
        plt.figure()
        for i in range(3):
            plt.plot(Z, [b[i] for b in B])
        plt.show()

    bmax = max([abs(b[1]) for b in B])
    kmax = ru.b2k_mm(bmax, period)

    beff, bn = ru.get_beff_bn(Z, B, period=period)

    return [beff, bmax, bn]



