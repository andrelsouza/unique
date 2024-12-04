# Connectors Documentation

## Overview
The `src/connectors` directory contains the database connector implementations for different data sources. Currently, it includes the Amazon Redshift connector, with plans to support additional data sources in the future.

## RedshiftConnector

### Class Overview
`RedshiftConnector` is a Python class that manages connections to Amazon Redshift databases and provides methods for database interaction.

Location: `src/connectors/redshift_connector.py`

### Dependencies
- `psycopg2`: PostgreSQL database adapter for Python
- `pandas`: Data manipulation library
- `typing`: Type hinting support

### Class Methods

#### `__init__(self)`
Initializes a new RedshiftConnector instance.
- Creates an empty connection attribute
- No parameters required
- Returns: None

#### `connect(self, host: str, database: str, user: str, password: str, port: int = 5439) -> bool`
Establishes a connection to the Redshift database.

Parameters:
- `host`: The hostname of the Redshift cluster
- `database`: The name of the database to connect to
- `user`: Username for authentication
- `password`: Password for authentication
- `port`: Port number (default: 5439)

Returns:
- `bool`: True if connection is successful

Raises:
- `ConnectionError`: If connection fails, with detailed error message

#### `get_tables(self) -> List[str]`
Retrieves a list of all tables in the public schema.

Parameters: None

Returns:
- `List[str]`: List of table names

Raises:
- `ConnectionError`: If not connected to database

Implementation details: 