# single-cell-nextflow-pipeline

A reproducible single-cell RNA-seq analysis pipeline built with Nextflow.

## Workflow

Input:
- AnnData (.h5ad)

Pipeline:

1. Quality Control
2. Filtering
3. Normalization
4. Highly Variable Gene Selection
5. PCA
6. Neighborhood Graph
7. UMAP
8. Leiden Clustering
9. Marker Gene Analysis
10. HTML Report

Output:
- Processed AnnData
- Figures
- Metrics
- Report

# run

uv run python src/run_pipeline.py --config config/config.yml --output output/final.h5ad

nextflow run nextflow/main.nf \
  --input data/input.h5ad \
  --outdir results/nextflow_pca \
  --model pca \
  --n_components 50