"""
Performance Test Configuration
הגדרות בדיקות ביצועים

Configuration settings and utilities for performance testing.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class PerformanceTestConfig:
    """Configuration for performance tests"""
    
    # Server configuration
    backend_url: str = "http://127.0.0.1:5000"
    frontend_url: str = "http://localhost:5174"
    
    # Test parameters
    max_concurrent_users: int = 50
    max_requests_per_user: int = 50
    request_timeout: int = 30
    
    # Performance thresholds
    max_response_time_ms: float = 2000.0
    min_success_rate: float = 95.0
    max_error_rate: float = 5.0
    min_requests_per_second: float = 10.0
    
    # Memory and CPU limits
    max_memory_usage_mb: float = 500.0
    max_cpu_usage_percent: float = 80.0
    
    # Database performance
    max_db_query_time_ms: float = 100.0
    max_db_insert_time_ms: float = 50.0
    
    # Test scenarios
    test_scenarios: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.test_scenarios is None:
            self.test_scenarios = [
                {
                    "name": "Smoke Test",
                    "concurrent_users": 1,
                    "requests_per_user": 5,
                    "description": "Basic functionality test"
                },
                {
                    "name": "Light Load",
                    "concurrent_users": 5,
                    "requests_per_user": 10,
                    "description": "Light usage simulation"
                },
                {
                    "name": "Normal Load",
                    "concurrent_users": 15,
                    "requests_per_user": 20,
                    "description": "Normal usage simulation"
                },
                {
                    "name": "Heavy Load",
                    "concurrent_users": 30,
                    "requests_per_user": 15,
                    "description": "Heavy usage simulation"
                },
                {
                    "name": "Stress Test",
                    "concurrent_users": 50,
                    "requests_per_user": 10,
                    "description": "Maximum load stress test"
                }
            ]
    
    @classmethod
    def from_env(cls) -> 'PerformanceTestConfig':
        """Create configuration from environment variables"""
        return cls(
            backend_url=os.getenv('PERF_BACKEND_URL', "http://127.0.0.1:5000"),
            frontend_url=os.getenv('PERF_FRONTEND_URL', "http://localhost:5174"),
            max_concurrent_users=int(os.getenv('PERF_MAX_USERS', '50')),
            max_requests_per_user=int(os.getenv('PERF_MAX_REQUESTS', '50')),
            request_timeout=int(os.getenv('PERF_TIMEOUT', '30')),
            max_response_time_ms=float(os.getenv('PERF_MAX_RESPONSE_TIME', '2000')),
            min_success_rate=float(os.getenv('PERF_MIN_SUCCESS_RATE', '95')),
            max_error_rate=float(os.getenv('PERF_MAX_ERROR_RATE', '5')),
            min_requests_per_second=float(os.getenv('PERF_MIN_RPS', '10')),
            max_memory_usage_mb=float(os.getenv('PERF_MAX_MEMORY', '500')),
            max_cpu_usage_percent=float(os.getenv('PERF_MAX_CPU', '80'))
        )


class PerformanceThresholds:
    """Performance threshold definitions"""
    
    # Response time thresholds (milliseconds)
    EXCELLENT_RESPONSE_TIME = 200
    GOOD_RESPONSE_TIME = 500
    ACCEPTABLE_RESPONSE_TIME = 1000
    POOR_RESPONSE_TIME = 2000
    
    # Success rate thresholds (percentage)
    EXCELLENT_SUCCESS_RATE = 99.9
    GOOD_SUCCESS_RATE = 99.0
    ACCEPTABLE_SUCCESS_RATE = 95.0
    POOR_SUCCESS_RATE = 90.0
    
    # Throughput thresholds (requests per second)
    EXCELLENT_THROUGHPUT = 100
    GOOD_THROUGHPUT = 50
    ACCEPTABLE_THROUGHPUT = 20
    POOR_THROUGHPUT = 10
    
    # Memory usage thresholds (MB)
    LOW_MEMORY_USAGE = 100
    MODERATE_MEMORY_USAGE = 250
    HIGH_MEMORY_USAGE = 500
    EXCESSIVE_MEMORY_USAGE = 1000
    
    @classmethod
    def evaluate_response_time(cls, response_time_ms: float) -> str:
        """Evaluate response time performance"""
        if response_time_ms <= cls.EXCELLENT_RESPONSE_TIME:
            return "EXCELLENT"
        elif response_time_ms <= cls.GOOD_RESPONSE_TIME:
            return "GOOD"
        elif response_time_ms <= cls.ACCEPTABLE_RESPONSE_TIME:
            return "ACCEPTABLE"
        elif response_time_ms <= cls.POOR_RESPONSE_TIME:
            return "POOR"
        else:
            return "UNACCEPTABLE"
    
    @classmethod
    def evaluate_success_rate(cls, success_rate: float) -> str:
        """Evaluate success rate performance"""
        if success_rate >= cls.EXCELLENT_SUCCESS_RATE:
            return "EXCELLENT"
        elif success_rate >= cls.GOOD_SUCCESS_RATE:
            return "GOOD"
        elif success_rate >= cls.ACCEPTABLE_SUCCESS_RATE:
            return "ACCEPTABLE"
        elif success_rate >= cls.POOR_SUCCESS_RATE:
            return "POOR"
        else:
            return "UNACCEPTABLE"
    
    @classmethod
    def evaluate_throughput(cls, rps: float) -> str:
        """Evaluate throughput performance"""
        if rps >= cls.EXCELLENT_THROUGHPUT:
            return "EXCELLENT"
        elif rps >= cls.GOOD_THROUGHPUT:
            return "GOOD"
        elif rps >= cls.ACCEPTABLE_THROUGHPUT:
            return "ACCEPTABLE"
        elif rps >= cls.POOR_THROUGHPUT:
            return "POOR"
        else:
            return "UNACCEPTABLE"
    
    @classmethod
    def evaluate_memory_usage(cls, memory_mb: float) -> str:
        """Evaluate memory usage"""
        if memory_mb <= cls.LOW_MEMORY_USAGE:
            return "EXCELLENT"
        elif memory_mb <= cls.MODERATE_MEMORY_USAGE:
            return "GOOD"
        elif memory_mb <= cls.HIGH_MEMORY_USAGE:
            return "ACCEPTABLE"
        elif memory_mb <= cls.EXCESSIVE_MEMORY_USAGE:
            return "POOR"
        else:
            return "UNACCEPTABLE"


class TestDataGenerator:
    """Generate test data for performance tests"""
    
    @staticmethod
    def generate_messages(count: int, prefix: str = "Test message") -> List[str]:
        """Generate test messages"""
        return [f"{prefix} {i+1}" for i in range(count)]
    
    @staticmethod
    def generate_long_message(word_count: int = 100) -> str:
        """Generate a long test message"""
        words = [
            "performance", "testing", "message", "content", "system",
            "response", "evaluation", "benchmark", "load", "stress",
            "concurrent", "users", "requests", "throughput", "latency"
        ]
        
        message_words = []
        for i in range(word_count):
            message_words.append(words[i % len(words)])
        
        return " ".join(message_words)
    
    @staticmethod
    def generate_session_titles(count: int) -> List[str]:
        """Generate test session titles"""
        return [f"Performance Test Session {i+1}" for i in range(count)]
    
    @staticmethod
    def generate_user_ids(count: int) -> List[str]:
        """Generate test user IDs"""
        return [f"perf-test-user-{i+1}" for i in range(count)]


class PerformanceReporter:
    """Generate performance test reports"""
    
    @staticmethod
    def generate_summary_report(metrics_list: List[Dict[str, Any]]) -> str:
        """Generate a summary report from metrics"""
        if not metrics_list:
            return "No performance metrics available."
        
        # Calculate overall statistics
        total_tests = len(metrics_list)
        total_requests = sum(m.get('total_requests', 0) for m in metrics_list)
        avg_response_time = sum(m.get('average_response_time_ms', 0) for m in metrics_list) / total_tests
        avg_success_rate = sum(m.get('success_rate', 0) for m in metrics_list) / total_tests
        avg_throughput = sum(m.get('requests_per_second', 0) for m in metrics_list) / total_tests
        
        # Evaluate performance
        response_time_rating = PerformanceThresholds.evaluate_response_time(avg_response_time)
        success_rate_rating = PerformanceThresholds.evaluate_success_rate(avg_success_rate)
        throughput_rating = PerformanceThresholds.evaluate_throughput(avg_throughput)
        
        report = f"""
Performance Test Summary Report
===============================

Overall Statistics:
- Total Tests: {total_tests}
- Total Requests: {total_requests}
- Average Response Time: {avg_response_time:.2f}ms ({response_time_rating})
- Average Success Rate: {avg_success_rate:.1f}% ({success_rate_rating})
- Average Throughput: {avg_throughput:.2f} req/s ({throughput_rating})

Test Results:
"""
        
        for i, metrics in enumerate(metrics_list, 1):
            test_name = metrics.get('test_name', f'Test {i}')
            response_time = metrics.get('average_response_time_ms', 0)
            success_rate = metrics.get('success_rate', 0)
            throughput = metrics.get('requests_per_second', 0)
            
            rt_rating = PerformanceThresholds.evaluate_response_time(response_time)
            sr_rating = PerformanceThresholds.evaluate_success_rate(success_rate)
            tp_rating = PerformanceThresholds.evaluate_throughput(throughput)
            
            report += f"""
{i}. {test_name}
   - Response Time: {response_time:.2f}ms ({rt_rating})
   - Success Rate: {success_rate:.1f}% ({sr_rating})
   - Throughput: {throughput:.2f} req/s ({tp_rating})
"""
        
        return report
    
    @staticmethod
    def generate_csv_report(metrics_list: List[Dict[str, Any]]) -> str:
        """Generate CSV format report"""
        if not metrics_list:
            return "test_name,concurrent_users,total_requests,avg_response_time_ms,success_rate,requests_per_second\n"
        
        csv_lines = ["test_name,concurrent_users,total_requests,avg_response_time_ms,success_rate,requests_per_second"]
        
        for metrics in metrics_list:
            line = f"{metrics.get('test_name', 'Unknown')}," \
                   f"{metrics.get('concurrent_users', 0)}," \
                   f"{metrics.get('total_requests', 0)}," \
                   f"{metrics.get('average_response_time_ms', 0):.2f}," \
                   f"{metrics.get('success_rate', 0):.1f}," \
                   f"{metrics.get('requests_per_second', 0):.2f}"
            csv_lines.append(line)
        
        return "\n".join(csv_lines)


# Default configuration instance
DEFAULT_CONFIG = PerformanceTestConfig()

# Environment-based configuration
ENV_CONFIG = PerformanceTestConfig.from_env()

# Test data generators
MESSAGE_GENERATOR = TestDataGenerator()

# Performance thresholds
THRESHOLDS = PerformanceThresholds()

# Reporter
REPORTER = PerformanceReporter()