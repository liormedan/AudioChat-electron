# AI Chat System Testing Suite
# חבילת בדיקות למערכת שיחות AI

This directory contains comprehensive tests for the AI Chat System, including unit tests, integration tests, E2E tests, and performance tests.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
├── integration/             # Integration tests for full workflows
├── e2e/                     # End-to-end tests with Playwright
├── performance/             # Performance and load testing
├── api/                     # API endpoint tests
├── fixtures/                # Test fixtures and data
└── README.md               # This file
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)

Unit tests verify individual components in isolation:

- **Chat Models**: Test data models and validation
- **Chat Service**: Test business logic and message handling
- **Session Service**: Test session management
- **History Service**: Test message storage and retrieval
- **Security Service**: Test encryption and authentication

**Running Unit Tests:**
```bash
cd tests/unit
python -m pytest -v
```

### 2. Integration Tests (`tests/integration/`)

Integration tests verify complete workflows across multiple components:

- **Full Chat Flow**: Create session → Send messages → Get history
- **Streaming**: Test real-time message streaming
- **Session Management**: CRUD operations on sessions
- **Search and Export**: Message search and data export
- **Error Handling**: Error scenarios and recovery
- **Concurrent Operations**: Multi-user scenarios
- **Data Consistency**: Database integrity checks

**Running Integration Tests:**
```bash
cd tests/integration
python -m pytest test_chat_integration.py -v
```

### 3. End-to-End Tests (`tests/e2e/`)

E2E tests verify the complete user experience using Playwright:

- **Chat Interface**: UI interactions and workflows
- **Accessibility**: WCAG compliance and screen reader support
- **Performance**: Frontend performance metrics
- **Responsive Design**: Multi-device compatibility
- **Error Handling**: User-facing error scenarios

**Setup E2E Tests:**
```bash
# Install Playwright
npm install -g playwright
playwright install

# Install Python dependencies
pip install playwright axe-playwright

# Run E2E tests
cd tests/e2e
playwright test
```

**E2E Test Configuration:**
- `playwright.config.ts`: Main configuration
- `global-setup.ts`: Test environment setup
- `global-teardown.ts`: Cleanup after tests

### 4. Performance Tests (`tests/performance/`)

Performance tests evaluate system performance under various loads:

- **Load Testing**: Normal usage patterns
- **Stress Testing**: Maximum capacity testing
- **Memory Testing**: Memory usage and leak detection
- **Database Performance**: Query and insert performance
- **Concurrent Users**: Multi-user performance

**Running Performance Tests:**
```bash
cd tests/performance

# Quick performance test
python run_performance_tests.py --quick

# Full performance suite
python run_performance_tests.py --full

# Custom test
python run_performance_tests.py --custom --users 20 --requests 15 --type streaming

# Database performance
python run_performance_tests.py --database
```

## Test Configuration

### Environment Variables

Set these environment variables to configure tests:

```bash
# Backend configuration
export BACKEND_URL="http://127.0.0.1:5000"
export FRONTEND_URL="http://localhost:5174"

# Performance test configuration
export PERF_MAX_USERS=50
export PERF_MAX_REQUESTS=50
export PERF_TIMEOUT=30
export PERF_MAX_RESPONSE_TIME=2000
export PERF_MIN_SUCCESS_RATE=95

# Test database
export TEST_DB_PATH="test_chat.db"
```

### Test Data

Test fixtures and data are located in `tests/fixtures/`:
- Sample sessions and messages
- Mock user data
- Test configuration files

## Running All Tests

### Prerequisites

1. **Backend Server**: Ensure the backend is running
   ```bash
   cd backend
   python main.py
   ```

2. **Frontend Server** (for E2E tests):
   ```bash
   cd frontend/electron-app
   npm run dev:vite
   ```

3. **Dependencies**: Install test dependencies
   ```bash
   pip install -r tests/performance/requirements.txt
   ```

### Test Execution

**Run all test categories:**
```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# E2E tests
cd tests/e2e && playwright test

# Performance tests
cd tests/performance && python run_performance_tests.py --full
```

**Run specific test files:**
```bash
# Specific unit test
python -m pytest tests/unit/test_chat_service.py -v

# Specific integration test
python -m pytest tests/integration/test_chat_integration.py::TestChatIntegrationFlow::test_complete_chat_session_flow -v

# Specific E2E test
cd tests/e2e && playwright test chat-flow.spec.ts
```

## Test Reports

### Unit and Integration Tests
- Console output with pass/fail status
- Coverage reports (if coverage.py is configured)
- JUnit XML reports for CI/CD integration

### E2E Tests
- HTML report: `tests/e2e/playwright-report/index.html`
- Screenshots and videos of failures
- Trace files for debugging

### Performance Tests
- JSON metrics: `performance_results.json`
- HTML report: `chat_performance_report.html`
- CSV data: `performance_results.csv`
- Summary: `performance_summary.txt`

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tests/performance/requirements.txt
    
    - name: Run unit tests
      run: python -m pytest tests/unit/ -v
    
    - name: Run integration tests
      run: python -m pytest tests/integration/ -v
    
    - name: Install Playwright
      run: |
        npm install -g playwright
        playwright install
    
    - name: Run E2E tests
      run: cd tests/e2e && playwright test
    
    - name: Run performance tests
      run: cd tests/performance && python run_performance_tests.py --quick
```

## Test Development Guidelines

### Writing Unit Tests

1. **Test Structure**: Use AAA pattern (Arrange, Act, Assert)
2. **Mocking**: Mock external dependencies
3. **Coverage**: Aim for >90% code coverage
4. **Naming**: Use descriptive test names

```python
def test_send_message_success(self, chat_service, mock_session_service):
    # Arrange
    session_id = "test-session"
    message = "Hello"
    
    # Act
    result = chat_service.send_message(session_id, message)
    
    # Assert
    assert result.success is True
    assert result.content == "Test response"
```

### Writing Integration Tests

1. **Real Components**: Use actual services, not mocks
2. **Test Database**: Use temporary test database
3. **Cleanup**: Clean up test data after each test
4. **End-to-End Flows**: Test complete user workflows

### Writing E2E Tests

1. **Page Objects**: Use page object pattern for UI elements
2. **Selectors**: Use data-testid attributes for reliable selectors
3. **Waits**: Use explicit waits for dynamic content
4. **Accessibility**: Include accessibility checks

### Writing Performance Tests

1. **Realistic Load**: Use realistic user patterns
2. **Metrics**: Collect comprehensive performance metrics
3. **Thresholds**: Define clear performance thresholds
4. **Reporting**: Generate detailed performance reports

## Troubleshooting

### Common Issues

1. **Backend Not Running**
   ```
   Error: Connection refused
   Solution: Start the backend server
   ```

2. **Database Locked**
   ```
   Error: Database is locked
   Solution: Close other connections or use different test DB
   ```

3. **Playwright Installation**
   ```
   Error: Browser not found
   Solution: Run 'playwright install'
   ```

4. **Port Conflicts**
   ```
   Error: Port already in use
   Solution: Change port in configuration or stop conflicting service
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Unit/Integration tests
python -m pytest tests/ -v -s --log-cli-level=DEBUG

# E2E tests
cd tests/e2e && DEBUG=pw:api playwright test

# Performance tests
cd tests/performance && python run_performance_tests.py --full --debug
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add appropriate documentation
3. Update this README if needed
4. Ensure tests pass in CI/CD pipeline
5. Include both positive and negative test cases

## Performance Benchmarks

### Target Performance Metrics

- **Response Time**: < 500ms average, < 2000ms 95th percentile
- **Success Rate**: > 99% for normal load, > 95% for stress tests
- **Throughput**: > 50 requests/second for normal load
- **Memory Usage**: < 500MB for typical workload
- **Database Queries**: < 100ms average query time

### Performance Test Scenarios

1. **Light Load**: 5 users, 10 requests each
2. **Normal Load**: 15 users, 20 requests each
3. **Heavy Load**: 30 users, 15 requests each
4. **Stress Test**: 50 users, 10 requests each
5. **Streaming Test**: 10 users, streaming responses
6. **Mixed Operations**: Various API operations

## Security Testing

Security considerations in tests:

1. **Input Sanitization**: Test XSS and injection prevention
2. **Authentication**: Test access controls
3. **Rate Limiting**: Test abuse prevention
4. **Data Encryption**: Test sensitive data protection
5. **Session Security**: Test session management

## Accessibility Testing

Accessibility checks include:

1. **Keyboard Navigation**: Tab order and shortcuts
2. **Screen Readers**: ARIA labels and roles
3. **Color Contrast**: WCAG compliance
4. **Focus Management**: Proper focus handling
5. **Error Messages**: Clear error communication

---

For more information, see the individual test directories and their documentation.