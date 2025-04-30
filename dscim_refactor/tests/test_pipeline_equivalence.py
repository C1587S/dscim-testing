from pathlib import Path
import xarray as xr
import numpy as np

from dscim_refactor.pipeline.pipeline import DscimPipeline
from dscim_refactor.pipeline.steps.load_sector import LoadSectorDataStep
from dscim_refactor.pipeline.steps.transform import ApplyReductionStep
from dscim_refactor.pipeline.steps.save import SaveReducedDataStep
from dscim_refactor.config.config_loader import ConfigLoader
from dscim.preprocessing.preprocessing import reduce_damages as original_reduce_damages
from dscim_refactor.utils.pathing import get_project_root

from itertools import product

# ------------------------
# Load config
# ------------------------

project_root = get_project_root()
config_path = project_root / "configs" / "dummy_config.yaml"
config = ConfigLoader(config_path, base_path=project_root)

# ------------------------
# Test parameters
# ------------------------

sector = "dummy_not_coastl_sector"
reduction = "cc"
recipe = "adding_up"
eta = None  # For risk_aversion, set this to 2.0
BOTTOM_CODING_GDPPC = 39.39265060424805

# ------------------------
# Run pipeline version
# ------------------------

output_dir = Path("refactor_dummy_data/test_comparison")
output_dir.mkdir(parents=True, exist_ok=True)

pipeline = DscimPipeline([
    LoadSectorDataStep(name="LoadSector", sector=sector, config=config),
    ApplyReductionStep(name="ApplyReduction", recipe=recipe, reduction=reduction, bottom_coding_gdppc=BOTTOM_CODING_GDPPC, eta=eta),
    SaveReducedDataStep(name="SaveReduced", sector=sector, config=config, recipe=recipe, reduction=reduction, eta=eta, base_output_path=output_dir)
])

pipeline.compute()

# Load new output
pipeline_path = output_dir / f"{sector}_{recipe}_{reduction}.zarr"
if eta is not None:
    pipeline_path = pipeline_path.with_name(f"{pipeline_path.stem}_eta{eta}.zarr")
ds_pipeline = xr.open_zarr(pipeline_path)

# ------------------------
# Run original reduce_damages version
# ------------------------

conf = config.raw_dict
ds_original = original_reduce_damages(
    sector=sector,
    config=str(config_path),
    recipe=recipe,
    reduction=reduction,
    eta=eta,
    zero=False,
    socioec=conf["econdata"]["global_ssp"]
)

# ------------------------
# Compare
# ------------------------

def compare_datasets(ds1, ds2, var="reduced", tol=1e-6):
    a = ds1[var].values
    b = ds2[var].values
    return np.allclose(a, b, rtol=tol, equal_nan=True)

is_equal = compare_datasets(ds_pipeline, ds_original)
print(f"Comparison result: {'MATCH' if is_equal else 'DIFFERENCE FOUND'}")
