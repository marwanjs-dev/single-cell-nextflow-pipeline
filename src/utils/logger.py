import json
import logging
import os
from datetime import datetime
import traceback

class PipelineLogger:
    # def __init__(self, out_dir, name="pipeline"):
    #     self.out_dir = out_dir
    #     os.makedirs(out_dir, exist_ok=True)
        
    #     # 1. Python logger — human-readable .log file
    #     self.logger = logging.getLogger(name)
    #     self.logger.setLevel(logging.INFO)
        
    #     fh = logging.FileHandler(os.path.join(out_dir, f"{name}.log"))
    #     fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    #     self.logger.addHandler(fh)
        
    #     # Also print to console
    #     self.logger.addHandler(logging.StreamHandler())
    
    def __init__(self, out_dir, name="pipeline"):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # Avoid duplicate handlers if PipelineLogger is created multiple times
        if self.logger.handlers:
            self.logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
        )

        file_handler = logging.FileHandler(
            os.path.join(out_dir, f"{name}.log"),
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def log_artifacts(self, stage, artifacts):
        json_path = os.path.join(self.out_dir, f"{stage}.json")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "stage": stage,
                    "timestamp": datetime.now().isoformat(),
                    **artifacts,
                },
                f,
                indent=2,
                default=self._json_default
            )

        self.logger.info(
            f"[{stage}] " + " | ".join(f"{k}={v}" for k, v in artifacts.items()),
            stacklevel=2
        )
        
    def _json_default(self, obj):
        import numpy as np
        import pandas as pd

        if isinstance(obj, np.integer):
            return int(obj)

        if isinstance(obj, np.floating):
            return float(obj)

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, pd.Series):
            return obj.tolist()

        if isinstance(obj, pd.Index):
            return obj.tolist()

        if isinstance(obj, set):
            return list(obj)

        return str(obj)

        
    def log_exception(self, stage, error):
        """
        Logs full traceback to the .log file and writes a structured error JSON.
        """
        import os
        tb = error.__traceback__
        error_loc = ""
        while tb:
            filename = tb.tb_frame.f_code.co_filename
            # Traverses to the leaf frame where the exception actually occurred
            if not tb.tb_next:
                basename = os.path.basename(filename)
                error_loc = f" at {basename}:{tb.tb_lineno}"
            tb = tb.tb_next

        self.logger.exception(f"[{stage}] failed{error_loc}: {error}", stacklevel=2)

        json_path = os.path.join(self.out_dir, f"{stage}_error.json")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "stage": stage,
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "traceback": traceback.format_exc(),
                },
                f,
                indent=2,
            )