from abc import ABC, abstractmethod
import pandas as pd

#
# class OmicsData(ABC):
#     def __init__(self, file_path: str):
#         try:
#             self.data = pd.read_csv(file_path)
#
#             # check if the file is empty
#             if self.data.empty:
#                 raise ValueError("The file was read successfully but no data was found")
#
#         except FileNotFoundError:
#             raise FileNotFoundError(f"File not found: {file_path}")
#
#         except pd.errors.EmptyDataError:
#             raise pd.errors.EmptyDataError(f"The file is empty or contains errors: {file_path}")
#
#         except Exception as e:
#             raise RuntimeError(f"An error occurred while reading the file: {e}")
