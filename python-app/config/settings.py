# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 22:22:25 2025

@author: pedro

Configuration settings for the Tennis Analytics application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="MyKeys.env")

class Settings:
    """Application configuration settings."""
    
    # Anthropic API settings
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    ANTHROPIC_MAX_TOKENS = 1024
    ANTHROPIC_TEMPERATURE = 0.1
    
    # Snowflake connection settings
    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")
    SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
    SNOWFLAKE_PRIVATE_KEY_PATH = "rsa_key.p8"
    
    # Application settings
    DEFAULT_PLAYER_LIMIT = 20
    MAX_SEARCH_RESULTS = 25
    
    @classmethod
    def validate(cls):
        """Validate that required environment variables are set."""
        required_vars = [
            'ANTHROPIC_API_KEY',
            'SNOWFLAKE_ACCOUNT',
            'SNOWFLAKE_USER',
            'SNOWFLAKE_DATABASE',
            'SNOWFLAKE_SCHEMA'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Global settings instance
settings = Settings()
