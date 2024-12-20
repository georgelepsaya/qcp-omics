import functools

def report_step(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        step_name = func.__name__
        data_snapshot = self.data.copy()
        self.report_data.append({
            "step": step_name,
            "data": data_snapshot
        })
        return result
    return wrapper
