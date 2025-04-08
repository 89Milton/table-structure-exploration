"""Tests for the TableExplorer class."""

import pytest
import pandas as pd
from table_structure_exploration.explorer import TableExplorer


def test_analyze_structure():
    """Test the analyze_structure method."""
    explorer = TableExplorer()
    data = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c'],
        'C': [1.1, 2.2, 3.3]
    })
    
    result = explorer.analyze_structure(data)
    
    assert 'columns' in result
    assert 'dtypes' in result
    assert 'shape' in result
    assert 'null_counts' in result
    assert result['shape'] == (3, 3)
    assert len(result['columns']) == 3


def test_get_column_statistics():
    """Test the get_column_statistics method."""
    explorer = TableExplorer()
    data = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    
    result = explorer.get_column_statistics(data)
    
    assert 'A' in result
    assert 'B' in result
    assert 'count' in result['A']
    assert 'mean' in result['A']
    assert 'std' in result['A'] 