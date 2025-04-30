# %%
import yaml
import xarray as xr
import pandas as pd
import numpy as np
import os
from pathlib import Path
import numpy as np

config_file_path = "configs/dummy_config.yaml"
config = yaml.load(open(config_file_path, 'r'), Loader=yaml.FullLoader)

# %%
os.makedirs('dummy_data', exist_ok=True)
dummy_data_dir = Path('dummy_data')
folders = ['climate','sectoral', 'econ']
for folder in folders:
    os.makedirs(dummy_data_dir / folder, exist_ok=True)

# %%
# GMST file to match temperatures to sectoral damages. CSV file that contains the following columns: 
# - year: int,
# - rcp: str,
# - gcm: str,
# - anomaly: float

years = np.arange(2020, 2031)
rcps = ['dummy1', 'dummy2']
gcms = ['dummy1', 'dummy2']
anomalies = np.random.uniform(0, 10, (len(years), len(rcps), len(gcms)))
data = []
for i, year in enumerate(years):
    for j, rcp in enumerate(rcps):
        for k, gcm in enumerate(gcms):
            data.append([year, rcp, gcm, anomalies[i, j, k]])
df = pd.DataFrame(data, columns=['year', 'rcp', 'gcm', 'anomaly'])
df.to_csv(config['AR6_ssp_climate']['gmst_path'], index=False)


# %%
import pandas as pd
import numpy as np

# GMSL file to match temperatures to sectoral coastal damages. Zarr file that contains the following coordinates: 
# - year: int,
# - slr: str,
# And the following data variable:
# - gmsl: float

slrs = [0, 1]
gmsls = np.random.uniform(0, 10, len(years))
data = []
for i, year in enumerate(years):
    for slr in slrs:
        data.append([year, slr, gmsls[i]])
        
df = pd.DataFrame(data, columns=['year', 'slr', 'gmsl'])
df.set_index(['year','slr'],inplace=True)
df.to_xarray().to_zarr(config['AR6_ssp_climate']['gmsl_path'])

# %%
# GMST control/pulse file. NC4 file that contains the following coordinates:
# - year: int,
# - rcp: str,
# - simulation: int,
# - gas: str,
# And the following data variables:
# - control_temperature: float,
# - pulse_temperature: float,
# - medianparams_control_temperature: float,
# - medianparams_pulse_temperature: float,

pulse_years = [2020]
years_extrap = np.arange(2001, 2100)
simulations = np.arange(4)
gas = ['dummy_gas']
control_temperatures = np.random.uniform(0, 10, (len(years_extrap), len(rcps), len(simulations), len(gas)))
pulse_temperatures = np.random.uniform(0, 10, (len(years_extrap), len(rcps), len(simulations), len(gas), len(pulse_years)))
medianparams_control_temperatures = np.random.uniform(0, 10, (len(years_extrap), len(rcps), len(gas)))
medianparams_pulse_temperatures = np.random.uniform(0, 10, (len(years_extrap), len(rcps), len(gas), len(pulse_years)))



data = {
    'control_temperature': (['year', 'rcp', 'simulation', 'gas'], control_temperatures),
    'pulse_temperature': (['year', 'rcp', 'simulation', 'gas', 'pulse_year'], pulse_temperatures),
    'medianparams_control_temperature': (['year', 'rcp', 'gas'], medianparams_control_temperatures),
    'medianparams_pulse_temperature': (['year', 'rcp', 'gas', 'pulse_year'], medianparams_pulse_temperatures)
}
            
ds = xr.Dataset(data_vars=data, coords={'year': years_extrap, 'rcp': rcps, 'simulation': simulations, 'gas': gas, 'pulse_year': pulse_years})
ds.to_netcdf(config['AR6_ssp_climate']['gmst_fair_path'])

# %%
# GMSL control/pulse file. NC4 file that contains the following coordinates:
# - year: int,
# - pulse_year: int,
# - rcp: str,
# - simulation: int,
# - gas: str,
# And the following data variables:
# - control_gmsl: float,
# - pulse_gmsl: float,
# - medianparams_control_gmsl: float,
# - medianparams_pulse_gmsl: float,


control_gmsls = np.random.uniform(0, 10, (len(years_extrap), len(rcps), len(simulations), len(gas)))
pulse_gmsls = np.random.uniform(0, 10, (len(years_extrap), len(rcps), len(simulations), len(gas), len(pulse_years)))
medianparams_control_gmsls = np.random.uniform(0, 10, (len(years_extrap), len(rcps), len(gas)))
medianparams_pulse_gmsls = np.random.uniform(0, 10, (len(years_extrap), len(rcps), len(gas), len(pulse_years)))
data = {
    'control_gmsl': (['year', 'rcp', 'simulation', 'gas'], control_gmsls),
    'pulse_gmsl': (['year', 'rcp', 'simulation', 'gas', 'pulse_years'], pulse_gmsls),
    'medianparams_control_gmsl': (['year', 'rcp', 'gas'], medianparams_control_gmsls),
    'medianparams_pulse_gmsl': (['year', 'rcp', 'gas', 'pulse_years'], medianparams_pulse_gmsls)
}
            
ds = xr.Dataset(data_vars=data, coords={'year': years_extrap, 'rcp': rcps, 'simulation': simulations, 'gas': gas, 'pulse_years': pulse_years})
ds.to_netcdf(config['AR6_ssp_climate']['gmsl_fair_path'])

# %%
# This file converts large pulses of gigatons of a gas to a one ton pulse. NC4 file that contains the following coordinates:
# - gas: str,
# And the following data variable:
# - emissions: float,

data = {'emissions': 0.1}
ds = xr.Dataset(data_vars=data, coords={'gas': ['dummy_gas']})

ds.to_netcdf(config['AR6_ssp_climate']['damages_pulse_conversion_path'])

# %%
# This file contains socioeconomic data. Zarr file that contains the following coordinates:
# -year: int,
# -SSP: str,
# -region: str,
# -iam: str,
# And the following data variables:
# -pop: float,
# -gdppc: float,
# -gdp: float,

SSPs = ['ssp1','ssp2','ssp3','ssp4','ssp5']
regions = ['dummy1','dummy2']
iams = ['dummy1','dummy2']
pop = np.random.uniform(20, 100, (len(years), len(SSPs), len(regions), len(iams)))
gdppc = np.random.uniform(50, 100, (len(years), len(SSPs), len(regions), len(iams)))
gdp = pop * gdppc
data = {
    'pop': (('year', 'ssp', 'region', 'model'), pop),
    'gdppc': (('year', 'ssp', 'region', 'model'), gdppc),
    'gdp': (('year', 'ssp', 'region', 'model'), gdp)
}
ds = xr.Dataset(data_vars=data, coords={'year': years, 'ssp': SSPs, 'region': regions, 'model': iams})
ds.to_zarr(config['econdata']['global_ssp'], mode = 'w')

# %%
# Sectoral damages file. Zarr file that contains the following coordinates:
# -year: int,
# -SSP: str,
# -region: str,
# -iam: str,
# -gcm: str,
# -rcp: str,
# -batch: int,
# And the following data variables:
# -delta_dummy: float,
# -histclim_dummy: float,

batches = np.arange(15)
delta_dummy = np.random.uniform(5, 15, (len(rcps), len(regions), len(gcms), len(years), len(iams), len(SSPs), len(batches)))
histclim_dummy = np.random.uniform(1, 10, (len(rcps), len(regions), len(gcms), len(years), len(iams), len(SSPs), len(batches)))

delta_name = config['sectors']['dummy_not_coastl_sector']['delta']
histclim_name = config['sectors']['dummy_not_coastl_sector']['histclim']

data = {
    delta_name: (('rcp', 'region', 'gcm', 'year', 'model', 'ssp', 'batch'), delta_dummy),
    histclim_name: (('rcp', 'region', 'gcm', 'year', 'model', 'ssp', 'batch'), histclim_dummy)
}
ds = xr.Dataset(data_vars=data, coords={ 'rcp': rcps, 'region': regions, 'gcm': gcms, 'year': years, 'model': iams, 'ssp': SSPs, 'batch':batches}).chunk({'batch':-1})
ds.to_zarr(config['sectors']['dummy_not_coastl_sector']['sector_path'], mode = 'w')

# %%
# Sectoral damages file. Zarr file that contains the following coordinates:
# -year: int,
# -SSP: str,
# -region: str,
# -iam: str,
# -slr: str,
# -batch: int,
# And the following data variables:
# -delta_dummy: float,
# -histclim_dummy: float,

delta_dummy = np.random.uniform(5, 15, (len(regions),  len(years), len(batches), len(slrs), len(iams), len(SSPs)))
histclim_dummy = np.random.uniform(1, 10, (len(regions),  len(years), len(batches), len(slrs), len(iams), len(SSPs)))

delta_name = config['sectors']['dummy_coastal_sector']['delta']
histclim_name = config['sectors']['dummy_coastal_sector']['histclim']

data = {
    delta_name: (('region', 'year', 'batch', 'slr', 'model', 'ssp'), delta_dummy),
    histclim_name: (('region', 'year', 'batch', 'slr', 'model', 'ssp'), histclim_dummy)
}
ds = xr.Dataset(data_vars=data, coords={'region': regions, 'slr': slrs, 'year': years, 'model': iams, 'ssp': SSPs, 'batch':batches}).chunk({'region':1,'slr':1,'year':1,'model':1,'ssp':1, 'batch':-1})
ds.to_zarr(config['sectors']['dummy_coastal_sector']['sector_path'], mode = 'w')

# %%
# to avoid errors in next step
np.random.seed(42)

