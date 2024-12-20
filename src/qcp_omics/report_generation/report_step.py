import functools
import pandas as pd
import typing as t


def report_step(snapshot=False, dict_out=False):
    def report_step_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            step_name = func.__name__
            data_snapshot: t.Optional[pd.DataFrame] = None
            dict_output: t.Optional[dict] = None
            if snapshot:
                data_snapshot = self.data.copy()
            if dict_out:
                dict_output = result
            self.report_data.append({
                "step": step_name,
                "data": data_snapshot,
                "output": dict_output
            })
            return result
        return wrapper
    return report_step_decorator
