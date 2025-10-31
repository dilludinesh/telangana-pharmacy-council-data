"""
Minimal configuration settings for TGPC data extraction system.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class Config:
    """Minimal configuration class for TGPC system."""
    
    # API Settings
    base_url: str = "https://www.pharmacycouncil.telangana.gov.in"
    timeout: int = 30
    max_retries: int = 3
    
    # Rate Limiting
    min_delay: float = 4.0
    max_delay: float = 10.0
    long_break_after: int = 100
    long_break_duration: int = 60
    adaptive_pause_minutes: int = 10
    
    # Storage
    data_directory: str = "data"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "tgpc.log"
    
    # User Agent
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    @classmethod
    def load(cls, config_file: str = None) -> "Config":
        """Load configuration from environment variables."""
        # Load environment variables
        for env_path in [".env", ".env.local"]:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                break
        
        # Create config with environment overrides
        config = cls()
        
        # Override with environment variables
        if os.getenv("TGPC_BASE_URL"):
            config.base_url = os.getenv("TGPC_BASE_URL")
        if os.getenv("TGPC_TIMEOUT"):
            config.timeout = int(os.getenv("TGPC_TIMEOUT"))
        if os.getenv("TGPC_MIN_DELAY"):
            config.min_delay = float(os.getenv("TGPC_MIN_DELAY"))
        if os.getenv("TGPC_MAX_DELAY"):
            config.max_delay = float(os.getenv("TGPC_MAX_DELAY"))
        if os.getenv("TGPC_DATA_DIRECTORY"):
            config.data_directory = os.getenv("TGPC_DATA_DIRECTORY")
        if os.getenv("TGPC_LOG_LEVEL"):
            config.log_level = os.getenv("TGPC_LOG_LEVEL")
        
        # Ensure data directory exists
        Path(config.data_directory).mkdir(parents=True, exist_ok=True)
        
        return config