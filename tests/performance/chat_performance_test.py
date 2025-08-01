"""
Performance Testing for AI Chat System
בדיקות ביצועים למערכת שיחות AI

This module contains comprehensive performance tests for the chat system,
including load testing, stress testing, and performance benchmarking.
"""

import asyncio
import time
import statistics
import json
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests
import pytest
import psutil
import memory_profiler

# Import test utilities
from tests.integration.test_chat_integration import create_test_database, MockLLMService


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    requests_per_second: float
    average_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    success_rate: float
    error_count: int
    memory_usage_mb: float
    cpu_usage_percent: float
    concurrent_users: int
    total_requests: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['start_time'] = self.start_time.isoformat()
        result['end_time'] = self.end_time.isoformat()
        return result


class PerformanceTestRunner:
    """Performance test runner with metrics collection"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.metrics: List[PerformanceMetrics] = []
        
    def create_session(self, title: str = "Performance Test Session") -> str:
        """Create a test session and return session ID"""
        response = self.session.post(
            f"{self.base_url}/api/chat/sessions",
            json={
                "title": title,
                "model_id": "mock-model",
                "user_id": "perf-test-user"
            }
        )
        response.raise_for_status()
        return response.json()["id"]
    
    def send_message(self, session_id: str, message: str) -> Tuple[bool, float]:
        """Send a message and return (success, response_time_ms)"""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat/send",
                json={
                    "session_id": session_id,
                    "message": message,
                    "user_id": "perf-test-user"
                },
                timeout=30
            )
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                return True, response_time_ms
            else:
                return False, response_time_ms
                
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return False, response_time_ms
    
    def stream_message(self, session_id: str, message: str) -> Tuple[bool, float]:
        """Send a streaming message and return (success, response_time_ms)"""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat/stream",
                json={
                    "session_id": session_id,
                    "message": message,
                    "user_id": "perf-test-user"
                },
                stream=True,
                timeout=30
            )
            
            # Read the entire stream
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    pass  # Process chunk
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                return True, response_time_ms
            else:
                return False, response_time_ms
                
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return False, response_time_ms
    
    def run_load_test(
        self,
        test_name: str,
        concurrent_users: int,
        requests_per_user: int,
        test_function,
        **kwargs
    ) -> PerformanceMetrics:
        """Run a load test with specified parameters"""
        
        print(f"🚀 Starting load test: {test_name}")
        print(f"   Concurrent users: {concurrent_users}")
        print(f"   Requests per user: {requests_per_user}")
        print(f"   Total requests: {concurrent_users * requests_per_user}")
        
        # Collect initial system metrics
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = datetime.now()
        response_times = []
        errors = 0
        
        def user_simulation(user_id: int) -> List[Tuple[bool, float]]:
            """Simulate a single user's requests"""
            user_results = []
            for request_id in range(requests_per_user):
                success, response_time = test_function(user_id, request_id, **kwargs)
                user_results.append((success, response_time))
                if not success:
                    errors += 1
                
                # Small delay between requests from same user
                time.sleep(0.1)
            
            return user_results
        
        # Execute load test with thread pool
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # Submit all user simulations
            futures = [
                executor.submit(user_simulation, user_id)
                for user_id in range(concurrent_users)
            ]
            
            # Collect results
            for future in as_completed(futures):
                try:
                    user_results = future.result()
                    for success, response_time in user_results:
                        response_times.append(response_time)
                except Exception as e:
                    print(f"User simulation failed: {e}")
                    errors += 1
        
        end_time = datetime.now()
        
        # Collect final system metrics
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent()
        
        # Calculate metrics
        duration_ms = (end_time - start_time).total_seconds() * 1000
        total_requests = len(response_times)
        successful_requests = sum(1 for rt in response_times if rt > 0)
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        requests_per_second = total_requests / (duration_ms / 1000) if duration_ms > 0 else 0
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            requests_per_second=requests_per_second,
            average_response_time_ms=avg_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            success_rate=success_rate,
            error_count=errors,
            memory_usage_mb=final_memory - initial_memory,
            cpu_usage_percent=cpu_usage,
            concurrent_users=concurrent_users,
            total_requests=total_requests
        )
        
        self.metrics.append(metrics)
        
        # Print results
        print(f"✅ Load test completed: {test_name}")
        print(f"   Duration: {duration_ms:.0f}ms")
        print(f"   Requests/sec: {requests_per_second:.2f}")
        print(f"   Avg response time: {avg_response_time:.2f}ms")
        print(f"   95th percentile: {p95_response_time:.2f}ms")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Memory usage: {final_memory - initial_memory:.1f}MB")
        
        return metrics
    
    def save_metrics(self, filename: str = "performance_results.json"):
        """Save all collected metrics to a JSON file"""
        with open(filename, 'w') as f:
            json.dump([m.to_dict() for m in self.metrics], f, indent=2)
        print(f"📊 Performance metrics saved to {filename}")


class ChatPerformanceTests:
    """Chat system performance test suite"""
    
    def __init__(self):
        self.runner = PerformanceTestRunner()
        self.test_sessions = []
    
    def setup_test_sessions(self, count: int = 10):
        """Create test sessions for performance testing"""
        print(f"🔧 Setting up {count} test sessions...")
        self.test_sessions = []
        for i in range(count):
            try:
                session_id = self.runner.create_session(f"Perf Test Session {i+1}")
                self.test_sessions.append(session_id)
            except Exception as e:
                print(f"Failed to create session {i+1}: {e}")
        
        print(f"✅ Created {len(self.test_sessions)} test sessions")
    
    def test_basic_message_load(self, user_id: int, request_id: int) -> Tuple[bool, float]:
        """Basic message sending test function"""
        if not self.test_sessions:
            return False, 0
        
        session_id = self.test_sessions[user_id % len(self.test_sessions)]
        message = f"Load test message from user {user_id}, request {request_id}"
        
        return self.runner.send_message(session_id, message)
    
    def test_streaming_load(self, user_id: int, request_id: int) -> Tuple[bool, float]:
        """Streaming message test function"""
        if not self.test_sessions:
            return False, 0
        
        session_id = self.test_sessions[user_id % len(self.test_sessions)]
        message = f"Streaming load test from user {user_id}, request {request_id}"
        
        return self.runner.stream_message(session_id, message)
    
    def test_mixed_operations(self, user_id: int, request_id: int) -> Tuple[bool, float]:
        """Mixed operations test function"""
        if not self.test_sessions:
            return False, 0
        
        # Alternate between different operations
        if request_id % 3 == 0:
            # Send regular message
            session_id = self.test_sessions[user_id % len(self.test_sessions)]
            message = f"Mixed test message from user {user_id}, request {request_id}"
            return self.runner.send_message(session_id, message)
        
        elif request_id % 3 == 1:
            # Get session messages
            session_id = self.test_sessions[user_id % len(self.test_sessions)]
            start_time = time.time()
            try:
                response = self.runner.session.get(
                    f"{self.runner.base_url}/api/chat/sessions/{session_id}/messages",
                    timeout=10
                )
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                return response.status_code == 200, response_time_ms
            except Exception:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                return False, response_time_ms
        
        else:
            # Search messages
            start_time = time.time()
            try:
                response = self.runner.session.get(
                    f"{self.runner.base_url}/api/chat/search",
                    params={"query": f"user {user_id}"},
                    timeout=10
                )
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                return response.status_code == 200, response_time_ms
            except Exception:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                return False, response_time_ms
    
    def run_all_performance_tests(self):
        """Run all performance test scenarios"""
        print("🎯 Starting comprehensive performance test suite...")
        
        # Setup test sessions
        self.setup_test_sessions(20)
        
        # Test 1: Light load - Basic functionality
        self.runner.run_load_test(
            test_name="Light Load - Basic Messages",
            concurrent_users=5,
            requests_per_user=10,
            test_function=self.test_basic_message_load
        )
        
        # Test 2: Medium load - Typical usage
        self.runner.run_load_test(
            test_name="Medium Load - Typical Usage",
            concurrent_users=15,
            requests_per_user=20,
            test_function=self.test_basic_message_load
        )
        
        # Test 3: Heavy load - Peak usage
        self.runner.run_load_test(
            test_name="Heavy Load - Peak Usage",
            concurrent_users=30,
            requests_per_user=15,
            test_function=self.test_basic_message_load
        )
        
        # Test 4: Streaming performance
        self.runner.run_load_test(
            test_name="Streaming Performance",
            concurrent_users=10,
            requests_per_user=10,
            test_function=self.test_streaming_load
        )
        
        # Test 5: Mixed operations
        self.runner.run_load_test(
            test_name="Mixed Operations",
            concurrent_users=20,
            requests_per_user=15,
            test_function=self.test_mixed_operations
        )
        
        # Test 6: Stress test - Maximum load
        self.runner.run_load_test(
            test_name="Stress Test - Maximum Load",
            concurrent_users=50,
            requests_per_user=10,
            test_function=self.test_basic_message_load
        )
        
        # Save results
        self.runner.save_metrics("chat_performance_results.json")
        
        # Generate performance report
        self.generate_performance_report()
    
    def generate_performance_report(self):
        """Generate a comprehensive performance report"""
        print("📊 Generating performance report...")
        
        if not self.runner.metrics:
            print("No metrics available for report generation")
            return
        
        # Calculate summary statistics
        all_response_times = []
        all_success_rates = []
        all_rps = []
        
        for metric in self.runner.metrics:
            all_response_times.append(metric.average_response_time_ms)
            all_success_rates.append(metric.success_rate)
            all_rps.append(metric.requests_per_second)
        
        # Generate HTML report
        html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Chat System Performance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .metric-card {{ background: #fff; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .metric-title {{ font-size: 18px; font-weight: bold; color: #495057; margin-bottom: 15px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .metric-unit {{ font-size: 14px; color: #6c757d; }}
        .summary-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .summary-table th, .summary-table td {{ border: 1px solid #dee2e6; padding: 12px; text-align: left; }}
        .summary-table th {{ background: #f8f9fa; font-weight: bold; }}
        .pass {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .fail {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Chat System Performance Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Tests: {len(self.runner.metrics)}</p>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">Overall Performance Summary</div>
        <p><strong>Average Response Time:</strong> <span class="metric-value">{statistics.mean(all_response_times):.2f}</span> <span class="metric-unit">ms</span></p>
        <p><strong>Average Success Rate:</strong> <span class="metric-value">{statistics.mean(all_success_rates):.1f}</span> <span class="metric-unit">%</span></p>
        <p><strong>Average Requests/Second:</strong> <span class="metric-value">{statistics.mean(all_rps):.2f}</span> <span class="metric-unit">req/s</span></p>
    </div>
    
    <h2>Detailed Test Results</h2>
    <table class="summary-table">
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Users</th>
                <th>Total Requests</th>
                <th>Avg Response (ms)</th>
                <th>95th Percentile (ms)</th>
                <th>Requests/sec</th>
                <th>Success Rate (%)</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for metric in self.runner.metrics:
            # Determine status based on performance criteria
            status_class = "pass"
            status_text = "PASS"
            
            if metric.average_response_time_ms > 2000 or metric.success_rate < 95:
                status_class = "fail"
                status_text = "FAIL"
            elif metric.average_response_time_ms > 1000 or metric.success_rate < 98:
                status_class = "warning"
                status_text = "WARNING"
            
            html_report += f"""
            <tr>
                <td>{metric.test_name}</td>
                <td>{metric.concurrent_users}</td>
                <td>{metric.total_requests}</td>
                <td>{metric.average_response_time_ms:.2f}</td>
                <td>{metric.p95_response_time_ms:.2f}</td>
                <td>{metric.requests_per_second:.2f}</td>
                <td>{metric.success_rate:.1f}</td>
                <td class="{status_class}">{status_text}</td>
            </tr>
"""
        
        html_report += """
        </tbody>
    </table>
    
    <h2>Performance Recommendations</h2>
    <div class="metric-card">
        <ul>
"""
        
        # Add recommendations based on results
        avg_response_time = statistics.mean(all_response_times)
        avg_success_rate = statistics.mean(all_success_rates)
        
        if avg_response_time > 1000:
            html_report += "<li>⚠️ Average response time is high. Consider optimizing database queries and caching.</li>"
        
        if avg_success_rate < 98:
            html_report += "<li>⚠️ Success rate is below optimal. Investigate error handling and timeout configurations.</li>"
        
        if statistics.mean(all_rps) < 10:
            html_report += "<li>⚠️ Request throughput is low. Consider scaling infrastructure or optimizing code.</li>"
        
        html_report += """
            <li>✅ Monitor memory usage during peak loads to prevent memory leaks.</li>
            <li>✅ Implement connection pooling for better database performance.</li>
            <li>✅ Consider implementing rate limiting to prevent system overload.</li>
        </ul>
    </div>
</body>
</html>
"""
        
        # Save HTML report
        with open("chat_performance_report.html", "w") as f:
            f.write(html_report)
        
        print("✅ Performance report generated: chat_performance_report.html")


@memory_profiler.profile
def memory_usage_test():
    """Test memory usage during chat operations"""
    print("🧠 Running memory usage test...")
    
    # This decorator will profile memory usage
    runner = PerformanceTestRunner()
    
    # Create sessions and send messages
    sessions = []
    for i in range(10):
        session_id = runner.create_session(f"Memory Test Session {i}")
        sessions.append(session_id)
    
    # Send many messages to test memory usage
    for i in range(100):
        session_id = sessions[i % len(sessions)]
        runner.send_message(session_id, f"Memory test message {i}")
        
        if i % 10 == 0:
            print(f"Sent {i+1} messages...")
    
    print("✅ Memory usage test completed")


def run_database_performance_test():
    """Test database performance under load"""
    print("🗄️ Running database performance test...")
    
    import tempfile
    import os
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        create_test_database(db_path)
        
        # Test database operations
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert performance test
        start_time = time.time()
        for i in range(1000):
            cursor.execute("""
                INSERT INTO chat_sessions (id, title, model_id, user_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (f"session-{i}", f"Session {i}", "test-model", "test-user", 
                  datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        insert_time = time.time() - start_time
        
        # Query performance test
        start_time = time.time()
        for i in range(100):
            cursor.execute("SELECT * FROM chat_sessions WHERE user_id = ?", ("test-user",))
            results = cursor.fetchall()
        
        query_time = time.time() - start_time
        
        conn.close()
        
        print(f"✅ Database performance test completed:")
        print(f"   Insert 1000 sessions: {insert_time:.2f}s ({1000/insert_time:.1f} ops/sec)")
        print(f"   Query 100 times: {query_time:.2f}s ({100/query_time:.1f} ops/sec)")
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    # Run performance tests
    print("🚀 Starting Chat System Performance Tests")
    print("=" * 50)
    
    try:
        # Run main performance test suite
        perf_tests = ChatPerformanceTests()
        perf_tests.run_all_performance_tests()
        
        # Run memory usage test
        memory_usage_test()
        
        # Run database performance test
        run_database_performance_test()
        
        print("\n" + "=" * 50)
        print("✅ All performance tests completed successfully!")
        print("📊 Check chat_performance_report.html for detailed results")
        
    except Exception as e:
        print(f"\n❌ Performance tests failed: {e}")
        raise