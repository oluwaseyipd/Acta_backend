#!/usr/bin/env python
"""
Simple test summary script for Acta backend.
Runs tests in small batches to avoid timeouts and provides summary.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_test_batch(test_path, description):
    """Run a batch of tests and return results."""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Path: {test_path}")
    print('='*50)

    try:
        # Run tests with minimal output
        result = subprocess.run(
            f"python -m pytest {test_path} --tb=no -q",
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        output_lines = result.stdout.split('\n')

        # Parse results
        passed = 0
        failed = 0
        errors = 0

        for line in output_lines:
            if 'passed' in line and 'failed' in line:
                # Example: "2 failed, 40 passed in 12.34s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'failed,':
                        failed = int(parts[i-1])
                    elif part == 'passed':
                        passed = int(parts[i-1])
            elif line.endswith(' passed in'):
                # Example: "42 passed in 12.34s"
                passed = int(line.split()[0])
            elif 'FAILED' in line:
                failed += 1
            elif 'ERROR' in line:
                errors += 1

        if result.returncode == 0:
            print(f"✅ PASSED - {passed} tests passed")
            return {'passed': passed, 'failed': 0, 'errors': 0, 'status': 'PASS'}
        else:
            print(f"❌ FAILED - {passed} passed, {failed} failed, {errors} errors")
            if result.stderr:
                print(f"Error output: {result.stderr[:200]}...")
            return {'passed': passed, 'failed': failed, 'errors': errors, 'status': 'FAIL'}

    except subprocess.TimeoutExpired:
        print("⏱️ TIMEOUT - Tests took too long")
        return {'passed': 0, 'failed': 0, 'errors': 1, 'status': 'TIMEOUT'}
    except Exception as e:
        print(f"💥 ERROR - {str(e)}")
        return {'passed': 0, 'failed': 0, 'errors': 1, 'status': 'ERROR'}

def main():
    """Run test summary."""
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    print("🚀 Acta Backend Test Summary")
    print(f"📁 Project: {project_dir}")
    print("⏱️  Running tests in batches to avoid timeouts...")

    # Test batches
    test_batches = [
        # Accounts tests by category
        ("tests/test_accounts.py::TestUserRegistration", "User Registration"),
        ("tests/test_accounts.py::TestUserLogin", "User Login"),
        ("tests/test_accounts.py::TestUserLogout", "User Logout"),
        ("tests/test_accounts.py::TestTokenRefresh", "Token Refresh"),
        ("tests/test_accounts.py::TestCurrentUser", "Current User"),
        ("tests/test_accounts.py::TestUserProfile", "User Profile"),
        ("tests/test_accounts.py::TestChangePassword", "Change Password"),
        ("tests/test_accounts.py::TestPasswordReset", "Password Reset"),
        ("tests/test_accounts.py::TestUserModel", "User Model"),
        ("tests/test_accounts.py::TestProfileModel", "Profile Model"),
        ("tests/test_accounts.py::TestUserRoleModel", "User Role Model"),
        ("tests/test_accounts.py::TestProfilePermissions", "Profile Permissions"),

        # Tasks tests by category
        ("tests/test_tasks.py::TestTaskViewSet", "Task ViewSet"),
        ("tests/test_tasks.py::TestCategoryViewSet", "Category ViewSet"),
        ("tests/test_tasks.py::TestTaskCommentViewSet", "Task Comments"),
        ("tests/test_tasks.py::TestTaskModel", "Task Model"),

        # Analytics tests by category
        ("tests/test_analytics.py::TestOverviewStatsView", "Overview Stats"),
        ("tests/test_analytics.py::TestDailyStatsView", "Daily Stats"),
        ("tests/test_analytics.py::TestWeeklyStatsView", "Weekly Stats"),
        ("tests/test_analytics.py::TestProductivityTrendView", "Productivity Trends"),
        ("tests/test_analytics.py::TestCategoryStatsView", "Category Stats"),
        ("tests/test_analytics.py::TestDailyStatsModel", "Daily Stats Model"),
        ("tests/test_analytics.py::TestWeeklyStatsModel", "Weekly Stats Model"),
        ("tests/test_analytics.py::TestAnalyticsPermissions", "Analytics Permissions"),
    ]

    # Track overall results
    total_results = {
        'passed': 0,
        'failed': 0,
        'errors': 0,
        'timeouts': 0,
        'batches_passed': 0,
        'total_batches': len(test_batches)
    }

    failed_batches = []

    # Run each batch
    for test_path, description in test_batches:
        result = run_test_batch(test_path, description)

        # Update totals
        total_results['passed'] += result['passed']
        total_results['failed'] += result['failed']
        total_results['errors'] += result['errors']

        if result['status'] == 'PASS':
            total_results['batches_passed'] += 1
        elif result['status'] == 'TIMEOUT':
            total_results['timeouts'] += 1
            failed_batches.append((description, 'TIMEOUT'))
        else:
            failed_batches.append((description, result['status']))

        # Small delay to prevent overwhelming
        time.sleep(0.5)

    # Print summary
    print(f"\n{'='*60}")
    print("📊 FINAL TEST SUMMARY")
    print('='*60)
    print(f"Total Tests Run: {total_results['passed'] + total_results['failed']}")
    print(f"✅ Passed: {total_results['passed']}")
    print(f"❌ Failed: {total_results['failed']}")
    print(f"💥 Errors: {total_results['errors']}")
    print(f"⏱️  Timeouts: {total_results['timeouts']}")
    print()
    print(f"Test Batches: {total_results['batches_passed']}/{total_results['total_batches']} passed")

    if failed_batches:
        print(f"\n⚠️  Failed Batches:")
        for batch_name, status in failed_batches:
            print(f"   - {batch_name}: {status}")

    # Calculate pass rate
    total_tests = total_results['passed'] + total_results['failed']
    if total_tests > 0:
        pass_rate = (total_results['passed'] / total_tests) * 100
        print(f"\n📈 Pass Rate: {pass_rate:.1f}%")

    # Overall status
    if total_results['failed'] == 0 and total_results['errors'] == 0 and total_results['timeouts'] == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("💥 SOME TESTS FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
