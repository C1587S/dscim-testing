# dscim/pipeline/steps/transform.py
from dscim_refactor.pipeline.pipeline import PipelineStep
from dscim_refactor.core.aggregation import reduce_damages
from dscim_refactor.utils.logger import setup_logger

logger = setup_logger(__name__)

class ApplyReductionStep(PipelineStep):
    def __init__(self, name, recipe, reduction, bottom_coding_gdppc, eta=None, zero=False):
        super().__init__(name)
        self.recipe = recipe
        self.reduction = reduction
        self.bottom_coding_gdppc = bottom_coding_gdppc
        self.eta = eta
        self.zero = zero

    def compute(self, data):
        logger.info(f"[{self.name}] Applying reduction: {self.recipe}, eta={self.eta}")
        reduced = reduce_damages(
            damages=data["damages"],
            socioec=data["socioec"],
            recipe=self.recipe,
            reduction=self.reduction,
            bottom_coding_gdppc=self.bottom_coding_gdppc,
            eta=self.eta,
            zero=self.zero
        )
        data["reduced"] = reduced
        return data

    def get_metadata(self):
        return {
            **super().get_metadata(),
            "recipe": self.recipe,
            "reduction": self.reduction,
            "eta": self.eta,
            "zero": self.zero,
        }

    def describe_output(self):
        return {
            "reduced": "dims: year, ssp, region, model, rcp, gcm",
        }
