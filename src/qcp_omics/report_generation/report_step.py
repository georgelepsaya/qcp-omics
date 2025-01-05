import functools
from typing import Tuple, Optional, Union, Literal, Callable, Any, Dict

import pandas as pd


def report_step(
        snapshot: Optional[Literal["combined", "split", "numerical", "categorical"]] = None,
        output: bool = False
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    A decorator for capturing and reporting steps in a processing pipeline.

    Args:
        snapshot (Optional[Literal["combined", "split", "numerical", "categorical"]]):
            Specifies the type of data snapshot to capture during the step.
            - "combined": Takes a snapshot of the combined dataset.
            - "split": Takes snapshots of both numerical and categorical datasets.
            - "numerical": Takes a snapshot of the numerical dataset.
            - "categorical": Takes a snapshot of the categorical dataset.
        output (bool): If True, captures and includes the step output in the report.

    Returns:
        Callable: A decorator that processes and appends report data for each step.
    """

    def report_step_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            result = func(self, *args, **kwargs)
            step_name = func.__name__

            data_snapshot: Optional[Union[Tuple[str, str], str]] = None

            try:
                # Capture the specified data snapshot
                if snapshot == "combined":
                    data_snapshot = self._visualize_data_snapshot(self.data)
                elif snapshot == "split":
                    data_snapshot = (
                        self._visualize_data_snapshot(self.data_numerical),
                        self._visualize_data_snapshot(self.data_categorical)
                    )
                elif snapshot == "numerical":
                    data_snapshot = self._visualize_data_snapshot(self.data_numerical)
                elif snapshot == "categorical":
                    data_snapshot = self._visualize_data_snapshot(self.data_categorical)
            except AttributeError as e:
                raise RuntimeError(f"Error capturing snapshot for step '{step_name}': {e}")

            # Handle the result based on its type
            if isinstance(result, pd.DataFrame):
                final_output = self._visualize_data_snapshot(result)
            elif isinstance(result, str):
                final_output = result
            elif isinstance(result, dict):
                final_output = {}
                for key, val in result.items():
                    if isinstance(val, pd.DataFrame):
                        final_output[key] = self._visualize_data_snapshot(val)
                    else:
                        final_output[key] = val
            else:
                final_output = result

            method_name: Optional[str] = None

            for step in self.metadata["steps_to_run"]:
                if step["step"] == step_name:
                    method_name = step.get("method", None)

            # Append the step information to the report
            self.report_data.append({
                "step": step_name,
                "method": method_name,
                "data_snapshot": data_snapshot,
                "data_snapshot_type": snapshot,
                "output": final_output if output else None
            })

            return result

        return wrapper

    return report_step_decorator
