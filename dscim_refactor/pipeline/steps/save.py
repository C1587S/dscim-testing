from pathlib import Path
import logging

from dscim_refactor.pipeline.pipeline import PipelineStep
from pathlib import Path
import logging
import xarray as xr

from dscim_refactor.pipeline.pipeline import PipelineStep

logger = logging.getLogger(__name__)

class SaveReducedDataStep(PipelineStep):
    """
    Pipeline step to save a reduced Dataset to Zarr under a dynamic filename that
    includes the reduction and optional eta suffix.
    """
    def __init__(
        self,
        name: str,
        sector: str,
        config,
        recipe: str,
        reduction: str,
        eta: float = None,
        base_output_path: Path = None,
    ):
        super().__init__(name)
        self.sector = sector
        self.config = config
        self.recipe = recipe
        self.reduction = reduction
        self.eta = eta
        self.base_output_path = Path(base_output_path) if base_output_path else None

    def compute(self, data: dict) -> dict:
        # Retrieve the Dataset under the dynamic key matching the reduction
        ds_to_save = data[self.reduction]

                # Construct output filename
        filename = f"{self.recipe}_{self.reduction}"
        if self.eta is not None:
            # match legacy naming: always include decimal point
            filename += f"_eta{self.eta}"
        filename += ".zarr"

        # Determine output path
        base = self.base_output_path or Path(self.config.paths["reduced_damages_library"])
        out_path = base / self.sector / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Log and save directly
        logger.info(f"[{self.name}] Writing reduced data to: {out_path}")
        ds_to_save.to_zarr(str(out_path), mode="w", consolidated=True)
        logger.info(f"[{self.name}] Completed write to: {out_path}")

        return data

    def get_metadata(self) -> dict:
        meta = super().get_metadata()
        meta.update({
            "sector": self.sector,
            "recipe": self.recipe,
            "reduction": self.reduction,
            "eta": self.eta,
            "output_dir": str(self.base_output_path) if self.base_output_path else self.config.paths.get("reduced_damages_library"),
        })
        return meta

    def describe_output(self) -> dict:
        return {"output_path": "Path to saved Zarr file"}
