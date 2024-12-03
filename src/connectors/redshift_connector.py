import psycopg2
import pandas as pd
from typing import List, Dict, Optional

class RedshiftConnector:
    def __init__(self):
        self.connection = None
        
    def connect(self, host: str, database: str, user: str, password: str, port: int = 5439) -> bool:
        """Establish connection to Redshift database"""
        try:
            self.connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redshift: {str(e)}")
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        if not self.connection:
            raise ConnectionError("Not connected to database")
            
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return [table[0] for table in cursor.fetchall()]
    
    def get_columns(self, table_name: str) -> List[Dict[str, str]]:
        """Get column information for specified table"""
        if not self.connection:
            raise ConnectionError("Not connected to database")
            
        query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s
            AND table_schema = 'public'
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, (table_name,))
            return [{"name": col[0], "type": col[1]} for col in cursor.fetchall()]
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close() 