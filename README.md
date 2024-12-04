# Unique - Customer Identity Resolution

## Overview
Unique is an open-source platform for customer identity resolution and data integration. The platform helps organizations create a unified view of their customers by identifying and matching customer records across different databases and tables using advanced fuzzy matching techniques.

## The Problem
Organizations often store customer data in different systems and formats:
- CRM systems
- Sales databases
- Support tickets
- Marketing platforms
- Legacy systems

This leads to:
- Duplicate customer records
- Inconsistent customer information
- Difficulty in creating a unified customer view
- Challenges in data analysis and customer insights

## Our Solution
Unique provides a powerful, yet easy-to-use platform that:
1. Connects to different data sources (starting with Amazon Redshift)
2. Identifies potential matching records using intelligent algorithms
3. Provides confidence scores for matches
4. Allows for easy verification and export of results

### How It Works
1. **Smart Column Detection**:
   - Automatically categorizes columns (identity, contact, name)
   - Assigns weights based on reliability of identifiers
   - Supports common patterns in customer data

2. **Fuzzy Matching Engine**:
   - Uses weighted scoring system
   - Handles variations in:
     - Names (order, case, formatting)
     - Emails (domains, formats)
     - Phone numbers (formats, country codes)
   - Configurable similarity thresholds

3. **Scoring System**:
   - Identity fields (SSN, tax ID): 1.0 weight
   - Contact information (email, phone): 0.8 weight
   - Names: 0.6 weight
   - Customizable weights and thresholds

## Getting Started

### Prerequisites
- Python 3.8+
- Access to a Redshift database
- Required Python packages (see requirements.txt)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/andrelsouza/unique.git
cd unique
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables -If you dont want to use the front end to pass the credentials:
```bash
REDSHIFT_HOST=your-host
REDSHIFT_DATABASE=your-database
REDSHIFT_USER=your-username
REDSHIFT_PASSWORD=your-password
REDSHIFT_PORT=5439
```

4. Run the application:
```bash
streamlit run app.py
```

## Contributing

We welcome contributions! Here are some areas where you can help:

### 1. New Data Source Connectors
- Add support for new databases:
  - PostgreSQL
  - MySQL
  - MongoDB
  - Snowflake
  - BigQuery

### 2. Matching Algorithm Improvements
- Implement new matching techniques:
  - Machine learning-based matching
  - Phonetic matching algorithms
  - Address standardization
  - Name parsing and normalization
  - Cultural name variations

### 3. Performance Optimizations
- Batch processing for large datasets
- Parallel processing
- Indexing strategies
- Memory optimization
- Caching mechanisms

### 4. Feature Additions
- Matching rule configuration UI
- Match review and validation interface
- Batch processing interface
- API endpoints
- Custom scoring rules
- Match visualization tools

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

#### Development Guidelines
1. Follow PEP 8 style guide
2. Add docstrings and comments
3. Include unit tests
4. Update documentation
5. Keep commits atomic and descriptive

## Testing
Run the test suite:
```bash
python -m tests.test_matching
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap
- [ ] Additional database connectors
- [ ] Better UI/UX
- [ ] API endpoints
- [ ] Match review interface
- [ ] Batch processing
- [ ] Performance optimizations
- [ ] Visualization tools
- [ ] Custom rules engine
