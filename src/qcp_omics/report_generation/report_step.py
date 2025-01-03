import functools
from typing import Tuple, Optional, Union, Literal

import pandas as pd


def report_step(snapshot: Optional[Literal["combined", "split", "numerical", "categorical"]] = None,
                output: bool = False
                ):
    def report_step_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            step_name = func.__name__

            data_snapshot: Optional[Union[Tuple[str, str], str]] = None
            # TODO: add error handling here
            if snapshot == "combined":
                data_snapshot = self._visualize_data_snapshot(self.data)
            elif snapshot == "split":
                data_snapshot = (self._visualize_data_snapshot(self.data_numerical),
                                 self._visualize_data_snapshot(self.data_categorical))
            elif snapshot == "numerical":
                data_snapshot = self._visualize_data_snapshot(self.data_numerical)
            elif snapshot == "categorical":
                data_snapshot = self._visualize_data_snapshot(self.data_categorical)

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

            self.report_data.append({
                "step": step_name,
                "data_snapshot": data_snapshot,
                "data_snapshot_type": snapshot,
                "output": final_output if output else None
            })
            return result
        return wrapper
    return report_step_decorator
