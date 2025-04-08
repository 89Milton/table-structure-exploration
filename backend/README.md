# Table Structure Exploration Backend

The Python backend for the Table Structure Exploration project.

## Description
This component provides the API and processing logic for analyzing table structures in various data formats such as CSV, Excel, and database tables.

## Features
- Table structure analysis
- Schema exploration
- Data type inference
- Relationship mapping
- RESTful API endpoints

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from table_structure_exploration import TableExplorer

# Create an explorer instance
explorer = TableExplorer()

# Load your data (example with pandas)
import pandas as pd
data = pd.read_csv('your_data.csv')

# Analyze structure
structure_info = explorer.analyze_structure(data)
print(structure_info)

# Get column statistics
stats = explorer.get_column_statistics(data)
print(stats)
```

## API Documentation
API documentation will be added as endpoints are developed.

## Development
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
