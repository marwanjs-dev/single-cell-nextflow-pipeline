from pathlib import Path

import scanpy as sc
import anndata as ad
from utils.decorator import handle_stage_errors
from utils.error import DataLoadingError

class DataLoader:
    def __init__(self, config=None):
        self.config = config or {}
        self.supported_scanpy_datasets = sc.datasets.__all__
        
    @handle_stage_errors("Data Loading", wrap_error_class=DataLoadingError)
    def load_data(self, file_path=None) -> ad.AnnData:
        dataset_name = self.config.get("dataset_name")

        if file_path:
            adata = self._load_from_path(file_path)

        elif dataset_name:
            if self._is_path(dataset_name):
                adata = self._load_from_path(dataset_name)
            else:
                adata = self._load_scanpy_dataset(dataset_name)

        else:
            raise DataLoadingError("No input file path or dataset name provided in config")

        self._validate_adata(adata)

        return adata

    def _load_from_path(self, file_path) -> ad.AnnData:
        path = Path(file_path)

        if not path.exists():
            raise DataLoadingError(f"Input file does not exist: {path}")

        return sc.read(path)

    def _load_scanpy_dataset(self, dataset_name: str) -> ad.AnnData:
        if dataset_name not in self.supported_scanpy_datasets:
            raise DataLoadingError(
                f"Unsupported Scanpy dataset: {dataset_name}. "
                f"Supported datasets are: {sorted(self.supported_scanpy_datasets)}"
            )

        dataset_fn = getattr(sc.datasets, dataset_name)
        return dataset_fn()

    def _is_path(self, value: str) -> bool:
        path = Path(value)

        return (
            path.suffix != ""
            or "/" in value
            or "\\" in value
        )

    def _validate_adata(self, adata: ad.AnnData) -> None:
        if adata.n_obs == 0 or adata.n_vars == 0:
            raise DataLoadingError(
                f"Loaded AnnData is empty: n_obs={adata.n_obs}, n_vars={adata.n_vars}"
            )