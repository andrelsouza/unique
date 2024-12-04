from thefuzz import fuzz
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class ColumnMetadata:
    name: str
    type: str
    category: str  # identity, contact, or other

class UniqueIdentifier:
    # Threshold for fuzzy matching (can be adjusted)
    SIMILARITY_THRESHOLD = 85
    
    # Define column categories and their weights
    COLUMN_CATEGORIES = {
        'identity': {
            'patterns': [
                'ssn', 'social_security', 'tax_id', 'document', 'cpf', 'identity',
                'passport', 'id_number', 'national_id'
            ],
            'weight': 1.0
        },
        'contact': {
            'patterns': [
                'email', 'phone', 'mobile', 'telephone', 'contact_number',
                'address', 'postal_code', 'zip_code'
            ],
            'weight': 0.8
        },
        'name': {
            'patterns': [
                'name', 'first_name', 'last_name', 'full_name',
                'customer_name', 'client_name'
            ],
            'weight': 0.6
        }
    }
    
    def __init__(self, redshift_connector):
        self.connector = redshift_connector
        
    def categorize_column(self, column_name: str) -> str:
        """Categorize column based on its name"""
        column_name = column_name.lower()
        
        for category, info in self.COLUMN_CATEGORIES.items():
            if any(pattern in column_name for pattern in info['patterns']):
                return category
        return 'other'
    
    def get_column_weight(self, category: str) -> float:
        """Get weight for column category"""
        return self.COLUMN_CATEGORIES.get(category, {'weight': 0.2})['weight']
    
    def compare_values(self, val1, val2, column_type: str) -> float:
        """Compare two values using appropriate comparison method"""
        if pd.isna(val1) or pd.isna(val2):
            return 0.0
            
        val1, val2 = str(val1).lower(), str(val2).lower()
        
        # Direct comparison for exact matches
        if val1 == val2:
            return 100.0
            
        # Fuzzy matching for text values
        return fuzz.ratio(val1, val2)
    
    def find_unique_users(self, schema1: str, table1: str, columns1: List[str],
                         schema2: str, table2: str, columns2: List[str]) -> pd.DataFrame:
        """Find unique users across two tables"""
        # Fetch data from both tables
        query1 = f"SELECT {', '.join(columns1)} FROM {schema1}.{table1}"
        query2 = f"SELECT {', '.join(columns2)} FROM {schema2}.{table2}"
        
        with self.connector.connection.cursor() as cursor:
            # Fetch data from first table
            cursor.execute(query1)
            data1 = cursor.fetchall()
            df1 = pd.DataFrame(data1, columns=columns1)
            
            # Fetch data from second table
            cursor.execute(query2)
            data2 = cursor.fetchall()
            df2 = pd.DataFrame(data2, columns=columns2)
        
        # Get column metadata
        columns1_meta = [ColumnMetadata(
            name=col,
            type=next(c["type"] for c in self.connector.get_columns(schema1, table1) if c["name"] == col),
            category=self.categorize_column(col)
        ) for col in columns1]
        
        columns2_meta = [ColumnMetadata(
            name=col,
            type=next(c["type"] for c in self.connector.get_columns(schema2, table2) if c["name"] == col),
            category=self.categorize_column(col)
        ) for col in columns2]
        
        # Results storage
        matches = []
        
        # Compare records
        for idx1, row1 in df1.iterrows():
            for idx2, row2 in df2.iterrows():
                total_weight = 0
                weighted_similarity = 0
                
                # Compare each column pair
                for col1 in columns1_meta:
                    for col2 in columns2_meta:
                        if col1.category == col2.category and col1.category != 'other':
                            weight = self.get_column_weight(col1.category)
                            similarity = self.compare_values(row1[col1.name], row2[col2.name], col1.type)
                            
                            if similarity >= self.SIMILARITY_THRESHOLD:
                                weighted_similarity += similarity * weight
                                total_weight += weight
                
                # Calculate final similarity score
                if total_weight > 0:
                    final_score = weighted_similarity / total_weight
                    if final_score >= self.SIMILARITY_THRESHOLD:
                        matches.append({
                            'table1_id': idx1,
                            'table2_id': idx2,
                            'similarity_score': final_score,
                            **{f"table1_{col}": row1[col] for col in columns1},
                            **{f"table2_{col}": row2[col] for col in columns2}
                        })
        
        return pd.DataFrame(matches) 