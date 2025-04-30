import xarray as xr
from pathlib import Path

from dscim_refactor.pipeline.pipeline import PipelineStep

class LoadSectorDataStep(PipelineStep):
    """
    Loads sectoral damage and socioeconomic Zarrs.
    Outputs keys matching ApplyReductionStep inputs.
    """
    def __init__(self, name: str, sector: str, config):
        super().__init__(name)
        self.sector = sector
        self.config = config

    def process(self, inputs: dict) -> dict:
        sector_info = self.config.sectors[self.sector]
        # full paths resolve via base_path
        sector_path = Path(self.config.base_path) / sector_info["sector_path"]
        socioec_path = Path(self.config.base_path) / self.config.econdata["global_ssp"]

        ds_damages = xr.open_zarr(sector_path, consolidated=True)
        ds_socioec = xr.open_zarr(socioec_path, consolidated=True)

        return {
            "damage_ds": ds_damages,
            "socioec_ds": ds_socioec,
            "sector": self.sector,
            "config": self.config,
        }

    def describe_output(self) -> dict:
        return {
            "damage_ds": "xr.Dataset",
            "socioec_ds": "xr.Dataset",
            "sector": "str",
            "config": "ConfigLoader",
        }

