#!/usr/bin/env python3
"""
Performance Test Runner
מריץ בדיקות ביצועים

Main script to run all performance tests for the AI Chat System.
"""

import sys
import os
import argparse
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.performance.chat_performance_test import ChatPerformanceTests, run_database_performance_test
from tests.performance.performance_config import ENV_CONFIG, REPORTER


def check_prerequisites():
    """Check if all prerequisites are met for running performance tests"""
    print("🔍 Checking prerequisites...")
    
    # Check if backend is running
    import requests
    try:
        response = requests.get(f"{ENV_CONFIG.backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend server is not accessible: {e}")
        print(f"   Make sure the backend is running at {ENV_CONFIG.backend_url}")
        return False
    
    # Check if required Python packages are installed
    required_packages = ['requests', 'psutil', 'memory_profiler']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("   Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All prerequisites met")
    return True


def run_quick_test():
    """Run a quick performance test"""
    print("🚀 Running quick performance test...")
    
    perf_tests = ChatPerformanceTests()
    perf_tests.setup_test_sessions(5)
    
    # Run only light load test
    perf_tests.runner.run_load_test(
        test_name="Quick Test",
        concurrent_users=3,
        requests_per_user=5,
        test_function=perf_tests.test_basic_message_load
    )
    
    # Save results
    perf_tests.runner.save_metrics("quick_performance_results.json")
    
    print("✅ Quick performance test completed")
    return perf_tests.runner.metrics


def run_full_test_suite():
    """Run the complete performance test suite"""
    print("🎯 Running full performance test suite...")
    
    perf_tests = ChatPerformanceTests()
    perf_tests.run_all_performance_tests()
    
    print("✅ Full performance test suite completed")
    return perf_tests.runner.metrics


def run_custom_test(concurrent_users: int, requests_per_user: int, test_type: str = "basic"):
    """Run a custom performance test"""
    print(f"🔧 Running custom performance test...")
    print(f"   Users: {concurrent_users}, Requests per user: {requests_per_user}, Type: {test_type}")
    
    perf_tests = ChatPerformanceTests()
    perf_tests.setup_test_sessions(max(10, concurrent_users))
    
    # Select test function based on type
    if test_type == "streaming":
        test_function = perf_tests.test_streaming_load
    elif test_type == "mixed":
        test_function = perf_tests.test_mixed_operations
    else:
        test_function = perf_tests.test_basic_message_load
    
    # Run custom test
    perf_tests.runner.run_load_test(
        test_name=f"Custom Test - {test_type}",
        concurrent_users=concurrent_users,
        requests_per_user=requests_per_user,
        test_function=test_function
    )
    
    # Save results
    perf_tests.runner.save_metrics(f"custom_performance_results_{test_type}.json")
    
    print("✅ Custom performance test completed")
    return perf_tests.runner.metrics


def run_database_tests():
    """Run database-specific performance tests"""
    print("🗄️ Running database performance tests...")
    
    run_database_performance_test()
    
    print("✅ Database performance tests completed")


def generate_reports(metrics_list):
    """Generate performance reports"""
    print("📊 Generating performance reports...")
    
    if not metrics_list:
        print("❌ No metrics available for report generation")
        return
    
    # Convert metrics to dict format for reporting
    metrics_dicts = []
    for metric in metrics_list:
        if hasattr(metric, 'to_dict'):
            metrics_dicts.append(metric.to_dict())
        else:
            metrics_dicts.append(metric)
    
    # Generate summary report
    summary_report = REPORTER.generate_summary_report(metrics_dicts)
    with open("performance_summary.txt", "w") as f:
        f.write(summary_report)
    print("📄 Summary report saved to: performance_summary.txt")
    
    # Generate CSV report
    csv_report = REPORTER.generate_csv_report(metrics_dicts)
    with open("performance_results.csv", "w") as f:
        f.write(csv_report)
    print("📊 CSV report saved to: performance_results.csv")
    
    # Print summary to console
    print("\n" + "="*60)
    print("PERFORMANCE TEST SUMMARY")
    print("="*60)
    print(summary_report)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Run performance tests for the AI Chat System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_performance_tests.py --quick
  python run_performance_tests.py --full
  python run_performance_tests.py --custom --users 10 --requests 20 --type streaming
  python run_performance_tests.py --database
        """
    )
    
    # Test type arguments
    test_group = parser.add_mutually_exclusive_group(required=True)
    test_group.add_argument("--quick", action="store_true", help="Run quick performance test")
    test_group.add_argument("--full", action="store_true", help="Run full performance test suite")
    test_group.add_argument("--custom", action="store_true", help="Run custom performance test")
    test_group.add_argument("--database", action="store_true", help="Run database performance tests")
    
    # Custom test parameters
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users (for custom test)")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests per user (for custom test)")
    parser.add_argument("--type", choices=["basic", "streaming", "mixed"], default="basic", 
                       help="Type of test to run (for custom test)")
    
    # General options
    parser.add_argument("--skip-prereq", action="store_true", help="Skip prerequisite checks")
    parser.add_argument("--no-reports", action="store_true", help="Skip report generation")
    parser.add_argument("--output-dir", default=".", help="Output directory for results")
    
    args = parser.parse_args()
    
    # Change to output directory
    if args.output_dir != ".":
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
    
    print("🎯 AI Chat System Performance Test Runner")
    print("=" * 50)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {ENV_CONFIG.backend_url}")
    print(f"Output directory: {os.getcwd()}")
    print()
    
    # Check prerequisites
    if not args.skip_prereq:
        if not check_prerequisites():
            print("❌ Prerequisites not met. Exiting.")
            sys.exit(1)
        print()
    
    # Run selected test
    metrics = []
    start_time = time.time()
    
    try:
        if args.quick:
            metrics = run_quick_test()
        elif args.full:
            metrics = run_full_test_suite()
        elif args.custom:
            metrics = run_custom_test(args.users, args.requests, args.type)
        elif args.database:
            run_database_tests()
            # Database tests don't return metrics in the same format
            metrics = []
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⏱️ Total execution time: {total_time:.2f} seconds")
        
        # Generate reports
        if not args.no_reports and metrics:
            generate_reports(metrics)
        
        print("\n✅ Performance testing completed successfully!")
        
        # Exit with appropriate code based on results
        if metrics:
            # Check if any tests failed performance thresholds
            failed_tests = 0
            for metric in metrics:
                if hasattr(metric, 'success_rate'):
                    if metric.success_rate < ENV_CONFIG.min_success_rate:
                        failed_tests += 1
                elif hasattr(metric, 'average_response_time_ms'):
                    if metric.average_response_time_ms > ENV_CONFIG.max_response_time_ms:
                        failed_tests += 1
            
            if failed_tests > 0:
                print(f"⚠️ {failed_tests} test(s) failed to meet performance thresholds")
                sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Performance testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()