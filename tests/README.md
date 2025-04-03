# Testing Strategy

## 🎯 Testing Priorities

### 🔥 High Priority

Core functionality that must be tested:

- Strain analysis algorithms (point normalization, tensor calculations)
- Data processing (regression analysis, data transformations)
- Data export/import operations

### ⚪ Low Priority

UI and visual elements that we intentionally skip:

- Main Streamlit app flow
- Basic UI layout and styling
- Visual elements (manual testing preferred)

## 📚 Current Test Files

### 🔬 `test_strain_analysis_core.py`

Tests core strain analysis algorithms in `strain_analysis_core.py`:

- Point normalization and scaling: Ensures accurate spatial measurements
- Strain tensor calculations: Validates deformation analysis
- Edge cases: Handles invalid inputs and boundary conditions

### 📊 `test_strain_analysis_data.py`

Tests data processing and visualization in `strain_analysis_data.py`:

- Scientific formatting: Ensures consistent number representation
- Regression analysis: Validates strain trend calculations
- Data export: Verifies correct data serialization
- Plot creation: Confirms visualization data integrity

## 🛠️ Running Tests

```shell
pytest  # Run all tests

pytest --cov  # Run with coverage
```

## 📝 Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Clear Test Names**: Use descriptive names that explain the expected behavior
3. **DRY Principle**: Use fixtures and helper functions to avoid code duplication
4. **KISS Principle**: Keep tests simple and focused on one aspect
5. **Meaningful Assertions**: Test behavior, not implementation details
6. **Edge Cases**: Include tests for boundary conditions and error cases

## 🔄 Adding New Tests

When adding new tests:

1. Follow the existing test structure
2. Use appropriate fixtures for common test data
3. Include both positive and negative test cases
4. Document any special considerations or assumptions
5. Ensure tests are maintainable and readable
