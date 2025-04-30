# File: dscim_testing/examples/run_dummy_pipeline.py


import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from pipeline.pipeline import DscimPipeline
from pipeline.steps.load_sector import LoadSectorDataStep
from pipeline.steps.transform import ApplyReductionStep
from pipeline.steps.save import SaveReducedDataStep
from config.config_loader import ConfigLoader
from itertools import product
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)

# Load configuration
dummy_config_path = "../../configs/dummy_config.yaml"
config = ConfigLoader(dummy_config_path)

# Define sectors and reductions
sectors = {
    "coastal": "dummy_coastal_sector",
    "not_coastl": "dummy_not_coastl_sector"
}

# Which sectors to run
sectors.update(
    indiv_sectors=[sectors["not_coastl"]]
)

reductions = ["cc", "no_cc"]
recipe_discs = list(
    product(
        ["adding_up", "risk_aversion"],
        [None]  # Simplified: using only one discount for dummy run
    )
)

# Set eta values manually
eta_rhos = [[2.0, 0.0001]]

# Assume a bottom coding value passed manually for now
BOTTOM_CODING_GDPPC = 39.39265060424805

#%%
######################
# Run Pipeline
######################

for sector, reduction in product(sectors["indiv_sectors"], reductions):
    for recipe, _ in recipe_discs:
        if recipe == "adding_up":
            pipeline = DscimPipeline([
                LoadSectorDataStep(name="LoadSector", sector=sector, config=config),
                ApplyReductionStep(name="ApplyReduction", recipe=recipe, reduction=reduction, bottom_coding_gdppc=BOTTOM_CODING_GDPPC),
                SaveReducedDataStep(name="SaveReduced", sector=sector, config=config, recipe=recipe, reduction=reduction)
            ])
            pipeline.visualize().render(view=True)
            pipeline.compute()

        elif recipe == "risk_aversion":
            for eta, _ in eta_rhos:
                pipeline = DscimPipeline([
                    LoadSectorDataStep(name="LoadSector", sector=sector, config=config),
                    ApplyReductionStep(name="ApplyReduction", recipe=recipe, reduction=reduction, bottom_coding_gdppc=BOTTOM_CODING_GDPPC, eta=eta),
                    SaveReducedDataStep(name="SaveReduced", sector=sector, config=config, recipe=recipe, reduction=reduction, eta=eta)
                ])
                pipeline.visualize().render(view=True)
                pipeline.compute()

print("Dummy damage reduction pipeline completed!")
