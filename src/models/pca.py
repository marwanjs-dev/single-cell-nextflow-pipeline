from sklearn.decomposition import PCA
from .base import BaseEmbeddingModel

class PCAWrapper(BaseEmbeddingModel):
    def __init__(self, config, params=None):
        super().__init__(params)
        self.model = None
        self.config = config
        self.embedding_key = self.config.get("embedding_key", "X_pca")

    def fit_transform(self, adata):
        X = adata.X

        if hasattr(X, "toarray"):
            X = X.toarray()

        self.model = PCA(n_components=self.config.get("n_components", 50))
        Z = self.model.fit_transform(X)

        adata.obsm[self.embedding_key] = Z
        adata.uns["pca"] = {
            "explained_variance_ratio": self.model.explained_variance_ratio_.tolist(),
            "explained_variance": self.model.explained_variance_.tolist(),
        }
        return adata