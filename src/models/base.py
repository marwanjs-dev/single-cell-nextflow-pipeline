class BaseEmbeddingModel:
    def __init__(self, params=None):
        self.params = params or {}

    def fit(self, adata):
        raise NotImplementedError

    def transform(self, adata):
        raise NotImplementedError

    def fit_transform(self, adata):
        self.fit(adata)
        return self.transform(adata)

    def get_artifacts(self):
        return {}