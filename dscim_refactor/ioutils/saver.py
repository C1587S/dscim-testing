def save_zarr(ds, config, sector, recipe, reduction, eta=None, base_path=None):
    """
    Save the reduced Dataset to a Zarr store using either a custom base path
    or the path defined in config.
    """
    from pathlib import Path

    base = Path(base_path) if base_path else Path(config.paths["reduced_damages_library"])
    out_path = base / f"{sector}_{recipe}_{reduction}"
    if eta is not None:
        out_path = out_path.with_name(f"{out_path.stem}_eta{eta}")
    out_path = out_path.with_suffix(".zarr")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_zarr(str(out_path), mode="w", consolidated=True)
