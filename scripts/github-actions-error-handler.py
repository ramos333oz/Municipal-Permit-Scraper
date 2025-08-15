#!/usr/bin/env python3
"""
Enhanced Error Handling for GitHub Actions Municipal Permit Scraping
Provides comprehensive error handling, retry logic, and monitoring
"""

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ScrapingError:
    """Structured error information"""
    timestamp: str
    municipality: str
    error_type: str
    severity: ErrorSeverity
    message: str
    traceback: Optional[str] = None
    context: Optional[Dict] = None
    retry_count: int = 0
    resolved: bool = False

class GitHubActionsErrorHandler:
    """Enhanced error handling for GitHub Actions environment"""
    
    def __init__(self, municipality: str, max_retries: int = 3):
        self.municipality = municipality
        self.max_retries = max_retries
        self.errors: List[ScrapingError] = []
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging for GitHub Actions"""
        log_level = logging.DEBUG if os.getenv('DEBUG_MODE') == 'true' else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{self.municipality}_scraper.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, 
                    error: Exception, 
                    error_type: str,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: Optional[Dict] = None,
                    retry_count: int = 0) -> ScrapingError:
        """Handle and log errors with structured information"""
        
        scraping_error = ScrapingError(
            timestamp=datetime.utcnow().isoformat(),
            municipality=self.municipality,
            error_type=error_type,
            severity=severity,
            message=str(error),
            traceback=traceback.format_exc(),
            context=context or {},
            retry_count=retry_count
        )
        
        self.errors.append(scraping_error)
        
        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error_type} - {error}")
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY: {error_type} - {error}")
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY: {error_type} - {error}")
        else:
            self.logger.info(f"LOW SEVERITY: {error_type} - {error}")
        
        # Set GitHub Actions output for monitoring
        self.set_github_output(f"error_{error_type}", str(error))
        
        return scraping_error
    
    def retry_with_backoff(self, 
                          func: Callable, 
                          *args, 
                          error_type: str = "retry_operation",
                          **kwargs) -> Any:
        """Retry function with exponential backoff"""
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    self.logger.info(f"✅ {error_type} succeeded on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                if attempt == self.max_retries:
                    # Final attempt failed
                    self.handle_error(
                        e, 
                        error_type, 
                        ErrorSeverity.HIGH,
                        context={"final_attempt": True, "total_attempts": attempt + 1},
                        retry_count=attempt
                    )
                    raise
                else:
                    # Retry with backoff
                    backoff_time = 2 ** attempt
                    self.logger.warning(
                        f"⚠️ {error_type} failed (attempt {attempt + 1}/{self.max_retries + 1}). "
                        f"Retrying in {backoff_time} seconds..."
                    )
                    
                    self.handle_error(
                        e, 
                        error_type, 
                        ErrorSeverity.LOW,
                        context={"retry_attempt": attempt + 1, "backoff_seconds": backoff_time},
                        retry_count=attempt
                    )
                    
                    time.sleep(backoff_time)
    
    def check_environment(self) -> bool:
        """Validate environment and dependencies"""
        required_env_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'GEOCODIO_API_KEY'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Missing environment variables: {', '.join(missing_vars)}"
            self.handle_error(
                ValueError(error_msg),
                "environment_validation",
                ErrorSeverity.CRITICAL,
                context={"missing_variables": missing_vars}
            )
            return False
        
        # Test imports
        try:
            import playwright
            import supabase
            import pandas
            self.logger.info("✅ All required packages available")
            return True
        except ImportError as e:
            self.handle_error(
                e,
                "dependency_import",
                ErrorSeverity.CRITICAL,
                context={"missing_package": str(e)}
            )
            return False
    
    def monitor_performance(self, operation_name: str, start_time: float) -> Dict:
        """Monitor and log performance metrics"""
        duration = time.time() - start_time
        
        performance_data = {
            "operation": operation_name,
            "duration_seconds": round(duration, 2),
            "municipality": self.municipality,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log performance
        if duration > 300:  # 5 minutes
            self.logger.warning(f"⚠️ Slow operation: {operation_name} took {duration:.2f}s")
        else:
            self.logger.info(f"✅ {operation_name} completed in {duration:.2f}s")
        
        # Set GitHub Actions output
        self.set_github_output(f"duration_{operation_name}", str(duration))
        
        return performance_data
    
    def set_github_output(self, name: str, value: str):
        """Set GitHub Actions output variable"""
        github_output = os.getenv('GITHUB_OUTPUT')
        if github_output:
            with open(github_output, 'a') as f:
                f.write(f"{name}={value}\n")
    
    def generate_error_report(self) -> Dict:
        """Generate comprehensive error report"""
        report = {
            "municipality": self.municipality,
            "total_errors": len(self.errors),
            "error_summary": {},
            "critical_errors": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Categorize errors
        for error in self.errors:
            error_type = error.error_type
            if error_type not in report["error_summary"]:
                report["error_summary"][error_type] = {
                    "count": 0,
                    "severities": {}
                }
            
            report["error_summary"][error_type]["count"] += 1
            severity = error.severity.value
            if severity not in report["error_summary"][error_type]["severities"]:
                report["error_summary"][error_type]["severities"][severity] = 0
            report["error_summary"][error_type]["severities"][severity] += 1
            
            # Track critical errors
            if error.severity == ErrorSeverity.CRITICAL:
                report["critical_errors"].append(asdict(error))
        
        return report
    
    def save_error_report(self, file_path: Optional[str] = None):
        """Save error report to file"""
        if not file_path:
            file_path = f"{self.municipality}_error_report.json"
        
        report = self.generate_error_report()
        
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📊 Error report saved to {file_path}")
        return file_path
    
    def should_fail_workflow(self) -> bool:
        """Determine if workflow should fail based on error severity"""
        critical_errors = [e for e in self.errors if e.severity == ErrorSeverity.CRITICAL]
        high_errors = [e for e in self.errors if e.severity == ErrorSeverity.HIGH]
        
        # Fail if any critical errors or too many high-severity errors
        if critical_errors:
            self.logger.error(f"❌ Workflow should fail: {len(critical_errors)} critical errors")
            return True
        
        if len(high_errors) >= 3:
            self.logger.error(f"❌ Workflow should fail: {len(high_errors)} high-severity errors")
            return True
        
        return False

# Usage example for integration with existing scrapers
def enhanced_scraper_wrapper(municipality: str, scraper_function: Callable):
    """Wrapper to add enhanced error handling to existing scrapers"""
    error_handler = GitHubActionsErrorHandler(municipality)
    
    try:
        # Environment validation
        if not error_handler.check_environment():
            sys.exit(1)
        
        # Execute scraper with monitoring
        start_time = time.time()
        
        result = error_handler.retry_with_backoff(
            scraper_function,
            error_type="main_scraping_operation"
        )
        
        # Monitor performance
        error_handler.monitor_performance("complete_scraping", start_time)
        
        # Generate final report
        error_handler.save_error_report()
        
        # Determine exit status
        if error_handler.should_fail_workflow():
            sys.exit(1)
        else:
            error_handler.logger.info("✅ Scraping completed successfully")
            sys.exit(0)
            
    except Exception as e:
        error_handler.handle_error(
            e,
            "wrapper_execution",
            ErrorSeverity.CRITICAL
        )
        error_handler.save_error_report()
        sys.exit(1)

if __name__ == "__main__":
    # Example usage
    municipality = os.getenv('MUNICIPALITY', 'san-diego')
    error_handler = GitHubActionsErrorHandler(municipality)
    
    # Test error handling
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_handler.handle_error(e, "test_error", ErrorSeverity.MEDIUM)
    
    # Generate and save report
    error_handler.save_error_report()
    print("Error handling test completed")
