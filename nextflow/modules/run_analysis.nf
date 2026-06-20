process RUN_ANALYSIS {
    tag "$input_source"

    publishDir params.outdir, mode: 'copy'

    input:
    val input_source
    path config_file
    val model
    val n_components

    output:
    path "output.h5ad"

    script:
    """
    python3 $projectDir/../src/run_pipeline.py \
        --input $input_source \
        --output output.h5ad \
        --config $config_file \
        --model $model \
        --n-components $n_components
    """
}