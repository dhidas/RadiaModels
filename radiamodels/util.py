import radia as rad
import numpy as np
from pkg_resources import resource_stream

def get_beff (Z, By, nperiods=None, harmonics=False, debug=False):
    """
    Get the effective bfield based on the input field.  Input data must be correspond to 
    an integer number of periods.
    
    Z : list of z positions
    By: list of vertical field values corresponding to each z in Z
    nperiods: Number of periods present in the data given
    harmonics: if True return odd harmonics instead of beff
    debug: if True print debug info
    """
    n = len(By)
    freqs = np.fft.fftfreq(n)
    mask = freqs > 0

    fft_vals = np.fft.fft(By)
    fft_theo = 2 * np.abs(fft_vals/n)

    # If nperiods is not specified, just find the fundamental and scale
    if nperiods is None:
        nperiods = np.argmax(fft_theo[mask]) + 1
    if debug: print('nperiods:', nperiods)

    period = np.abs(Z[-1] - Z[0]) / nperiods
    if debug: print('get_beff period', period)

    beff = 0
    bharmonics = []
    for i in range(nperiods-1, len(fft_theo[mask])//2, 2*nperiods):
        h = (i // nperiods) * 2 + 1

        if debug and h < 15: print(i, h, fft_theo[mask][i])

        beff += (fft_theo[mask][i]/h)**2
        bharmonics.append(fft_theo[mask][i])

    if harmonics:
        return bharmonics
    return np.sqrt(beff)

def b2k_mm (b, period):
    """Convert magnetic field to K where period is in mm"""
    return 0.09336*b*period

def get_magnetic_material_permendur ():
    return get_magnetic_material(filename=resource_stream (__name__,'data/PermendurNEOMAX.txt'))

def get_magnetic_material (filename):
    '''
    Get magnetic material defined by bh curve in file
    '''
    # Setup permendur material for radia
    Permendur = np.loadtxt(filename)
    HP = [x[0] for x in Permendur]
    BP = [x[1] for x in Permendur]

    # H(Oe) vs B(G) to myu0*H(A/m) vs myu0*M(T)=B(T)-myu0*H(A/m)
    myu0 = 4e-7 * np.pi

    # conversion factor between oersted and A/m
    conversion = 1000 / 4 / np.pi

    radHP = [conversion * myu0 * x for x in HP]
    radMP = [1e-4 * x[1] - x[0] for x in zip(radHP, BP)]
    radHMP = [[x[0], x[1]] for x in zip(radHP, radMP)]
    return rad.MatSatIsoTab(radHMP)


