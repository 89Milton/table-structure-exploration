"""
Main module for table structure exploration.
"""

import pandas as pd
from typing import Dict, Any, List


class TableExplorer:
    """Class for exploring table structures."""

    def __init__(self):
        """Initialize the TableExplorer."""
        pass

    def analyze_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the structure of a pandas DataFrame.

        Args:
            data: pandas DataFrame to analyze

        Returns:
            Dictionary containing structure information
        """
        return {
            "columns": list(data.columns),
            "dtypes": data.dtypes.to_dict(),
            "shape": data.shape,
            "null_counts": data.isnull().sum().to_dict(),
        }

    def get_column_statistics(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Get basic statistics for each column in the DataFrame.

        Args:
            data: pandas DataFrame to analyze

        Returns:
            Dictionary containing statistics for each column
        """
        return data.describe().to_dict() 