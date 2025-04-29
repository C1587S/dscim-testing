import xarray as xr

def save_zarr(ds, path, consolidated=True):
    ds.to_zarr(path, mode="w", consolidated=consolidated)
