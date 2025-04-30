# dscim_refactor/core/aggregation.py
from pathlib import Path
import xarray as xr
import dask.array as da
import numpy as np
from dscim.utils.functions import ce_func, mean_func

def ce_from_chunk(
    chunk,
    filepath: Path,
    reduction: str,
    bottom_code: float,
    histclim: str,
    delta: str,
    recipe: str,
    eta: float,
    zero: bool,
    socioec: str,
    ce_batch_coords: dict,
):
    """
    Exactly the same logic as in the original `reduce_damages` map_blocks loop.
    """
    year = chunk.year.values
    ssp   = chunk.ssp.values
    model = chunk.model.values

    # load GDPpc for exactly this batch
    gdppc = (
        xr.open_zarr(socioec, chunks=None)
          .sel(year=year, ssp=ssp, model=model, region=ce_batch_coords["region"], drop=True)
          .gdppc
    )

    # build the “calculation” array
    if reduction == "no_cc":
        if zero:
            chunk[histclim] = xr.where(chunk[histclim] == 0, 0, 0)
        calculation = gdppc + chunk[histclim].mean("batch") - chunk[histclim]
    elif reduction == "cc":
        calculation = gdppc - chunk[delta]
    else:
        raise NotImplementedError(f"Unknown reduction: {reduction}")

    # apply recipe
    arr = np.maximum(calculation, bottom_code)
    if recipe == "adding_up":
        result = mean_func(arr, "batch")
    elif recipe == "risk_aversion":
        result = ce_func(arr, "batch", eta=eta)
    else:
        raise NotImplementedError(f"Unknown recipe: {recipe}")

    return result
