#!/usr/bin/env python
"""
Test runner script for Acta backend testing.
Provides convenient commands for running different test suites.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)

    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False


def main():
    parser = argparse.ArgumentParser(description='Acta Backend Test Runner')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage report')
    parser.add_argument('--fast', action='store_true', help='Run tests in parallel (faster)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--app', type=str, help='Run tests for specific app (accounts, tasks, analytics)')
    parser.add_argument('--class', dest='test_class', type=str, help='Run specific test class')
    parser.add_argument('--method', type=str, help='Run specific test method')
    parser.add_argument('--clean', action='store_true', help='Clean test database and cache before running')

    args = parser.parse_args()

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # Clean up if requested
    if args.clean:
        print("🧹 Cleaning test environment...")
        run_command("find . -name '*.pyc' -delete", "Remove Python cache files")
        run_command("find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true", "Remove cache directories")
        run_command("rm -rf .pytest_cache", "Remove pytest cache")
        run_command("rm -f .coverage", "Remove coverage file")

    success_count = 0
    total_tests = 0

    # Build pytest command
    pytest_cmd = "python -m pytest"

    # Add verbosity
    if args.verbose:
        pytest_cmd += " -v"
    else:
        pytest_cmd += " -q"

    # Add parallel execution
    if args.fast:
        pytest_cmd += " -n auto"

    # Add coverage
    if args.coverage:
        pytest_cmd += " --cov=. --cov-report=term-missing --cov-report=html"

    # Determine test path
    if args.app:
        test_path = f"tests/test_{args.app}.py"
        if args.test_class:
            test_path += f"::{args.test_class}"
            if args.method:
                test_path += f"::{args.method}"
    elif args.test_class:
        test_path = f"tests/*::{args.test_class}"
        if args.method:
            test_path += f"::{args.method}"
    elif args.unit:
        test_path = "tests/ -m 'unit'"
    elif args.integration:
        test_path = "tests/ -m 'integration'"
    else:
        test_path = "tests/"

    pytest_cmd += f" {test_path}"

    # Run main test command
    print("🚀 Starting Acta Backend Test Suite")
    print(f"📁 Project Directory: {project_dir}")
    print(f"🔧 Django Settings: Acta_backend.settings.development")

    success = run_command(pytest_cmd, "Main Test Suite")
    if success:
        success_count += 1
    total_tests += 1

    # Additional checks if running full suite
    if not any([args.app, args.test_class, args.method, args.unit, args.integration]):
        # Run Django checks
        django_check = run_command("python manage.py check", "Django System Check")
        if django_check:
            success_count += 1
        total_tests += 1

        # Run migrations check
        migration_check = run_command("python manage.py makemigrations --dry-run --check", "Migration Check")
        if migration_check:
            success_count += 1
        total_tests += 1

    # Display summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    print(f"✅ Passed: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")

    if success_count == total_tests:
        print("🎉 All tests passed!")
        if args.coverage:
            print("📈 Coverage report generated in htmlcov/index.html")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
