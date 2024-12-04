import os
import sys
import random
from faker import Faker
import psycopg2
from dotenv import load_dotenv
from src.model.model_run import UniqueIdentifier
from src.connectors.redshift_connector import RedshiftConnector


### The main goal of this script is to test the matching algorithm with a small dataset created in Database
### Tested by: Andre Souza
### Date: 2024-12-01


# Initialize Faker for generating realistic test data
fake = Faker()

def create_test_schema(cursor):
    """Create test schema and tables"""
    # Create schema
    cursor.execute("DROP SCHEMA IF EXISTS unique_test CASCADE")
    cursor.execute("CREATE SCHEMA unique_test")
    
    # Create first table (customers)
    cursor.execute("""
        CREATE TABLE unique_test.customers (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255),
            full_name VARCHAR(255),
            phone VARCHAR(20)
        )
    """)
    
    # Create second table (users)
    cursor.execute("""
        CREATE TABLE unique_test.users (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255),
            name VARCHAR(255),
            contact_number VARCHAR(20)
        )
    """)

def generate_phone():
    """Generate a random phone number"""
    return f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def create_matching_record():
    """Create a record that will appear in both tables with slight variations"""
    email = fake.email()
    name = fake.name()
    phone = generate_phone()
    
    # Create variations for the second table
    variations = {
        'email': [
            email,  # Exact match
            email.replace('@', '.at.'),  # Modified format
            email.split('@')[0] + '@' + fake.domain_name(),  # Different domain
        ],
        'name': [
            name,  # Exact match
            name.upper(),  # All caps
            ' '.join(reversed(name.split())),  # Reversed first/last name
            name.replace(' ', ''),  # No spaces
        ],
        'phone': [
            phone,  # Exact match
            phone.replace('-', ''),  # No dashes
            phone.replace('+1-', ''),  # No country code
        ]
    }
    
    return {
        'original': (email, name, phone),
        'variations': (
            random.choice(variations['email']),
            random.choice(variations['name']),
            random.choice(variations['phone'])
        )
    }

def populate_test_data(cursor, num_records=100, match_percentage=0.7):
    """Populate tables with test data, ensuring some matching records"""
    num_matching = int(num_records * match_percentage)
    num_unique = num_records - num_matching
    
    # Generate matching records
    matching_records = [create_matching_record() for _ in range(num_matching)]
    
    # Insert matching records into first table
    for record in matching_records:
        cursor.execute("""
            INSERT INTO unique_test.customers (email, full_name, phone)
            VALUES (%s, %s, %s)
        """, record['original'])
    
    # Insert matching records into second table with variations
    for record in matching_records:
        cursor.execute("""
            INSERT INTO unique_test.users (user_email, name, contact_number)
            VALUES (%s, %s, %s)
        """, record['variations'])
    
    # Add some unique records to both tables
    for _ in range(num_unique):
        # Unique records for customers
        cursor.execute("""
            INSERT INTO unique_test.customers (email, full_name, phone)
            VALUES (%s, %s, %s)
        """, (fake.email(), fake.name(), generate_phone()))
        
        # Unique records for users
        cursor.execute("""
            INSERT INTO unique_test.users (user_email, name, contact_number)
            VALUES (%s, %s, %s)
        """, (fake.email(), fake.name(), generate_phone()))

def main():
    """Main test function"""
    # Load environment variables
    load_dotenv()
    
    # Get database connection details from environment variables
    db_params = {
        'host': os.getenv('REDSHIFT_HOST'),
        'database': os.getenv('REDSHIFT_DATABASE'),
        'user': os.getenv('REDSHIFT_USER'),
        'password': os.getenv('REDSHIFT_PASSWORD'),
        'port': int(os.getenv('REDSHIFT_PORT', '5439'))
    }
    
    try:
        # Connect to database
        print("Connecting to database...")
        connector = RedshiftConnector()
        connector.connect(**db_params)
        
        with connector.connection.cursor() as cursor:
            # Create test schema and tables
            print("Creating test schema and tables...")
            create_test_schema(cursor)
            
            # Populate test data
            print("Populating test data...")
            populate_test_data(cursor)
            
            # Commit the changes
            connector.connection.commit()
        
        # Initialize the unique identifier
        unique_identifier = UniqueIdentifier(connector)
        
        # Run the matching algorithm
        print("Running matching algorithm...")
        results = unique_identifier.find_unique_users(
            schema1="unique_test",
            table1="customers",
            columns1=["email", "full_name", "phone"],
            schema2="unique_test",
            table2="users",
            columns2=["user_email", "name", "contact_number"]
        )
        
        # Print results
        print("\nMatching Results:")
        print(f"Total records processed: 100 in each table")
        print(f"Matches found: {len(results)}")
        if not results.empty:
            print("\nSample matches:")
            print(results.head())
            print("\nMatching statistics:")
            print(f"Average similarity score: {results['similarity_score'].mean():.2f}%")
            print(f"Minimum similarity score: {results['similarity_score'].min():.2f}%")
            print(f"Maximum similarity score: {results['similarity_score'].max():.2f}%")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if connector:
            connector.close()

if __name__ == "__main__":
    main() 