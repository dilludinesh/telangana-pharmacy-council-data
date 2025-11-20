"""
Pharmacist data extractor for TGPC system.

This module provides the main data extraction functionality with
robust error handling, rate limiting, and data validation.
"""

import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from tgpc.config.settings import Config
from tgpc.core.exceptions import (
    ExtractionException,
    NetworkException,
    ParsingException,
    create_http_exception,
)
from tgpc.extractors.rate_limiter import RateLimiter
from tgpc.models.pharmacist import EducationRecord, PharmacistRecord, WorkExperience
from tgpc.utils.logger import get_logger


class PharmacistExtractor:
    """
    Main extractor for pharmacist data from TGPC website.

    This class handles both basic and detailed data extraction with
    intelligent rate limiting, error recovery, and data validation.
    """

    def __init__(self, config: Config):
        """
        Initialize the pharmacist extractor.

        Args:
            config: Configuration object with extraction settings.
        """
        self.config = config
        self.logger = get_logger(__name__)

        # Initialize session with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        })

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(config)

        # URLs
        self.base_url = config.base_url
        self.total_url = f"{self.base_url}/pharmacy/srchpharmacisttotal"
        self.search_url = f"{self.base_url}/pharmacy/getsearchpharmacist"

        self.logger.info(
            "Pharmacist extractor initialized",
            extra={
                "base_url": self.base_url,
                "timeout": config.timeout,
                "max_retries": config.max_retries
            }
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, NetworkException))
    )
    def _make_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with retry logic and rate limiting.

        Args:
            url: URL to request.
            method: HTTP method (GET, POST).
            data: Optional form data for POST requests.
            **kwargs: Additional arguments for requests.

        Returns:
            Response object.

        Raises:
            NetworkException: If request fails after retries.
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        start_time = time.time()

        try:
            # Make the request
            if method.upper() == "POST":
                response = self.session.post(
                    url,
                    data=data,
                    timeout=self.config.timeout,
                    **kwargs
                )
            else:
                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    **kwargs
                )

            # Calculate response time
            response_time = time.time() - start_time

            # Record request statistics
            self.rate_limiter.record_request(
                response_time=response_time,
                status_code=response.status_code,
                success=response.status_code < 400
            )

            # Handle HTTP errors
            if response.status_code >= 400:
                raise create_http_exception(
                    status_code=response.status_code,
                    message=f"HTTP {response.status_code} error for {url}",
                    url=url
                )

            self.logger.debug(
                "Request successful",
                extra={
                    "url": url,
                    "method": method,
                    "status_code": response.status_code,
                    "response_time": response_time
                }
            )

            return response

        except requests.exceptions.Timeout as e:
            self.rate_limiter.record_request(0, 0, False)
            raise NetworkException(
                f"Request timeout for {url}",
                error_code="TIMEOUT",
                url=url,
                cause=e
            )
        except requests.exceptions.ConnectionError as e:
            self.rate_limiter.record_request(0, 0, False)
            raise NetworkException(
                f"Connection error for {url}",
                error_code="CONNECTION_ERROR",
                url=url,
                cause=e
            )
        except requests.exceptions.RequestException as e:
            self.rate_limiter.record_request(0, 0, False)
            raise NetworkException(
                f"Request failed for {url}: {str(e)}",
                error_code="REQUEST_ERROR",
                url=url,
                cause=e
            )

    def extract_total_count(self) -> int:
        """
        Extract the total count of pharmacists from TGPC website.

        Returns:
            Total number of registered pharmacists.

        Raises:
            NetworkException: If unable to fetch data.
            ParsingException: If unable to parse the response.
        """
        # Extract total count
        self.logger.info("Fetching total pharmacist count")

        try:
            response = self._make_request(self.total_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the pharmacists table
            table = soup.find('table', attrs={'id': 'tablesorter-demo'})
            if not table:
                # Fallback to first table
                tables = soup.find_all('table')
                table = tables[0] if tables else None

            if not table:
                raise ParsingException(
                    "Could not locate pharmacists table on the page",
                    data_format="html",
                    parse_location="table search"
                )

            # Count data rows
            data_rows = [row for row in table.find_all('tr') if row.find_all('td')]

            if not data_rows:
                raise ParsingException(
                    "No pharmacist rows found in table",
                    data_format="html",
                    parse_location="table rows"
                )

            # Extract serial numbers for accurate count
            serial_numbers = []
            for row in data_rows:
                first_col = row.find_all('td')[0].get_text(strip=True)
                if first_col.isdigit():
                    serial_numbers.append(int(first_col))

            if serial_numbers:
                unique_count = len(set(serial_numbers))
                self.logger.info(f"Total count extracted: {unique_count}")
                return unique_count

            # Fallback to row count
            count = len(data_rows)
            self.logger.info(f"Total count (row count): {count}")
            return count

        except (NetworkException, ParsingException):
            raise
        except Exception as e:
            raise ExtractionException(
                f"Failed to extract total count: {str(e)}",
                extraction_type="total_count",
                cause=e
            )

    def extract_basic_records(self) -> List[PharmacistRecord]:
        """
        Extract basic pharmacist records from TGPC website.

        Returns:
            List of basic pharmacist records.

        Raises:
            NetworkException: If unable to fetch data.
            ParsingException: If unable to parse the response.
        """
        # Extract basic records
        self.logger.info("Extracting basic pharmacist records")

        try:
            response = self._make_request(self.total_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the pharmacists table
            table = soup.find('table', attrs={'id': 'tablesorter-demo'})
            if not table:
                tables = soup.find_all('table')
                table = tables[0] if tables else None

            if not table:
                raise ParsingException(
                    "Could not locate pharmacists table",
                    data_format="html",
                    parse_location="table search"
                )

            records = self._parse_basic_table(table)

            self.logger.info(
                f"Basic records extraction completed: {len(records)} records"
            )

            return records

        except (NetworkException, ParsingException):
            raise
        except Exception as e:
            raise ExtractionException(
                f"Failed to extract basic records: {str(e)}",
                extraction_type="basic_records",
                cause=e
            )

    def _parse_basic_table(self, table) -> List[PharmacistRecord]:
        """Parse basic pharmacist data from HTML table."""
        records = []
        rows = table.find_all('tr')

        if not rows:
            return records

        # Skip header row
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) < 5:
                continue

            try:
                serial_text = cells[0].get_text(strip=True)
                reg_no = cells[1].get_text(strip=True)
                name = cells[2].get_text(strip=True)
                father_name = cells[3].get_text(strip=True)
                category = cells[4].get_text(strip=True)

                # Create record
                record = PharmacistRecord(
                    serial_number=int(serial_text) if serial_text.isdigit() else serial_text,
                    registration_number=reg_no,
                    name=name,
                    father_name=father_name,
                    category=category
                )

                records.append(record)

            except Exception as e:
                self.logger.warning(
                    "Failed to parse table row",
                    extra={
                        "row_data": [cell.get_text(strip=True) for cell in cells],
                        "error": str(e)
                    }
                )

        return records

    def extract_detailed_info(self, registration_number: str) -> Optional[PharmacistRecord]:
        """
        Extract detailed information for a single registration number.

        Args:
            registration_number: Registration number to extract.

        Returns:
            Detailed pharmacist record or None if not found.

        Raises:
            NetworkException: If unable to fetch data.
            ParsingException: If unable to parse the response.
        """
        # Extract detailed info
        self.logger.debug(f"Extracting detailed info for {registration_number}")

        try:
            # Prepare form data
            form_data = {
                'registration_no': registration_number,
                'app_name': '',
                'father_name': '',
                'dob': '',
                'submit': 'Submit'
            }

            response = self._make_request(
                self.search_url,
                method="POST",
                data=form_data
            )

            # Check for "No Records Found" message
            if 'No Records Found' in response.text or 'No records found' in response.text:
                self.logger.debug(f"No records found for {registration_number}")
                return None

            # Parse the response
            record = self._parse_detailed_response(response.text, registration_number)

            if record:
                self.logger.debug(f"Successfully extracted detailed info for {registration_number}")
            else:
                self.logger.warning(f"Could not parse detailed info for {registration_number}")

            return record

        except (NetworkException, ParsingException):
            raise
        except Exception as e:
            raise ExtractionException(
                f"Failed to extract detailed info for {registration_number}: {str(e)}",
                extraction_type="detailed_info",
                registration_number=registration_number,
                cause=e
            )

    def _parse_detailed_response(self, html_content: str, registration_number: str) -> Optional[PharmacistRecord]:
        """Parse detailed pharmacist information from HTML response."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tables = soup.find_all('table')

            if not tables:
                return None

            # Initialize record with registration number
            record_data = {
                'registration_number': registration_number,
                'name': '',
                'father_name': '',
                'category': '',
                'status': '',
                'gender': '',
                'validity': '',
                'photo_data': None,
                'education': [],
                'work_experience': None
            }

            # Parse main pharmacist info table (first table)
            if len(tables) >= 1:
                self._parse_main_info_table(tables[0], record_data)

            # Parse education table (second table)
            if len(tables) >= 2:
                self._parse_education_table(tables[1], record_data)

            # Parse work/study info table (third table)
            if len(tables) >= 3:
                self._parse_work_info_table(tables[2], record_data)

            # Parse validity date if present
            validity_date = None
            if record_data['validity']:
                try:
                    # Parse date format like "31-Dec-2022"
                    validity_date = datetime.strptime(record_data['validity'], '%d-%b-%Y')
                except ValueError:
                    # If parsing fails, keep as None
                    pass

            # Create PharmacistRecord object
            record = PharmacistRecord(
                registration_number=record_data['registration_number'],
                name=record_data['name'],
                father_name=record_data['father_name'],
                category=record_data['category'],
                status=record_data['status'],
                gender=record_data['gender'],
                validity_date=validity_date,
                photo_data=record_data['photo_data'],
                education=record_data['education'],
                work_experience=record_data['work_experience']
            )

            return record

        except Exception as e:
            raise ParsingException(
                f"Failed to parse detailed response for {registration_number}",
                data_format="html",
                parse_location="detailed_response",
                registration_number=registration_number,
                cause=e
            )

    def _parse_main_info_table(self, table, record_data: Dict[str, Any]) -> None:
        """Parse main pharmacist information table."""
        rows = table.find_all('tr')

        if len(rows) >= 2:  # Header + data row
            header_row = rows[0]
            data_row = rows[1]

            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            cells = data_row.find_all('td')

            for i, header in enumerate(headers):
                if i >= len(cells):
                    break

                cell = cells[i]
                value = cell.get_text(strip=True)

                # Map headers to record fields
                header_lower = header.lower()

                if 'name' in header_lower and 'father' not in header_lower:
                    record_data['name'] = value
                elif 'father' in header_lower or 'husband' in header_lower:
                    record_data['father_name'] = value
                elif 'category' in header_lower or 'qualification' in header_lower:
                    record_data['category'] = value
                elif 'status' in header_lower:
                    record_data['status'] = value
                elif 'gender' in header_lower or 'sex' in header_lower:
                    record_data['gender'] = value
                elif 'validity' in header_lower:
                    record_data['validity'] = value
                elif 'photo' in header_lower or i == len(headers) - 1:
                    # Photo is typically in the last column
                    photo_img = cell.find('img')
                    if photo_img:
                        src = photo_img.get('src', '')
                        if src and ('data:image' in src or re.search(r'[a-zA-Z0-9]', src)):
                            record_data['photo_data'] = src

    def _parse_education_table(self, table, record_data: Dict[str, Any]) -> None:
        """Parse education information table."""
        rows = table.find_all('tr')

        if len(rows) >= 2:  # Header + data rows
            header_row = rows[0]
            [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

            for row in rows[1:]:  # Skip header
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 7:  # Ensure we have enough columns
                    education = EducationRecord(
                        qualification=cells[0].get_text(strip=True) if len(cells) > 0 else '',
                        board_university=cells[1].get_text(strip=True) if len(cells) > 1 else '',
                        college_name=cells[2].get_text(strip=True) if len(cells) > 2 else '',
                        college_address=cells[3].get_text(strip=True) if len(cells) > 3 else '',
                        academic_year_from=cells[4].get_text(strip=True) if len(cells) > 4 else '',
                        academic_year_to=cells[5].get_text(strip=True) if len(cells) > 5 else '',
                        hallticket_no=cells[6].get_text(strip=True) if len(cells) > 6 else ''
                    )
                    record_data['education'].append(education)

    def _parse_work_info_table(self, table, record_data: Dict[str, Any]) -> None:
        """Parse work/study information table."""
        rows = table.find_all('tr')

        if len(rows) >= 2:  # Header + data row
            data_row = rows[1]
            cells = data_row.find_all('td')

            if len(cells) >= 4:
                work_experience = WorkExperience(
                    address=cells[0].get_text(strip=True) if len(cells) > 0 else '',
                    state=cells[1].get_text(strip=True) if len(cells) > 1 else '',
                    district=cells[2].get_text(strip=True) if len(cells) > 2 else '',
                    pincode=cells[3].get_text(strip=True) if len(cells) > 3 else ''
                )
                record_data['work_experience'] = work_experience

    def batch_extract(
        self,
        registration_numbers: List[str],
        batch_size: int = 100,
        start_index: int = 0
    ) -> List[PharmacistRecord]:
        """
        Extract detailed information for multiple registration numbers.

        Args:
            registration_numbers: List of registration numbers to extract.
            batch_size: Number of records to process in each batch.
            start_index: Index to start extraction from.

        Returns:
            List of detailed pharmacist records.
        """
        # Batch extract
        self.logger.info(
            f"Starting batch extraction: {len(registration_numbers)} numbers, "
            f"batch size: {batch_size}, start: {start_index}"
        )

        detailed_records = []
        numbers_to_process = registration_numbers[start_index:]

        for i, reg_number in enumerate(numbers_to_process, start_index):
            try:
                self.logger.debug(f"Processing {i+1}/{len(registration_numbers)}: {reg_number}")

                detailed_info = self.extract_detailed_info(reg_number)

                if detailed_info:
                    detailed_records.append(detailed_info)
                    self.logger.debug(f"Successfully extracted: {reg_number}")
                else:
                    self.logger.warning(f"No detailed info found for: {reg_number}")

                # Progress logging every 10 records
                if (i + 1) % 10 == 0:
                    self.logger.info(
                        f"Batch progress: {i+1}/{len(registration_numbers)} processed, "
                        f"{len(detailed_records)} successful extractions"
                    )

            except Exception as e:
                self.logger.error(
                    f"Failed to extract detailed info for {reg_number}: {str(e)}",
                    extra={"registration_number": reg_number, "error": str(e)}
                )

        self.logger.info(
            f"Batch extraction completed: {len(detailed_records)} records extracted"
        )

        return detailed_records

    def test_connection(self) -> None:
        """Test connection to TGPC website for health checks."""
        try:
            response = self._make_request(self.base_url)
            if response.status_code != 200:
                raise NetworkException(f"Unexpected status code: {response.status_code}")

            self.logger.debug("Connection test successful")

        except Exception as e:
            raise NetworkException(f"Connection test failed: {str(e)}", cause=e)

    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics and rate limiter status."""
        return {
            "rate_limiter_stats": self.rate_limiter.get_stats(),
            "session_info": {
                "headers": dict(self.session.headers),
                "cookies": len(self.session.cookies)
            },
            "urls": {
                "base_url": self.base_url,
                "total_url": self.total_url,
                "search_url": self.search_url
            }
        }
