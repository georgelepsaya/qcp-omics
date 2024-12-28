import functools
from typing import Tuple


def report_step(snapshot=False, output=False):
    def report_step_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            step_name = func.__name__
            data_snapshot: Tuple[str, str] = None
            if snapshot:
                data_snapshot = self._visualize_data_snapshot()
            self.report_data.append({
                "step": step_name,
                "data_snapshot": data_snapshot,
                "output": result if output else None
            })
            return result
        return wrapper
    return report_step_decorator
