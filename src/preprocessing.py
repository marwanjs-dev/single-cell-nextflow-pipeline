from anndata import AnnData
import scanpy as sc

class Preprocessor:
    def __init__(self, config=None):
        self.config = config or {}
        self.artifacts = {}
        
    def run(self, adata):
        adata.raw = adata.copy()  # Keep a copy of the raw data
        adata = self._qc_metrics(adata)
        adata = self._filter_cells(adata)
        adata = self._filter_genes(adata)
        adata = self._log_transform(adata)
        adata = self._hvg(adata)
        adata = self._finalize(adata)
        return adata
        
    def _qc_metrics(self, adata):
        adata.var["mt"] = adata.var_names.str.startswith("MT-")
        sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
        
        self.artifacts["qc_before_filtering"] = {
            "n_cells": adata.n_obs,
            "n_genes": adata.n_vars,
            "percent_mt": adata.obs["pct_counts_mt"].mean()
        }
        return adata
    
    def _filter_cells(self, adata):
        min_genes = self.config.get("min_genes", 200)
        max_genes = self.config.get("max_genes", 6000)
        max_pct_mt = self.config.get("max_pct_mt", 20)
        
        n_before = adata.n_obs
        
        sc.pp.filter_cells(adata, min_genes=min_genes).copy()
        sc.pp.filter_cells(adata, max_genes=max_genes).copy()
        adata = adata[adata.obs["pct_counts_mt"] < max_pct_mt].copy()
        
        self.artifacts["qc_after_filtering"] = {
            "n_before": n_before,
            "n_after": adata.n_obs,
            "n_removed": n_before - adata.n_obs
        }
        return adata
    
    def _filter_genes(self, adata):
        min_cells = self.config.get("min_cells", 3)
        n_before = adata.n_vars
        sc.pp.filter_genes(adata, min_cells=min_cells)
        self.artifacts["gene_filtering"] = {
            "n_before": n_before,
            "n_after": adata.n_vars,
            "n_removed": n_before - adata.n_vars
        }
        return adata
    
    def _log_transform(self, adata):
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        self.artifacts["log_transform"] = {
            "method": "log1p",
            "target_sum": 1e4
        }
        return adata
    
    def _hvg(self, adata):
        n_top_genes = self.config.get("n_top_genes", 2000)
        sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes, flavor="seurat_v3", subset=False)
        n_hvg = adata.var["highly_variable"].sum()
        
        self.artifacts["hvg"] = {
            "n_top_genes": n_top_genes,
            "n_hvg": n_hvg
        }
        
        adata = adata[:, adata.var["highly_variable"]].copy()
        return adata
    
    def _finalize(self, adata):
        adata.uns["preprocessing"] = {
            "config": self.config,
            "n_cells_final": adata.n_obs,
            "n_genes_final": adata.n_vars
        }
        return adata