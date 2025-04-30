from dscim_refactor.pipeline.pipeline import PipelineStep
from dscim_refactor.ioutils.saver import save_zarr
from dscim_refactor.utils.logger import setup_logger
from pathlib import Path

logger = setup_logger(__name__)

class SaveReducedDataStep(PipelineStep):
    def __init__(self, name, sector, config, recipe, reduction, eta=None, base_output_path=None):
        super().__init__(name)
        self.sector = sector
        self.config = config
        self.recipe = recipe
        self.reduction = reduction
        self.eta = eta
        self.base_output_path = Path(base_output_path) if base_output_path else None

    def compute(self, data):
        logger.info(f"[{self.name}] Saving reduced data: sector={self.sector}, recipe={self.recipe}")
        save_zarr(
            ds=data["reduced"],
            config=self.config,
            sector=self.sector,
            recipe=self.recipe,
            reduction=self.reduction,
            eta=self.eta,
            base_path=self.base_output_path  # <-- new argument
        )
        return data

    def get_metadata(self):
        return {
            **super().get_metadata(),
            "sector": self.sector,
            "recipe": self.recipe,
            "reduction": self.reduction,
            "eta": self.eta,
            "output_dir": str(self.base_output_path) if self.base_output_path else "default (from config)"
        }

    def describe_output(self):
        return {
            "output_location": self.base_output_path or "config.paths.reduced_damages_library"
        }
