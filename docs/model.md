# Unique User Identifier Model

## Overview
The Unique User Identifier model is designed to find matching user records across different tables in a database using fuzzy matching techniques. It employs a weighted scoring system based on different types of identifying information.

## Core Components

### ColumnMetadata
A dataclass that stores metadata about database columns:
- `name`: Column name
- `type`: Data type
- `category`: Classification of the column (identity, contact, name, or other)

### UniqueIdentifier
The main class that handles the matching logic.

#### Configuration
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: 85) for considering matches
- `COLUMN_CATEGORIES`: Predefined categories and their weights:
  - Identity (1.0): SSN, tax ID, passport,CPF, etc.
  - Contact (0.8): Email, phone, address
  - Name (0.6): First name, last name, full name

## Matching Process

1. **Column Categorization**
   - Analyzes column names to determine their category
   - Uses predefined patterns to match common identifying fields
   - Assigns weights based on the reliability of the identifier

2. **Value Comparison**
   - Performs exact matching when possible
   - Uses fuzzy matching for text-based fields
   - Handles null values and different data types

3. **Scoring System**
   - Calculates weighted similarity scores
   - Combines multiple field matches
   - Applies threshold filtering

## Usage Example
```python
# Initialize the identifier
identifier = UniqueIdentifier(redshift_connector)

# Find matching users
matches = identifier.find_unique_users(
    schema1="public", 
    table1="customers",
    columns1=["email", "full_name", "phone"],
    schema2="sales",
    table2="users",
    columns2=["user_email", "name", "contact_number"]
)
```

## Performance Considerations

1. **Memory Usage**
   - Loads entire tables into memory
   - Consider chunking for large datasets

2. **Processing Time**
   - O(n*m) complexity where n and m are table sizes
   - Optimized for small to medium-sized datasets

## Future Improvements

1. **Optimization**
   - Implement batch processing
   - Add indexing for faster matching
   - Parallel processing support

2. **Features**
   - Additional matching algorithms
   - Custom category definitions
   - Machine learning-based matching
   - Support for more data types

3. **Integration**
   - API endpoints
   - Batch processing jobs
   - Real-time matching 