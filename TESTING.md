# Testing Documentation

## Overview

This document provides comprehensive information about testing the Acta Task Management Backend API. Our test suite covers unit tests, integration tests, and end-to-end API testing.

## Test Structure

```
tests/
├── __init__.py
├── test_accounts.py      # User authentication and profile tests
├── test_tasks.py         # Task management functionality tests
├── test_analytics.py     # Analytics and reporting tests
└── conftest.py           # Shared fixtures and configuration
```

## Testing Framework

We use **pytest** with Django integration for comprehensive testing:

- **pytest**: Main testing framework
- **pytest-django**: Django integration
- **pytest-cov**: Coverage reporting
- **pytest-xdist**: Parallel test execution
- **pytest-mock**: Mocking capabilities

## Configuration Files

### pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = Acta_backend.settings.development
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --tb=short --strict-markers --disable-warnings --reuse-db
```

### conftest.py
Contains shared fixtures for:
- API clients (authenticated/unauthenticated)
- Test users and profiles
- Sample tasks and categories
- Analytics data
- JWT tokens

## Running Tests

### Quick Start
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific app tests
python -m pytest tests/test_accounts.py
python -m pytest tests/test_tasks.py
python -m pytest tests/test_analytics.py
```

### Using Test Runner Script
```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run tests in parallel (faster)
python run_tests.py --fast

# Run specific app
python run_tests.py --app accounts

# Run specific test class
python run_tests.py --class TestTaskViewSet

# Clean environment and run tests
python run_tests.py --clean --coverage
```

### Advanced Usage
```bash
# Run tests with coverage report
python -m pytest --cov=. --cov-report=html --cov-report=term-missing

# Run tests in parallel
python -m pytest -n auto

# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Run with specific verbosity
python -m pytest -v --tb=short
```

## Test Categories

### Unit Tests
Test individual components in isolation:
- Model methods and properties
- Serializer validation
- Utility functions
- Business logic

### Integration Tests
Test component interactions:
- API endpoints
- Database operations
- Signal handlers
- Authentication flow

### API Tests
Test complete request-response cycles:
- Authentication endpoints
- CRUD operations
- Filtering and search
- Permissions and security

## Test Coverage

### Accounts App Tests (test_accounts.py)

#### User Registration
- ✅ Successful registration with JWT tokens
- ✅ Password validation and mismatch handling
- ✅ Duplicate email prevention
- ✅ Email format validation
- ✅ Weak password rejection

#### User Authentication
- ✅ Successful login with credentials
- ✅ Invalid credentials handling
- ✅ Non-existent user handling
- ✅ Inactive user restrictions
- ✅ Token refresh functionality
- ✅ Logout and token blacklisting

#### User Profile Management
- ✅ Profile retrieval and updates
- ✅ Nested user field updates
- ✅ Phone number validation
- ✅ Profile permissions
- ✅ Auto-creation via signals

#### Password Management
- ✅ Password change with validation
- ✅ Password reset request
- ✅ Old password verification
- ✅ Password strength requirements

#### Models Testing
- ✅ User model creation and properties
- ✅ Profile model with JSON fields
- ✅ UserRole model and choices
- ✅ Signal-based auto-creation

### Tasks App Tests (test_tasks.py)

#### Task CRUD Operations
- ✅ Task listing with pagination
- ✅ Task creation with validation
- ✅ Task retrieval and updates
- ✅ Task deletion
- ✅ Status management
- ✅ Completion toggling

#### Task Filtering and Search
- ✅ Status-based filtering
- ✅ Priority filtering
- ✅ Date range filtering
- ✅ Overdue task identification
- ✅ Search functionality
- ✅ Ordering capabilities

#### Specialized Endpoints
- ✅ Today's tasks
- ✅ Overdue tasks
- ✅ Recently completed tasks
- ✅ Upcoming tasks
- ✅ Bulk operations

#### Task Relationships
- ✅ Category management
- ✅ Task comments CRUD
- ✅ File attachments
- ✅ User assignments

#### Permissions and Security
- ✅ User data isolation
- ✅ Object-level permissions
- ✅ Authentication requirements
- ✅ Owner-only access

#### Models and Properties
- ✅ Task model validation
- ✅ Due date calculations
- ✅ Status change signals
- ✅ Category relationships

### Analytics App Tests (test_analytics.py)

#### Overview Statistics
- ✅ Dashboard stats calculation
- ✅ Completion rate computation
- ✅ Empty data handling
- ✅ Authentication requirements

#### Daily Statistics
- ✅ Daily stats listing and filtering
- ✅ Date range queries
- ✅ User data isolation
- ✅ Productivity calculations

#### Weekly Statistics
- ✅ Weekly aggregation
- ✅ Week boundary calculations
- ✅ Multi-week filtering
- ✅ Performance metrics

#### Trend Analysis
- ✅ Productivity trends
- ✅ Custom date ranges
- ✅ Completion rate trends
- ✅ Category breakdowns

#### Analytics Models
- ✅ DailyStats creation and properties
- ✅ WeeklyStats aggregation
- ✅ Unique constraints
- ✅ Calculation methods

## Fixtures and Test Data

### User Fixtures
```python
@pytest.fixture
def user(db):
    """Create test user"""

@pytest.fixture
def admin_user(db):
    """Create admin user"""

@pytest.fixture
def authenticated_client(api_client, user):
    """Authenticated API client"""
```

### Task Fixtures
```python
@pytest.fixture
def task(user, category):
    """Create test task"""

@pytest.fixture
def multiple_tasks(user, category):
    """Create multiple test tasks"""

@pytest.fixture
def overdue_task(user, category):
    """Create overdue test task"""
```

### Analytics Fixtures
```python
@pytest.fixture
def daily_stats(user):
    """Create test daily statistics"""

@pytest.fixture
def jwt_tokens(user):
    """Create JWT tokens for user"""
```

## Testing Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Keep tests focused and independent

### Database Testing
- Use `@pytest.mark.django_db` decorator
- Leverage fixtures for consistent test data
- Test both success and failure scenarios
- Verify database state changes

### API Testing
- Test all HTTP methods
- Verify response status codes
- Check response data structure
- Test authentication and permissions
- Validate error handling

### Coverage Goals
- Maintain >90% code coverage
- Focus on critical business logic
- Test edge cases and error conditions
- Document any untested code with reasons

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing
python run_tests.py --clean --coverage
python manage.py check
python manage.py makemigrations --dry-run --check
```

### CI Pipeline Tests
1. Environment setup
2. Dependency installation
3. Database migration
4. Full test suite execution
5. Coverage reporting
6. Security checks

## Debugging Tests

### Common Issues
- **Database state**: Use `--reuse-db` for faster runs
- **Fixtures conflicts**: Check fixture dependencies
- **Authentication errors**: Verify client authentication
- **Timing issues**: Use `timezone.now()` for consistency

### Debug Commands
```bash
# Run single test with full output
python -m pytest tests/test_tasks.py::TestTaskViewSet::test_create_task -v -s

# Drop into debugger on failure
python -m pytest --pdb

# Show local variables on failure
python -m pytest --tb=long

# Run with warnings enabled
python -m pytest --disable-warnings=false
```

### Test Data Inspection
```python
# Add to test for debugging
import pdb; pdb.set_trace()

# Or use pytest's built-in
assert False, f"Debug: {variable_to_inspect}"
```

## Performance Testing

### Load Testing Considerations
- Database query optimization
- API response times
- Concurrent user handling
- Memory usage patterns

### Profiling Tests
```bash
# Profile test execution
python -m pytest --profile

# Memory usage
python -m pytest --memray
```

## Security Testing

### Authentication Tests
- JWT token validation
- Session management
- Password security
- Permission enforcement

### Data Protection Tests
- User data isolation
- SQL injection prevention
- XSS protection
- CSRF token validation

## Maintenance

### Regular Tasks
- Update test dependencies
- Review test coverage reports
- Refactor outdated tests
- Add tests for new features

### Test Database Management
```bash
# Reset test database
python manage.py flush --settings=Acta_backend.settings.test

# Create test migrations
python manage.py makemigrations --settings=Acta_backend.settings.test
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [DRF Testing Guide](https://www.django-rest-framework.org/api-guide/testing/)

---

**Happy Testing! 🚀**

For questions or issues, please refer to the project documentation or create an issue in the repository.