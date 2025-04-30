import pytest
import yaml
import xarray as xr
import shutil
import warnings

from pathlib import Path
from tempfile import TemporaryDirectory

from dscim.preprocessing.preprocessing import reduce_damages
from dscim_refactor.pipeline.pipeline import DscimPipeline
from dscim_refactor.pipeline.steps.load_sector import LoadSectorDataStep
from dscim_refactor.pipeline.steps.transform import ApplyReductionStep
from dscim_refactor.pipeline.steps.save import SaveReducedDataStep
from dscim_refactor.config.config_loader import ConfigLoader

# Silence Zarr warnings
warnings.filterwarnings("ignore", category=UserWarning, module="zarr")

CONFIG_FILE   = Path("configs") / "dummy_config.yaml"
BOTTOM_CODING = 39.39265060424805

SECTORS    = ["dummy_not_coastl_sector"]
REDUCTIONS = ["cc", "no_cc"]
RECIPES    = ["adding_up", "risk_aversion"]

@pytest.mark.parametrize("sector", SECTORS)
@pytest.mark.parametrize("reduction", REDUCTIONS)
@pytest.mark.parametrize("recipe", RECIPES)
def test_output_equivalence(sector, reduction, recipe):
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Load and patch config
        conf = yaml.safe_load(CONFIG_FILE.read_text())

        # Copy sector data
        sector_src = Path(conf["sectors"][sector]["sector_path"])
        sector_dst = tmp_path / sector_src
        sector_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(sector_src, sector_dst)

        # Copy socioeconomic data
        socio_src = Path(conf["econdata"]["global_ssp"])
        socio_dst = tmp_path / socio_src
        socio_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(socio_src, socio_dst)

        # Point config at temporary locations
        conf["paths"]["reduced_damages_library"] = str(tmp_path / "legacy")
        conf["paths"]["sectoral_damage_zarr"]    = str(tmp_path / "dummy_data" / "sectoral")
        conf["econdata"]["global_ssp"]           = str(socio_dst)
        conf["sectors"][sector]["sector_path"]   = str(sector_dst)

        tmp_cfg = tmp_path / "config.yaml"
        tmp_cfg.write_text(yaml.safe_dump(conf))

        # Run legacy implementation
        eta = 2.0 if recipe == "risk_aversion" else None
        reduce_damages(
            sector=sector,
            config=str(tmp_cfg),
            recipe=recipe,
            reduction=reduction,
            eta=eta,
            zero=False,
            socioec=str(socio_dst),
        )

        # Load legacy output with fallback for filename format
        legacy_dir = tmp_path / "legacy" / sector
        if recipe == "risk_aversion":
            # Try both integer and float suffixes
            int_name   = f"{recipe}_{reduction}_eta{int(eta)}.zarr"
            float_name = f"{recipe}_{reduction}_eta{eta}.zarr"
            for name in (int_name, float_name):
                candidate = legacy_dir / name
                if candidate.exists():
                    ds_legacy = xr.open_zarr(candidate)
                    legacy_fname = name
                    break
            else:
                raise FileNotFoundError(f"Legacy Zarr not found at:\n"
                                        f" - {legacy_dir/int_name}\n"
                                        f" - {legacy_dir/float_name}")
        else:
            legacy_fname = f"{recipe}_{reduction}.zarr"
            ds_legacy    = xr.open_zarr(legacy_dir / legacy_fname)

        # Run refactored pipeline (writes integer-suffix for eta)
        ref_cfg = ConfigLoader(str(tmp_cfg))
        pipeline = DscimPipeline([
            LoadSectorDataStep("Load", sector, ref_cfg),
            ApplyReductionStep(
                "Apply", recipe, reduction,
                bottom_coding_gdppc=BOTTOM_CODING,
                eta=eta,
            ),
            SaveReducedDataStep(
                "Save", sector, ref_cfg,
                recipe, reduction,
                eta=eta,
                base_output_path=tmp_path / "refactored",
            ),
        ])
        pipeline.compute()

        # Load refactored output
        ref_path = tmp_path / "refactored" / sector / legacy_fname
        if not ref_path.exists():
            raise FileNotFoundError(f"Refactored Zarr not found at: {ref_path}")
        ds_ref = xr.open_zarr(ref_path)

        # Compare variable names
        assert set(ds_ref.data_vars) == set(ds_legacy.data_vars), (
            f"Variable mismatch:\n"
            f" Legacy only: {set(ds_legacy.data_vars) - set(ds_ref.data_vars)}\n"
            f" Refact only: {set(ds_ref.data_vars) - set(ds_legacy.data_vars)}"
        )

        # Compare data values
        for var in ds_legacy.data_vars:
            a = ds_legacy[var]
            b = ds_ref[var]

            # Align variable dimension names and shape
            try:
                b = b.transpose(*a.dims)
            except ValueError:
                # If dimensions mismatch, attempt to broadcast
                b = b.broadcast_like(a)

            # Final check to ensure same dimension order and shape
            assert b.dims == a.dims and b.shape == a.shape, (
                f"Dimension mismatch for variable '{var}':\n"
                f" Legacy dims: {a.dims}, shape: {a.shape}\n"
                f" Refact dims: {b.dims}, shape: {b.shape}"
            )

            xr.testing.assert_allclose(b, a, rtol=1e-6, atol=1e-9)

