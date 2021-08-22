import numpy as np

def get_d(h1, h2, K, W, L):
    if W != 0:
        d = (L/2)-(K/W)*((h1**2-h2**2)/(2*L))
    else:
        d = h1
    return d

def get_h(h1, h2, K, W, L, x):
    a = (h1**2)-(((h1**2-h2**2)*x)/L)+((W/K)*(L-x)*x) + 0j
    #inds = np.where(np.isnan(a))
    #a[inds] = None
    #print(inds)
    h = np.real(np.sqrt(a))
    return h

def get_h_max(h1, h2, K, W, L):
    d = get_d(h1, h2, K, W, L)
    h = np.real(np.sqrt((h1**2)-(((h1**2-h2**2)*d)/L)+((W/K)*(L-d)*d)+0j))
    return h

def get_q(h1, h2, K, W, L, x):
    q = ((K*(h1**2-h2**2))/(2*L))-(W*((L/2)-x))
    return q