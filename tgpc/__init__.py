"""
TGPC Data Extraction System - Minimal Version

A minimal system for extracting pharmacist registration data from the TGPC website.
"""

__version__ = "2.0.0"

from tgpc.core.engine import TGPCEngine
from tgpc.models.pharmacist import PharmacistRecord
from tgpc.config.settings import Config

__all__ = ["TGPCEngine", "PharmacistRecord", "Config"]