from sklearn.decomposition import PCA
from models.base import BaseEmbeddingModel
import numpy as np


class PCAWrapper(BaseEmbeddingModel):
    def __init__(self, params=None):
        super().__init__(params)
        self.n_components = self.params.get("n_components", 50)
        self.model = None

    def fit_transform(self, adata):
        X = adata.X

        if hasattr(X, "toarray"):
            X = X.toarray()

        self.model = PCA(n_components=self.n_components)
        Z = self.model.fit_transform(X)

        adata.obsm["X_pca"] = Z
        adata.uns["pca"] = {
            "explained_variance_ratio": self.model.explained_variance_ratio_.tolist(),
            "explained_variance": self.model.explained_variance_.tolist(),
        }

        return adata