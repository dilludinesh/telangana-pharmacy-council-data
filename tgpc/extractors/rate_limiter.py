"""
Rate limiting system for TGPC data extraction.

This module provides intelligent rate limiting to prevent server blocking
and ensure respectful interaction with the TGPC website.
"""

import time
import random
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from tgpc.config.settings import Config
from tgpc.utils.logger import get_logger


@dataclass
class RequestStats:
    """Statistics for tracking request patterns."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    blocked_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    consecutive_failures: int = 0


class RateLimiter:
    """
    Intelligent rate limiter with adaptive behavior.
    
    This class implements sophisticated rate limiting algorithms including:
    - Exponential backoff for failures
    - Adaptive delays based on server response
    - Circuit breaker pattern for persistent failures
    - Jitter to avoid thundering herd problems
    """
    
    def __init__(self, config: Config):
        """
        Initialize the rate limiter.
        
        Args:
            config: Configuration object with rate limiting settings.
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Rate limiting parameters
        self.min_delay = config.min_delay
        self.max_delay = config.max_delay
        self.long_break_after = config.long_break_after
        self.long_break_duration = config.long_break_duration
        self.adaptive_pause_minutes = config.adaptive_pause_minutes
        
        # State tracking
        self.stats = RequestStats()
        self.current_delay = self.min_delay
        self.requests_since_break = 0
        self.circuit_breaker_open = False
        self.circuit_breaker_open_time: Optional[datetime] = None
        
        # Adaptive parameters
        self.success_delay_reduction = 0.9  # Reduce delay by 10% on success
        self.failure_delay_increase = 1.5   # Increase delay by 50% on failure
        self.max_consecutive_failures = 5   # Open circuit breaker after 5 failures
        self.circuit_breaker_timeout = 300  # 5 minutes
        
        self.logger.info(
            "Rate limiter initialized",
            extra={
                "min_delay": self.min_delay,
                "max_delay": self.max_delay,
                "long_break_after": self.long_break_after
            }
        )
    
    def wait_if_needed(self) -> None:
        """
        Wait if rate limiting is required.
        
        This method implements the main rate limiting logic including:
        - Circuit breaker checks
        - Adaptive delays
        - Long breaks
        - Jitter application
        """
        # Check circuit breaker
        if self.circuit_breaker_open:
            self._check_circuit_breaker()
            if self.circuit_breaker_open:
                raise Exception("Circuit breaker is open - too many consecutive failures")
        
        # Calculate delay
        delay = self._calculate_delay()
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.8, 1.2)
        final_delay = delay * jitter
        
        self.logger.debug(
            "Rate limiting delay",
            extra={
                "base_delay": delay,
                "jitter": jitter,
                "final_delay": final_delay,
                "requests_since_break": self.requests_since_break
            }
        )
        
        # Wait
        if final_delay > 0:
            time.sleep(final_delay)
        
        # Check for long break
        self.requests_since_break += 1
        if self.requests_since_break >= self.long_break_after:
            self._take_long_break()
    
    def record_request(self, response_time: float, status_code: int, success: bool = True) -> None:
        """
        Record request statistics and adjust rate limiting parameters.
        
        Args:
            response_time: Time taken for the request in seconds.
            status_code: HTTP status code of the response.
            success: Whether the request was successful.
        """
        self.stats.total_requests += 1
        self.stats.last_request_time = datetime.now()
        
        # Update response time average
        if self.stats.total_requests == 1:
            self.stats.average_response_time = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.stats.average_response_time = (
                alpha * response_time + 
                (1 - alpha) * self.stats.average_response_time
            )
        
        if success:
            self.stats.successful_requests += 1
            self.stats.consecutive_failures = 0
            self._on_success(response_time, status_code)
        else:
            self.stats.failed_requests += 1
            self.stats.consecutive_failures += 1
            self._on_failure(response_time, status_code)
        
        # Check for blocking indicators
        if status_code in [403, 429]:
            self.stats.blocked_requests += 1
            self._on_blocked(status_code)
        
        self.logger.debug(
            "Request recorded",
            extra={
                "response_time": response_time,
                "status_code": status_code,
                "success": success,
                "consecutive_failures": self.stats.consecutive_failures,
                "current_delay": self.current_delay
            }
        )
    
    def _calculate_delay(self) -> float:
        """Calculate the delay for the next request."""
        # Base delay with adaptive adjustment
        delay = self.current_delay
        
        # Increase delay based on recent failures
        if self.stats.consecutive_failures > 0:
            failure_multiplier = 1.0 + (self.stats.consecutive_failures * 0.5)
            delay *= failure_multiplier
        
        # Adjust based on average response time
        if self.stats.average_response_time > 5.0:  # Slow responses
            delay *= 1.2
        elif self.stats.average_response_time < 1.0:  # Fast responses
            delay *= 0.9
        
        # Ensure delay is within bounds
        return max(self.min_delay, min(delay, self.max_delay))
    
    def _on_success(self, response_time: float, status_code: int) -> None:
        """Handle successful request."""
        # Gradually reduce delay on success
        self.current_delay = max(
            self.min_delay,
            self.current_delay * self.success_delay_reduction
        )
        
        # Close circuit breaker if it was open
        if self.circuit_breaker_open:
            self.circuit_breaker_open = False
            self.circuit_breaker_open_time = None
            self.logger.info("Circuit breaker closed after successful request")
    
    def _on_failure(self, response_time: float, status_code: int) -> None:
        """Handle failed request."""
        # Increase delay on failure
        self.current_delay = min(
            self.max_delay,
            self.current_delay * self.failure_delay_increase
        )
        
        # Check if we should open circuit breaker
        if self.stats.consecutive_failures >= self.max_consecutive_failures:
            self.circuit_breaker_open = True
            self.circuit_breaker_open_time = datetime.now()
            self.logger.warning(
                "Circuit breaker opened due to consecutive failures",
                extra={"consecutive_failures": self.stats.consecutive_failures}
            )
    
    def _on_blocked(self, status_code: int) -> None:
        """Handle blocked request (403, 429)."""
        # Aggressive backoff for blocking
        self.current_delay = min(
            self.max_delay,
            self.current_delay * 2.0
        )
        
        # Take immediate adaptive pause
        pause_duration = self.adaptive_pause_minutes * 60
        self.logger.warning(
            f"Blocking detected (HTTP {status_code}), taking adaptive pause",
            extra={"pause_duration": pause_duration}
        )
        time.sleep(pause_duration)
    
    def _take_long_break(self) -> None:
        """Take a long break after processing many requests."""
        self.logger.info(
            f"Taking long break after {self.requests_since_break} requests",
            extra={"break_duration": self.long_break_duration}
        )
        
        time.sleep(self.long_break_duration)
        self.requests_since_break = 0
        
        # Reset delay to baseline after long break
        self.current_delay = self.min_delay
    
    def _check_circuit_breaker(self) -> None:
        """Check if circuit breaker should be closed."""
        if not self.circuit_breaker_open or not self.circuit_breaker_open_time:
            return
        
        time_since_open = datetime.now() - self.circuit_breaker_open_time
        if time_since_open.total_seconds() >= self.circuit_breaker_timeout:
            self.circuit_breaker_open = False
            self.circuit_breaker_open_time = None
            self.stats.consecutive_failures = 0
            self.current_delay = self.min_delay
            self.logger.info("Circuit breaker closed after timeout")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current rate limiting statistics."""
        return {
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "blocked_requests": self.stats.blocked_requests,
            "success_rate": (
                self.stats.successful_requests / self.stats.total_requests
                if self.stats.total_requests > 0 else 0.0
            ),
            "average_response_time": self.stats.average_response_time,
            "current_delay": self.current_delay,
            "consecutive_failures": self.stats.consecutive_failures,
            "circuit_breaker_open": self.circuit_breaker_open,
            "requests_since_break": self.requests_since_break
        }
    
    def reset(self) -> None:
        """Reset rate limiter state."""
        self.stats = RequestStats()
        self.current_delay = self.min_delay
        self.requests_since_break = 0
        self.circuit_breaker_open = False
        self.circuit_breaker_open_time = None
        
        self.logger.info("Rate limiter state reset")
    
    def force_pause(self, duration: float) -> None:
        """Force a pause for the specified duration."""
        self.logger.info(f"Forced pause for {duration} seconds")
        time.sleep(duration)
    
    def is_healthy(self) -> bool:
        """Check if the rate limiter is in a healthy state."""
        if self.circuit_breaker_open:
            return False
        
        if self.stats.total_requests > 10:
            success_rate = self.stats.successful_requests / self.stats.total_requests
            if success_rate < 0.8:  # Less than 80% success rate
                return False
        
        return True