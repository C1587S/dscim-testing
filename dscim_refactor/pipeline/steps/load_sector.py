# dscim/pipeline/steps/load_sector.py
from dscim_refactor.pipeline.pipeline import PipelineStep
from dscim_refactor.utils.logger import setup_logger
import xarray as xr

logger = setup_logger(__name__)

class LoadSectorDataStep(PipelineStep):
    def __init__(self, name, sector, config, consolidated=True):
        super().__init__(name)
        self.sector = sector
        self.config = config
        self.consolidated = consolidated

    def compute(self, data):
        sector_info = self.config.sectors[self.sector]
        sector_path = (self.config.base_path / sector_info["sector_path"]).resolve()
        socioec_path = (self.config.base_path / self.config.econdata["global_ssp"]).resolve()

        logger.info(f"[{self.name}] Loading sector data from: {sector_path}")
        logger.info(f"[{self.name}] Loading socioeconomic data from: {socioec_path}")

        ds_damages = xr.open_zarr(sector_path, consolidated=self.consolidated)
        ds_socioec = xr.open_zarr(socioec_path, consolidated=self.consolidated)

        return {
            "damages": ds_damages,
            "socioec": ds_socioec,
            "sector_path": sector_path,
        }

    def get_metadata(self):
        return {
            **super().get_metadata(),
            "sector": self.sector,
            "consolidated": self.consolidated,
        }

    def describe_output(self):
        return {
            "damages": "dims: rcp, region, gcm, year, model, ssp, batch",
            "socioec": "dims: year, ssp, region, model"
        }
