import xarray as xr
from dscim_refactor.pipeline.pipeline import PipelineStep
from dscim_refactor.core.math_utils import ce_func

class ApplyReductionStep(PipelineStep):
    """
    Applies a damage reduction recipe and returns the result under the dynamic
    key matching the reduction (e.g. 'cc' or 'no_cc'), preserving the original
    variable name inside the Dataset.
    """
    def __init__(
        self,
        name: str,
        recipe: str,
        reduction: str,
        bottom_coding_gdppc: float,
        eta: float = None,
        zero: bool = False,
    ):
        super().__init__(name)
        self.recipe = recipe
        self.reduction = reduction
        self.bottom_code = bottom_coding_gdppc
        self.eta = eta
        self.zero = zero

    def process(self, inputs: dict) -> dict:
        ds      = inputs["damage_ds"]
        socioec = inputs["socioec_ds"]
        sector  = inputs["sector"]

        params = inputs["config"].sectors[sector]
        hist   = params["histclim"]
        delta  = params.get("delta")

        arr_hist  = ds[hist]
        arr_delta = ds[delta] if delta else None

        # 1) compute base damage change
        if self.reduction == "no_cc":
            if self.zero:
                arr_hist = xr.where(arr_hist == 0, 0, arr_hist)
            base = arr_hist.mean(dim="batch") - arr_hist
        elif self.reduction == "cc":
            base = arr_delta
        else:
            raise NotImplementedError(f"Unknown reduction: {self.reduction}")

        # 2) add/subtract GDPpc
        gdppc = socioec.gdppc
        calc  = (gdppc + base) if self.reduction == "no_cc" else (gdppc - base)

        # 3) clamp *before* aggregation/CE (identical to np.maximum(calc, bottom_code))
        calc = xr.where(calc < self.bottom_code, self.bottom_code, calc)

        # 4) apply recipe
        if self.recipe == "adding_up":
            out = calc.mean(dim="batch")
        elif self.recipe == "risk_aversion":
            out = xr.apply_ufunc(
                ce_func,
                calc,
                input_core_dims=[["batch"]],
                output_core_dims=[[]],
                vectorize=True,
                dask="parallelized",
                output_dtypes=[calc.dtype],
                kwargs={"eta": self.eta},
            )
        else:
            raise NotImplementedError(f"Unknown recipe: {self.recipe}")

        # 5) pack into a Dataset under the original variable name
        ds_out = out.rename(self.reduction).to_dataset()
        ds_out.attrs.update({
            "reduction": self.reduction,
            "recipe": self.recipe,
            "bottom_code": self.bottom_code,
        })

        # 6) return under dynamic key matching reduction
        return { self.reduction: ds_out }

    def describe_output(self) -> dict:
        return { self.reduction: f"xr.Dataset(var={self.reduction})" }
