import yaml
from pipeline import Pipeline
import argparse
import logging
import os
import sys

from utils.error import PipelineError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("runner")

def parse_args():
    parser = argparse.ArgumentParser(description="Single-Cell RNA-seq Analysis Pipeline")
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    parser.add_argument("--input", default=None, help="Path to input data file (.h5ad or URL)")
    parser.add_argument("--output", required=True, help="Path to write the processed .h5ad file")
    return parser.parse_args()


def main():
    args = parse_args()
    # 1. Validate config path exists
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    # 2. Read config
    try:
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to parse YAML config: {str(e)}")
        sys.exit(1)
    try:
        # Pass input/output parameters dynamically to override or supplement config
        pipeline = Pipeline.from_config(config)
        
        # The pipeline class executes the steps and returns the final AnnData
        adata = pipeline.run(args.input)
        
        # 4. Save output
        logger.info(f"Writing final AnnData object to {args.output}...")
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        adata.write(args.output)
        logger.info("Pipeline executed successfully!")
        
    except PipelineError as e:
        logger.error(f"Pipeline Execution Failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error("Unhandled system error occurred", exc_info=True)
        sys.exit(1)

    
if __name__ == "__main__":
    main()