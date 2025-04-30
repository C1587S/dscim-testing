# core/math_utils.py
"""
Standalone math utilities extracted from the original DSCIM impl (minor changes).
"""
import numpy as np


def power(a: np.ndarray, b: float) -> np.ndarray:
    """Power function that handles negative bases and fractional exponents safely."""
    return np.sign(a) * (np.abs(a) ** b)


def mean_func(consumption: np.ndarray, dims: tuple) -> np.ndarray:
    """Calculate arithmetic mean along specified axes."""
    return np.mean(consumption, axis=dims)


def ce_func(consumption: np.ndarray, eta: float) -> np.ndarray:
    """CRRA certainty equivalent (no dims argument)."""
    if eta == 1:
        return np.exp(np.log(consumption).mean(axis=0))
    u = np.power(consumption, 1 - eta) / (1 - eta)
    mu = u.mean(axis=0)
    return np.power(mu * (1 - eta), 1 / (1 - eta))



def c_equivalence(
    array: np.ndarray,
    dims: tuple,
    eta: float,
    weights: np.ndarray = None
) -> np.ndarray:
    """Generalized certainty equivalent with optional weights."""
    if np.any(array < 0):
        raise ValueError("Negative values passed to certainty equivalence.")
    if eta == 1:
        utility = np.log(array)
    else:
        utility = (array ** (1 - eta)) / (1 - eta)
    if weights is not None:
        # normalize weights and broadcast
        w = weights / np.sum(weights)
        mu = np.tensordot(utility, w, axes=(dims, (0,)))
    else:
        mu = np.mean(utility, axis=dims)
    if eta == 1:
        return np.exp(mu)
    return power(mu * (1 - eta), 1 / (1 - eta))