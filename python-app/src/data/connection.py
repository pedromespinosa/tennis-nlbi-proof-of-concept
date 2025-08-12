# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 22:21:43 2025

@author: pedro

Database connection management for Tennis Analytics.
"""
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from typing import Optional
from config.settings import settings

class SnowflakeConnection:
    """Manages Snowflake database connections."""
    
    def __init__(self):
        self._connection: Optional[snowflake.connector.SnowflakeConnection] = None
        self._private_key = self._load_private_key()
    
    def _load_private_key(self):
        """Load private key for Snowflake authentication."""
        try:
            with open(settings.SNOWFLAKE_PRIVATE_KEY_PATH, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                )
            return private_key
        except FileNotFoundError:
            raise FileNotFoundError(f"Private key file not found: {settings.SNOWFLAKE_PRIVATE_KEY_PATH}")
        except Exception as e:
            raise Exception(f"Error loading private key: {str(e)}")
    
    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Create and return a Snowflake connection."""
        try:
            print("Attempting Snowflake connection...")
            print(f"Account: {settings.SNOWFLAKE_ACCOUNT}")
            print(f"User: {settings.SNOWFLAKE_USER}")
            print(f"Database: {settings.SNOWFLAKE_DATABASE}")
            print(f"Schema: {settings.SNOWFLAKE_SCHEMA}")
            
            connection = snowflake.connector.connect(
                account=settings.SNOWFLAKE_ACCOUNT,
                user=settings.SNOWFLAKE_USER,
                private_key=self._private_key,
                role=settings.SNOWFLAKE_ROLE,
                warehouse=settings.SNOWFLAKE_WAREHOUSE,
                database=settings.SNOWFLAKE_DATABASE,
                schema=settings.SNOWFLAKE_SCHEMA
            )
            
            print("Snowflake connection successful")
            return connection
            
        except Exception as e:
            print(f"Snowflake connection error: {str(e)}")
            raise Exception(f"Failed to connect to Snowflake: {str(e)}")
    
    def get_cursor(self):
        """Get a cursor for executing queries."""
        connection = self.connect()
        return connection.cursor(), connection
    
    def execute_query(self, query: str, params: list = None):
        """Execute a query and return results."""
        cursor, connection = None, None
        try:
            cursor, connection = self.get_cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Query execution error: {str(e)}")
            raise Exception(f"Query failed: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_query_pandas(self, query: str, params: list = None):
        """Execute a query and return results as pandas DataFrame."""
        cursor, connection = None, None
        try:
            cursor, connection = self.get_cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetch_pandas_all()
            
        except Exception as e:
            print(f"Query execution error: {str(e)}")
            raise Exception(f"Query failed: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Global connection instance
snowflake_db = SnowflakeConnection()
