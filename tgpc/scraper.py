"""
Core scraping logic for TGPC system.
Handles data extraction, rate limiting, and parsing.
"""

import time
import random
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from tgpc.utils import Config, TGPCError, setup_logging

logger = setup_logging("tgpc.scraper")

# --- Models ---

@dataclass
class PharmacistRecord:
    """Pharmacist record data model."""
    registration_number: str
    name: str
    father_name: str
    category: str
    serial_number: Optional[int] = None
    status: str = ""
    gender: str = ""
    validity_date: Optional[datetime] = None
    photo_data: Optional[str] = None
    education: List[Dict[str, str]] = None
    work_experience: Dict[str, str] = None

    def to_dict(self):
        data = asdict(self)
        if self.validity_date:
            data['validity_date'] = self.validity_date.isoformat()
        return data

# --- Rate Limiter ---

class RateLimiter:
    """Simple adaptive rate limiter."""
    
    def __init__(self, config: Config):
        self.min_delay = config.min_delay
        self.max_delay = config.max_delay
        self.current_delay = config.min_delay
        self.consecutive_failures = 0

    def wait(self):
        """Wait for the calculated delay."""
        delay = self.current_delay * random.uniform(0.8, 1.2)
        time.sleep(delay)

    def record_result(self, success: bool):
        """Adjust delay based on success/failure."""
        if success:
            self.consecutive_failures = 0
            self.current_delay = max(self.min_delay, self.current_delay * 0.9)
        else:
            self.consecutive_failures += 1
            self.current_delay = min(self.max_delay, self.current_delay * 1.5)

# --- Scraper ---

class Scraper:
    """Main scraper class."""

    def __init__(self):
        self.config = Config.load()
        self.rate_limiter = RateLimiter(self.config)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.config.user_agent})
        
        self.urls = {
            'total': f"{self.config.base_url}/pharmacy/srchpharmacisttotal",
            'search': f"{self.config.base_url}/pharmacy/getsearchpharmacist"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry and rate limiting."""
        self.rate_limiter.wait()
        try:
            response = self.session.request(method, url, timeout=self.config.timeout, **kwargs)
            response.raise_for_status()
            self.rate_limiter.record_result(True)
            return response
        except Exception as e:
            self.rate_limiter.record_result(False)
            raise TGPCError(f"Request failed: {url}", e)

    def get_total_count(self) -> int:
        """Get total number of pharmacists."""
        try:
            response = self._request("GET", self.urls['total'])
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find table
            table = soup.find('table', attrs={'id': 'tablesorter-demo'})
            if not table:
                tables = soup.find_all('table')
                if not tables:
                    raise TGPCError("No tables found")
                table = tables[0]

            # Count rows
            rows = [r for r in table.find_all('tr') if r.find_all('td')]
            
            # Try to extract serial numbers for better accuracy
            serials = []
            for row in rows:
                try:
                    serials.append(int(row.find_all('td')[0].get_text(strip=True)))
                except (ValueError, IndexError):
                    pass
            
            count = len(set(serials)) if serials else len(rows)
            logger.info(f"Total count: {count}")
            return count
            
        except Exception as e:
            raise TGPCError("Failed to get total count", e)

    def extract_basic_records(self) -> List[PharmacistRecord]:
        """Extract all basic records."""
        logger.info("Extracting basic records...")
        response = self._request("GET", self.urls['total'])
        soup = BeautifulSoup(response.content, 'html.parser')
        
        records = []
        table = soup.find('table', attrs={'id': 'tablesorter-demo'}) or soup.find('table')
        
        if not table:
            return []

        for row in table.find_all('tr')[1:]: # Skip header
            cells = row.find_all('td')
            if len(cells) < 5:
                continue
                
            try:
                records.append(PharmacistRecord(
                    serial_number=int(cells[0].get_text(strip=True)) if cells[0].get_text(strip=True).isdigit() else None,
                    registration_number=cells[1].get_text(strip=True),
                    name=cells[2].get_text(strip=True),
                    father_name=cells[3].get_text(strip=True),
                    category=cells[4].get_text(strip=True)
                ))
            except Exception:
                continue
                
        logger.info(f"Extracted {len(records)} records")
        return records

    def extract_detailed_info(self, reg_no: str) -> Optional[PharmacistRecord]:
        """Extract detailed info for a single pharmacist."""
        try:
            response = self._request("POST", self.urls['search'], data={
                'registration_no': reg_no,
                'submit': 'Submit'
            })
            
            if 'No Records Found' in response.text:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            
            if not tables:
                return None

            # Parse main info
            data = {'registration_number': reg_no}
            main_rows = tables[0].find_all('tr')
            if len(main_rows) >= 2:
                headers = [th.get_text(strip=True).lower() for th in main_rows[0].find_all(['th', 'td'])]
                cells = main_rows[1].find_all('td')
                
                for i, header in enumerate(headers):
                    if i >= len(cells): break
                    val = cells[i].get_text(strip=True)
                    
                    if 'name' in header and 'father' not in header: data['name'] = val
                    elif 'father' in header: data['father_name'] = val
                    elif 'category' in header: data['category'] = val
                    elif 'status' in header: data['status'] = val
                    elif 'gender' in header: data['gender'] = val
                    elif 'validity' in header: 
                        try:
                            data['validity_date'] = datetime.strptime(val, '%d-%b-%Y')
                        except: pass

            return PharmacistRecord(**data)

        except Exception as e:
            logger.error(f"Failed to extract details for {reg_no}: {e}")
            return None
