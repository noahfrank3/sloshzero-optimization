def get_F_slosh(params):
    exec('from F_slosh import F_slosh')

    # Unpack parameters
    '''
    x_1 = params['x_1']
    x_2 = params['x_2']
    x_3 = params['x_3']
    d_pt = params['d_pt']
    s_d = params['s_d']
    '''

    # Calculate and return F_slosh
    F_slosh_val = F_slosh(params)
    # F_slosh_val = F_slosh(x_1, x_2, x_3, d_pt, s_d)
    return F_slosh_val
