import scanpy as sc
from utils.decorator import handle_stage_errors
from utils.error import ClusterError
from utils.logger import PipelineLogger

    
class Clusterer:
    def __init__(self, config=None):
        self.config = config or {}
        self.artifacts = {}
        self.logger = PipelineLogger(out_dir=self.config.get("out_dir", "output"), name="clustering")
        
    @handle_stage_errors("Clustering", wrap_error_class=ClusterError)
    def run(self, adata):
        adata = self._neighbors(adata)
        self.logger.log_artifacts("neighbors", self.artifacts["neighbors"])
        adata = self._umap(adata)
        self.logger.log_artifacts("umap", self.artifacts["umap"])
        adata = self._leiden(adata)
        self.logger.log_artifacts("leiden", self.artifacts["leiden"])
        return adata
    
    def _neighbors(self, adata):
        n_neighbors = self.config.get("n_neighbors", 15)
        n_pcs = self.config.get("n_pcs", 50)
        embedding_key = self.config.get("embedding_key", "X_pca")

        sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs, use_rep=embedding_key)
        
        self.artifacts["neighbors"] = {
            "n_neighbors": n_neighbors,
            "n_pcs": n_pcs,
            "embedding_key": embedding_key
        }
        return adata
        
    def _umap(self, adata):
        min_dist = self.config.get("umap_min_dist", 0.5)
        sc.tl.umap(adata, min_dist=min_dist)
        self.artifacts["umap"] = {
            "min_dist": min_dist,
            "n_cells": adata.n_obs
        }
        return adata
        
    def _leiden(self, adata):
        resolution = self.config.get("leiden_resolution", 1.0)
        sc.tl.leiden(adata, resolution=resolution)
        n_clusters = adata.obs["leiden"].nunique()
        cluster_sizes = adata.obs["leiden"].value_counts().to_dict()
        self.artifacts["leiden"] = {
            "resolution": resolution,
            "n_clusters": n_clusters,
            "cluster_sizes": cluster_sizes
        }
        return adata