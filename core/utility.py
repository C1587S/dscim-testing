def ce(consumption, dim, eta):
    import numpy as np
    if eta == 1:
        return np.exp(np.log(consumption).mean(dim))
    else:
        return ((consumption ** (1 - eta)).mean(dim) * (1 - eta)) ** (1 / (1 - eta))