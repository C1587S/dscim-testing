# dscim/core/aggregation.py

def reduce_damages(damages, socioec, recipe, reduction, bottom_coding_gdppc, eta=None, zero=False):
    """
    Simplified dummy version of damage reduction.
    This should mimic the logic from the original dscim.preprocessing.reduce_damages.
    """
    import xarray as xr

    # Apply a dummy reduction logic for the dummy test
    reduced = damages.mean(dim="batch")  # Example: aggregate over Monte Carlo draws

    # Fake logic for eta just to simulate
    if eta is not None:
        reduced = reduced * (1 - 0.01 * eta)

    # Copy attributes if needed
    reduced.attrs["recipe"] = recipe
    reduced.attrs["reduction"] = reduction
    reduced.attrs["eta"] = eta

    # Only assign name if it's a DataArray
    if isinstance(reduced, xr.DataArray):
        reduced.name = "reduced"

    return reduced
