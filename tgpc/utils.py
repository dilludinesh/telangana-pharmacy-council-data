"""
Core utilities for TGPC system.
Combines configuration, logging, and exception handling.
"""

import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# --- Exceptions ---

class TGPCError(Exception):
    """Base exception for all TGPC-related errors."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error

# --- Configuration ---

@dataclass
class Config:
    """Configuration for TGPC system."""
    
    # API Settings
    base_url: str = "https://www.pharmacycouncil.telangana.gov.in"
    timeout: int = 30
    max_retries: int = 3
    
    # Rate Limiting
    min_delay: float = 3.0
    max_delay: float = 8.0
    long_break_after: int = 100
    long_break_duration: int = 60
    
    # Storage
    data_directory: str = "data"
    
    # User Agent
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration."""
        config = cls()
        Path(config.data_directory).mkdir(parents=True, exist_ok=True)
        return config

# --- Logging ---

def setup_logging(name: str = "tgpc") -> logging.Logger:
    """Set up minimal logging."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
    return logger
