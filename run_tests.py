#!/usr/bin/env python3
"""
Comprehensive Test Execution Script for AI-PPT System
Runs all tests with performance monitoring and detailed reporting
"""

import asyncio
import os
import sys
import subprocess
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

class TestExecutor:
    """Execute tests with comprehensive monitoring and reporting"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.performance_data = {}
        
    def run_tests(self, test_types: List[str], verbose: bool = False, coverage: bool = True) -> Dict[str, Any]:
        """
        Run specified test types
        
        Args:
            test_types: List of test types to run
            verbose: Enable verbose output
            coverage: Enable coverage reporting
            
        Returns:
            Dict containing test results and metrics
        """
        print("🚀 AI-PPT System Test Execution")
        print("=" * 50)
        
        self.start_time = datetime.utcnow()
        
        # Prepare environment
        self._prepare_environment()
        
        # Run tests
        for test_type in test_types:
            print(f"\n📋 Running {test_type.upper()} tests...")
            result = self._run_test_type(test_type, verbose, coverage)
            self.results[test_type] = result
            self._print_test_summary(test_type, result)
        
        self.end_time = datetime.utcnow()
        
        # Generate comprehensive report
        report = self._generate_report()
        
        # Print final summary
        self._print_final_summary(report)
        
        return report
    
    def _prepare_environment(self):
        """Prepare test environment"""
        print("🔧 Preparing test environment...")
        
        # Install dependencies if needed
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
            ], check=True, capture_output=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to install dependencies: {e}")
        
        # Set environment variables
        os.environ.setdefault("TESTING", "true")
        os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ai_ppt.db")
        os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
        
        # Clean up previous test artifacts
        test_files = [
            "test_ai_ppt.db",
            "test-report.json",
            "test-report.html",
            "htmlcov"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
    
    def _run_test_type(self, test_type: str, verbose: bool, coverage: bool) -> Dict[str, Any]:
        """Run a specific type of tests"""
        start_time = time.time()
        
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test directory
        if test_type == "all":
            cmd.append("tests/")
        else:
            test_dir = f"tests/{test_type}"
            if not os.path.exists(test_dir):
                return {
                    "status": "skipped",
                    "reason": f"Test directory {test_dir} not found",
                    "duration": 0.0,
                    "tests": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0
                }
            cmd.append(test_dir)
        
        # Add options
        if verbose:
            cmd.extend(["-v", "-s"])
        
        if coverage and test_type in ["unit", "integration", "all"]:
            cmd.extend([
                "--cov=backend",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-report=xml"
            ])
        
        # Add markers
        if test_type != "all":
            cmd.extend(["-m", test_type])
        
        # Add JSON report
        cmd.extend([
            "--json-report",
            f"--json-report-file=test-report-{test_type}.json"
        ])
        
        # Add HTML report
        cmd.extend([
            "--html", f"test-report-{test_type}.html",
            "--self-contained-html"
        ])
        
        try:
            # Run tests
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Parse results
            return self._parse_test_results(test_type, result, duration)
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "reason": "Tests timed out after 10 minutes",
                "duration": 600.0,
                "tests": 0,
                "passed": 0,
                "failed": 1,
                "skipped": 0
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e),
                "duration": time.time() - start_time,
                "tests": 0,
                "passed": 0,
                "failed": 1,
                "skipped": 0
            }
    
    def _parse_test_results(self, test_type: str, result: subprocess.CompletedProcess, duration: float) -> Dict[str, Any]:
        """Parse pytest results"""
        # Try to load JSON report
        json_file = f"test-report-{test_type}.json"
        
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                summary = data.get('summary', {})
                
                return {
                    "status": "completed",
                    "duration": duration,
                    "tests": summary.get('total', 0),
                    "passed": summary.get('passed', 0),
                    "failed": summary.get('failed', 0),
                    "skipped": summary.get('skipped', 0),
                    "errors": summary.get('error', 0),
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "json_report": json_file
                }
                
            except Exception as e:
                print(f"⚠️ Failed to parse JSON report: {e}")
        
        # Fallback to parsing stdout
        lines = result.stdout.split('\n')
        summary_line = None
        
        for line in lines:
            if 'passed' in line and ('failed' in line or 'error' in line or 'skipped' in line):
                summary_line = line
                break
        
        if summary_line:
            # Parse summary line (e.g., "5 passed, 2 failed, 1 skipped in 10.5s")
            import re
            
            passed = len(re.findall(r'(\d+) passed', summary_line))
            failed = len(re.findall(r'(\d+) failed', summary_line))
            skipped = len(re.findall(r'(\d+) skipped', summary_line))
            errors = len(re.findall(r'(\d+) error', summary_line))
            
            return {
                "status": "completed",
                "duration": duration,
                "tests": passed + failed + skipped + errors,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "errors": errors,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        
        return {
            "status": "unknown",
            "duration": duration,
            "tests": 0,
            "passed": 0,
            "failed": 1 if result.returncode != 0 else 0,
            "skipped": 0,
            "errors": 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def _print_test_summary(self, test_type: str, result: Dict[str, Any]):
        """Print summary for a test type"""
        status = result["status"]
        
        if status == "completed":
            passed = result["passed"]
            failed = result["failed"]
            skipped = result["skipped"]
            duration = result["duration"]
            
            status_icon = "✅" if failed == 0 else "❌"
            print(f"{status_icon} {test_type.upper()}: {passed} passed, {failed} failed, {skipped} skipped ({duration:.2f}s)")
            
            if failed > 0:
                print(f"   ❌ {failed} test(s) failed - check detailed report")
                
        elif status == "skipped":
            print(f"⏭️ {test_type.upper()}: Skipped - {result['reason']}")
            
        elif status == "timeout":
            print(f"⏰ {test_type.upper()}: Timed out after {result['duration']:.2f}s")
            
        else:
            print(f"❌ {test_type.upper()}: Error - {result.get('reason', 'Unknown error')}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # Calculate totals
        total_tests = sum(r.get("tests", 0) for r in self.results.values())
        total_passed = sum(r.get("passed", 0) for r in self.results.values())
        total_failed = sum(r.get("failed", 0) for r in self.results.values())
        total_skipped = sum(r.get("skipped", 0) for r in self.results.values())
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Generate coverage report
        coverage_data = self._get_coverage_data()
        
        # Generate performance metrics
        performance_metrics = self._get_performance_metrics()
        
        report = {
            "summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_duration": total_duration,
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped,
                "success_rate": success_rate
            },
            "test_types": self.results,
            "coverage": coverage_data,
            "performance": performance_metrics,
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        report_file = f"comprehensive-test-report-{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Comprehensive report saved: {report_file}")
        
        return report
    
    def _get_coverage_data(self) -> Dict[str, Any]:
        """Get coverage data if available"""
        coverage_file = "coverage.xml"
        
        if os.path.exists(coverage_file):
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                
                # Extract coverage metrics
                coverage_elem = root.find('.//coverage')
                if coverage_elem is not None:
                    return {
                        "line_coverage": float(coverage_elem.get('line-rate', 0)) * 100,
                        "branch_coverage": float(coverage_elem.get('branch-rate', 0)) * 100,
                        "lines_covered": int(coverage_elem.get('lines-covered', 0)),
                        "lines_valid": int(coverage_elem.get('lines-valid', 0)),
                        "branches_covered": int(coverage_elem.get('branches-covered', 0)),
                        "branches_valid": int(coverage_elem.get('branches-valid', 0))
                    }
            except Exception as e:
                print(f"⚠️ Failed to parse coverage data: {e}")
        
        return {
            "line_coverage": 0.0,
            "branch_coverage": 0.0,
            "lines_covered": 0,
            "lines_valid": 0,
            "branches_covered": 0,
            "branches_valid": 0
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            import psutil
            
            # Get current system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "memory_usage_mb": memory.used // 1024 // 1024,
                "memory_percent": memory.percent,
                "cpu_percent": cpu_percent,
                "available_memory_mb": memory.available // 1024 // 1024
            }
        except ImportError:
            return {
                "memory_usage_mb": 0,
                "memory_percent": 0,
                "cpu_percent": 0,
                "available_memory_mb": 0
            }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for failures
        total_failed = sum(r.get("failed", 0) for r in self.results.values())
        if total_failed > 0:
            recommendations.append(f"🔧 Fix {total_failed} failing test(s) to improve system reliability")
        
        # Check coverage
        coverage_data = self._get_coverage_data()
        if coverage_data["line_coverage"] < 80:
            recommendations.append(f"📊 Increase test coverage from {coverage_data['line_coverage']:.1f}% to at least 80%")
        
        # Check for timeouts
        timeouts = [r for r in self.results.values() if r.get("status") == "timeout"]
        if timeouts:
            recommendations.append("⏰ Optimize slow tests that are timing out")
        
        # Check for skipped tests
        total_skipped = sum(r.get("skipped", 0) for r in self.results.values())
        if total_skipped > 0:
            recommendations.append(f"⏭️ Review {total_skipped} skipped test(s) and enable if appropriate")
        
        if not recommendations:
            recommendations.append("🎉 All tests passing! System is in excellent condition.")
        
        return recommendations
    
    def _print_final_summary(self, report: Dict[str, Any]):
        """Print final test summary"""
        summary = report["summary"]
        
        print("\n" + "=" * 50)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 50)
        
        print(f"📊 Tests: {summary['passed']}/{summary['total_tests']} passed ({summary['success_rate']:.1f}%)")
        print(f"⏱️ Duration: {summary['total_duration']:.2f}s")
        
        coverage = report["coverage"]
        if coverage["line_coverage"] > 0:
            print(f"📈 Coverage: {coverage['line_coverage']:.1f}% lines, {coverage['branch_coverage']:.1f}% branches")
        
        performance = report["performance"]
        if performance["memory_usage_mb"] > 0:
            print(f"💾 Memory: {performance['memory_usage_mb']}MB used ({performance['memory_percent']:.1f}%)")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   {rec}")
        
        # Exit code
        exit_code = 0 if summary["failed"] == 0 else 1
        print(f"\n🚪 Exit code: {exit_code}")
        
        return exit_code

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI-PPT System Test Runner")
    
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["unit", "integration", "e2e", "performance", "all"],
        default=["all"],
        help="Test types to run"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only unit tests for quick feedback"
    )
    
    args = parser.parse_args()
    
    # Handle quick mode
    if args.quick:
        test_types = ["unit"]
    elif "all" in args.types:
        test_types = ["unit", "integration", "e2e"]
    else:
        test_types = args.types
    
    # Run tests
    executor = TestExecutor()
    report = executor.run_tests(
        test_types=test_types,
        verbose=args.verbose,
        coverage=not args.no_coverage
    )
    
    # Exit with appropriate code
    exit_code = 0 if report["summary"]["failed"] == 0 else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()