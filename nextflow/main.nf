nextflow.enable.dsl=2

params.input = null
params.outdir = "results/nextflow_pca"
params.model = "pca"
params.n_components = 50

include { RUN_ANALYSIS } from './modules/run_analysis.nf'

workflow {
    input_ch = Channel.value(params.input)
    config_file = Channel.fromPath(params.config_file, checkIfExists: true)

    RUN_ANALYSIS(
        input_ch,
        config_file,
        params.model,
        params.n_components
    )
}