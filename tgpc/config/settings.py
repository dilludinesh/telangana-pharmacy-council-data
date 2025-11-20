"""Configuration settings for TGPC data extraction system."""

from dataclasses import dataclass
from pathlib import Path


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
    adaptive_pause_minutes: int = 10

    # Storage
    data_directory: str = "data"

    # Logging
    log_level: str = "INFO"
    log_file: str = "tgpc.log"

    # User Agent
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    @classmethod
    def load(cls, config_file: str = None) -> "Config":
        """Load configuration."""
        config = cls()
        Path(config.data_directory).mkdir(parents=True, exist_ok=True)
        return config
