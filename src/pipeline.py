from utils.decorator import handle_stage_errors
from utils.logger import PipelineLogger
from utils.error import PipelineError
from data.dataloader import DataLoader
from clustering import Clusterer
from models.pca import PCAWrapper
from models.scvi import SCVIWrapper
from preprocessing import Preprocessor


class Pipeline:
    def __init__(self, dataloader, preprocessor, model, clusterer, config=None):
        self.dataloader = dataloader
        self.preprocessor = preprocessor
        self.model = model
        self.clusterer = clusterer
        self.config = config or {}
        self.logger = PipelineLogger(out_dir=self.config.get("out_dir", "output"), name="pipeline")
        
    @classmethod
    def from_config(cls, config):
        dataloader = DataLoader(config=config.get("dataloader"))
        preprocessor = Preprocessor(config=config.get("preprocessor"))
        model_name = config.get("model", "pca").lower()
        if model_name == "pca":
            model = PCAWrapper(config=config.get("model_config"))
        elif model_name == "scvi":
            model = SCVIWrapper(config=config.get("model_config"))
        else:
            raise PipelineError(f"Unsupported model specified: {model_name}")
        clusterer = Clusterer(config=config.get("clustering"))
        return cls(dataloader, preprocessor, model, clusterer, config=config)
    
    @handle_stage_errors("Pipeline Execution", wrap_error_class=PipelineError)
    def run(self, file_path):
        adata = self.dataloader.load_data(file_path)
        self.logger.log_artifacts("raw_data", {"n_cells": adata.n_obs, "n_genes": adata.n_vars})
        
        adata = self.preprocessor.run(adata)
        self.logger.log_artifacts("preprocessing", {"n_cells": adata.n_obs, "n_genes": adata.n_vars})
        
        adata = self.model.fit_transform(adata)
        self.logger.log_artifacts("model", {"embedding_key": self.model.embedding_key})
        
        adata = self.clusterer.run(adata)
        self.logger.log_artifacts("clustering", {"clusters": adata.obs["leiden"].unique().tolist()})
        
        return adata