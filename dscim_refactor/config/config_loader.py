import yaml
from pathlib import Path

class ConfigLoader:
    """
    Loads a YAML configuration file and resolves all internal relative paths
    based on a configurable project root directory.
    """

    def __init__(self, config_path: str, base_path: str = None):
        self.config_path = Path(config_path).resolve()
        self.base_path = Path(base_path).resolve() if base_path else self.config_path.parent
        self._load()
        self._validate()
        self._resolve_all_paths()

    def _load(self):
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def _validate(self):
        required_top_keys = ["paths", "sectors", "econdata", "AR6_ssp_climate"]
        for key in required_top_keys:
            if key not in self.config:
                raise ValueError(f"Missing required section '{key}' in config.")

    def _resolve_path(self, raw_path: str) -> str:
        path = Path(raw_path)
        return str((self.base_path / path).resolve()) if not path.is_absolute() else str(path)

    def _resolve_all_paths(self):
        # Econdata
        self.config["econdata"] = {
            k: self._resolve_path(v) for k, v in self.config["econdata"].items()
        }

        # Output/result paths
        self.config["paths"] = {
            k: self._resolve_path(v) for k, v in self.config["paths"].items()
        }

        # Sector Zarr paths
        for sector_info in self.config["sectors"].values():
            if "sector_path" in sector_info:
                sector_info["sector_path"] = self._resolve_path(sector_info["sector_path"])

        # Climate inputs
        self.config["AR6_ssp_climate"] = {
            k: self._resolve_path(v) if k.endswith("_path") else v
            for k, v in self.config["AR6_ssp_climate"].items()
        }

    # Convenience accessors
    @property
    def paths(self):
        return self.config["paths"]

    @property
    def sectors(self):
        return self.config["sectors"]

    @property
    def econdata(self):
        return self.config["econdata"]

    @property
    def climate(self):
        return self.config["AR6_ssp_climate"]

    @property
    def global_parameters(self):
        return self.config.get("global_parameters", {})

    def __repr__(self):
        return f"ConfigLoader(config_path={self.config_path})"
