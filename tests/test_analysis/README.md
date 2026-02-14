# VST Audio Analysis Test Suite

This test suite provides comprehensive unit testing for the VST audio analysis system components.

## Test Coverage

### Core Components Tested

1. **Parameter Polling System** (`test_parameter_polling.py`)
   - ParameterPoller class initialization
   - TCP connection management
   - Parameter retrieval and caching
   - Error handling and timeout recovery
   - CSV logging functionality
   - Performance tracking

2. **Rules Parser** (`test_rules_parser.py`)
   - YAML rule file parsing
   - Condition parsing (comparison and logical operators)
   - Action parsing and validation
   - Rule priority sorting
   - Error handling for malformed files

3. **Rules Engine** (`test_rules_engine.py`)
   - Rule evaluation logic for all operators
   - Action execution via MCP server
   - Cooldown management
   - Parameter value resolution
   - Error handling and recovery

4. **Integration Tests** (`test_integration.py`)
   - End-to-end workflow testing
   - Mock MCP server interactions
   - Error scenario handling
   - Component integration testing
   - Responsive controller testing

## Test Features

### Mock Infrastructure
- `MockMCPServer`: Simulates Ableton MCP server with TCP and UDP protocols
- Command logging and verification
- Configurable responses for testing

### Test Coverage Target: >80%
- Comprehensive parameter combinations
- Error conditions and edge cases
- Integration scenarios
- Performance and reliability testing

## Running Tests

```bash
# Run all tests
python -m pytest tests/test_analysis/ -v

# Run with coverage
python -m coverage run --source=../../scripts/analysis -m pytest tests/test_analysis/ --cov-report=html

# Run individual test modules
python -m pytest tests/test_analysis/test_parameter_polling.py -v
python -m pytest tests/test_analysis/test_rules_parser.py -v
python -m pytest tests/test_analysis/test_rules_engine.py -v
python -m pytest tests/test_analysis/test_integration.py -v
```

## Test Quality

- **TDD Compliance**: All tests follow red-green-refactor methodology
- **Mocking Strategy**: Proper isolation of external dependencies
- **Error Coverage**: Comprehensive error condition testing
- **Integration**: Real-world scenario simulation
- **Documentation**: Clear test names and comprehensive docstrings