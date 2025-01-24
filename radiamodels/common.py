def write_params_to_file (p, fn):
    """
    write parameters from a dict to a file for keeping track of things

    p - dict of parameters
    fn - filename

    returns nothing
    """

    with open(fn, 'w') as fo:
        fo.write('dict({\n')
        for k, v in p.items():
            k = "'" + k + "'"
            fo.write(f'    {k:35s}: {v},\n')
        fo.write('})\n')
    return


def write_field_to_file (z, b, fn):
    """
    write field to a file.  the field will be a function of z and have bx by bz (OSCARS 1D)

    z - list or array of z points
    b - list or array of [bx, by, bz] corresponding to the z points

    returns nothing
    """

    if len(z) != len(b):
        raise ValueError('length of z and b are not the same')

    with open(fn, 'w') as fo:
        for i in range(len(z)):
            fo.write(f'{z[i]:+.3e} {b[i][0]:+.3e} {b[i][1]:+.3e} {b[i][2]:+.3e}\n')
    return

