import xarray as xr

def load_zarr(path):
    return xr.open_zarr(path, consolidated=True)