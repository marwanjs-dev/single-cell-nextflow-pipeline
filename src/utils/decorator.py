import functools
import logging

from utils.error import PipelineError

# Fallback logger if the object does not have self.logger
fallback_logger = logging.getLogger("pipeline")


def handle_stage_errors(stage_name, wrap_error_class=PipelineError):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get the self instance to access its custom PipelineLogger
            self_obj = args[0] if args else None
            pipeline_logger = getattr(self_obj, "logger", None)

            try:
                return func(*args, **kwargs)
            except PipelineError as e:
                # 1. Expected pipeline errors are logged and re-raised directly
                if pipeline_logger and hasattr(pipeline_logger, "logger"):
                    pipeline_logger.logger.error(f"[{stage_name}] Pipeline error: {str(e)}")
                else:
                    fallback_logger.error(f"[{stage_name}] Pipeline error: {str(e)}")
                raise
            except Exception as e:
                # 2. Unexpected exceptions: Log the full traceback using PipelineLogger.log_exception if available
                if pipeline_logger and hasattr(pipeline_logger, "log_exception"):
                    pipeline_logger.log_exception(stage_name, e)
                else:
                    fallback_logger.error(f"[{stage_name}] Unexpected fatal error: {str(e)}", exc_info=True)

                # Wrap the exception while preserving the traceback chain via 'from e'
                raise wrap_error_class(f"Stage '{stage_name}' failed due to unexpected error: {str(e)}") from e
        return wrapper
    return decorator