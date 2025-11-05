"""
Data models for pharmacist records.

This module defines the core data structures used throughout the TGPC system
for representing pharmacist information with proper validation and serialization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import json
import re

from tgpc.core.exceptions import DataValidationException


@dataclass
class EducationRecord:
    """Represents an education record for a pharmacist."""
    
    qualification: str = ""
    board_university: str = ""
    college_name: str = ""
    college_address: str = ""
    academic_year_from: str = ""
    academic_year_to: str = ""
    hallticket_no: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "qualification": self.qualification,
            "board_university": self.board_university,
            "college_name": self.college_name,
            "college_address": self.college_address,
            "academic_year_from": self.academic_year_from,
            "academic_year_to": self.academic_year_to,
            "hallticket_no": self.hallticket_no
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EducationRecord":
        """Create from dictionary."""
        return cls(
            qualification=data.get("qualification", ""),
            board_university=data.get("board_university", ""),
            college_name=data.get("college_name", ""),
            college_address=data.get("college_address", ""),
            academic_year_from=data.get("academic_year_from", ""),
            academic_year_to=data.get("academic_year_to", ""),
            hallticket_no=data.get("hallticket_no", "")
        )


@dataclass
class WorkExperience:
    """Represents work experience information for a pharmacist."""
    
    address: str = ""
    state: str = ""
    district: str = ""
    pincode: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "address": self.address,
            "state": self.state,
            "district": self.district,
            "pincode": self.pincode
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkExperience":
        """Create from dictionary."""
        return cls(
            address=data.get("address", ""),
            state=data.get("state", ""),
            district=data.get("district", ""),
            pincode=data.get("pincode", "")
        )


@dataclass
class PharmacistRecord:
    """
    Represents a complete pharmacist record with all available information.
    
    This class handles both basic and detailed pharmacist information,
    providing validation, serialization, and data quality checks.
    """
    
    # Basic Information (always available)
    registration_number: str
    name: str
    father_name: str
    category: str
    
    # Extended Information (may be available)
    serial_number: Optional[Union[int, str]] = None
    registration_date: Optional[datetime] = None
    validity_date: Optional[datetime] = None
    status: str = ""
    gender: str = ""
    photo_data: Optional[str] = None
    
    # Education and Work
    education: List[EducationRecord] = field(default_factory=list)
    work_experience: Optional[WorkExperience] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    data_source: str = "tgpc_website"
    
    def __post_init__(self):
        """Post-initialization validation and cleanup."""
        # Clean and validate registration number
        self.registration_number = self._clean_registration_number(self.registration_number)
        
        # Clean names
        self.name = self._clean_name(self.name)
        self.father_name = self._clean_name(self.father_name)
        
        # Validate category
        self.category = self._clean_category(self.category)
        
        # Update timestamp
        self.updated_at = datetime.now()
    
    @staticmethod
    def _clean_registration_number(reg_no: str) -> str:
        """Clean and validate registration number."""
        if not reg_no:
            raise DataValidationException("Registration number is required")
        
        # Remove extra whitespace
        reg_no = reg_no.strip()
        
        # Validate format (should start with TS or TG)
        if not re.match(r'^(TS|TG)[A-Z]*\d+$', reg_no, re.IGNORECASE):
            # Try to fix common issues
            if reg_no.isdigit():
                reg_no = f"TS{reg_no.zfill(6)}"
            elif not reg_no.startswith(('TS', 'TG')):
                raise DataValidationException(f"Invalid registration number format: {reg_no}")
        
        return reg_no.upper()
    
    @staticmethod
    def _clean_name(name: str) -> str:
        """Clean and validate name fields."""
        if not name:
            return ""
        
        # Remove extra whitespace and normalize
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Capitalize properly
        return name.title()
    
    @staticmethod
    def _clean_category(category: str) -> str:
        """Clean and validate pharmacist category."""
        if not category:
            return ""
        
        category = category.strip().upper()
        
        # Normalize common variations
        category_mapping = {
            'BPHARM': 'BPharm',
            'B.PHARM': 'BPharm',
            'B PHARM': 'BPharm',
            'DPHARM': 'DPharm',
            'D.PHARM': 'DPharm',
            'D PHARM': 'DPharm',
            'PHARMD': 'PharmD',
            'PHARM.D': 'PharmD',
            'PHARM D': 'PharmD',
            'MPHARM': 'MPharm',
            'M.PHARM': 'MPharm',
            'M PHARM': 'MPharm',
            'QP': 'QP',
            'QC': 'QC'
        }
        
        return category_mapping.get(category, category)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "registration_number": self.registration_number,
            "name": self.name,
            "father_name": self.father_name,
            "category": self.category,
            "serial_number": self.serial_number,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "validity_date": self.validity_date.isoformat() if self.validity_date else None,
            "status": self.status,
            "gender": self.gender,
            "photo_data": self.photo_data,
            "education": [edu.to_dict() for edu in self.education],
            "work_experience": self.work_experience.to_dict() if self.work_experience else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "data_source": self.data_source
        }
    
    def to_basic_dict(self) -> Dict[str, Any]:
        """Convert record to basic dictionary with only Total Records fields."""
        return {
            "serial_number": self.serial_number,
            "registration_number": self.registration_number,
            "name": self.name,
            "father_name": self.father_name,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PharmacistRecord":
        """Create record from dictionary."""
        # Parse dates
        registration_date = None
        if data.get("registration_date"):
            try:
                registration_date = datetime.fromisoformat(data["registration_date"])
            except ValueError:
                pass
        
        validity_date = None
        if data.get("validity_date"):
            try:
                validity_date = datetime.fromisoformat(data["validity_date"])
            except ValueError:
                pass
        
        created_at = datetime.now()
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except ValueError:
                pass
        
        updated_at = datetime.now()
        if data.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except ValueError:
                pass
        
        # Parse education records
        education = []
        if data.get("education"):
            for edu_data in data["education"]:
                education.append(EducationRecord.from_dict(edu_data))
        
        # Parse work experience
        work_experience = None
        if data.get("work_experience"):
            work_experience = WorkExperience.from_dict(data["work_experience"])
        
        return cls(
            registration_number=data.get("registration_number", ""),
            name=data.get("name", ""),
            father_name=data.get("father_name", ""),
            category=data.get("category", ""),
            serial_number=data.get("serial_number"),
            registration_date=registration_date,
            validity_date=validity_date,
            status=data.get("status", ""),
            gender=data.get("gender", ""),
            photo_data=data.get("photo_data"),
            education=education,
            work_experience=work_experience,
            created_at=created_at,
            updated_at=updated_at,
            data_source=data.get("data_source", "tgpc_website")
        )
    
    @classmethod
    def from_basic_dict(cls, data: Dict[str, Any]) -> "PharmacistRecord":
        """Create record from basic dictionary (legacy format)."""
        return cls(
            registration_number=data.get("registration_number", ""),
            name=data.get("name", ""),
            father_name=data.get("father_name", ""),
            category=data.get("category", ""),
            serial_number=data.get("serial_number")
        )
    
    def to_json(self) -> str:
        """Convert record to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "PharmacistRecord":
        """Create record from JSON string."""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise DataValidationException(f"Invalid JSON format: {e}")
    
    def is_basic_record(self) -> bool:
        """Check if this is a basic record (minimal information)."""
        return (
            not self.education and
            not self.work_experience and
            not self.photo_data and
            not self.registration_date
        )
    
    def is_detailed_record(self) -> bool:
        """Check if this is a detailed record (comprehensive information)."""
        return not self.is_basic_record()
    
    def get_data_quality_score(self) -> float:
        """
        Calculate a data quality score (0.0 to 1.0) based on completeness.
        
        Returns:
            Float between 0.0 and 1.0 indicating data completeness.
        """
        score = 0.0
        total_fields = 0
        
        # Required fields (weight: 0.4)
        required_fields = [self.registration_number, self.name, self.father_name, self.category]
        filled_required = sum(1 for field in required_fields if field and field.strip())
        score += (filled_required / len(required_fields)) * 0.4
        
        # Optional basic fields (weight: 0.3)
        optional_basic = [self.status, self.gender]
        filled_optional_basic = sum(1 for field in optional_basic if field and field.strip())
        if optional_basic:
            score += (filled_optional_basic / len(optional_basic)) * 0.3
        
        # Education information (weight: 0.2)
        if self.education:
            edu_completeness = sum(
                len([f for f in [edu.qualification, edu.board_university, edu.college_name] if f])
                for edu in self.education
            ) / (len(self.education) * 3)
            score += edu_completeness * 0.2
        
        # Additional information (weight: 0.1)
        additional_info = [self.photo_data, self.work_experience]
        filled_additional = sum(1 for field in additional_info if field)
        if additional_info:
            score += (filled_additional / len(additional_info)) * 0.1
        
        return min(score, 1.0)
    
    def validate(self) -> List[str]:
        """
        Validate the record and return list of validation errors.
        
        Returns:
            List of validation error messages.
        """
        errors = []
        
        # Required field validation
        if not self.registration_number or not self.registration_number.strip():
            errors.append("Registration number is required")
        
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        
        if not self.category or not self.category.strip():
            errors.append("Category is required")
        
        # Format validation
        if self.registration_number:
            try:
                self._clean_registration_number(self.registration_number)
            except DataValidationException as e:
                errors.append(str(e))
        
        # Category validation
        valid_categories = ['BPharm', 'DPharm', 'PharmD', 'MPharm', 'QP', 'QC']
        if self.category and self.category not in valid_categories:
            errors.append(f"Invalid category: {self.category}. Must be one of {valid_categories}")
        
        return errors
    
    def __str__(self) -> str:
        """String representation of the record."""
        return f"PharmacistRecord({self.registration_number}: {self.name})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"PharmacistRecord(registration_number='{self.registration_number}', "
            f"name='{self.name}', category='{self.category}')"
        )